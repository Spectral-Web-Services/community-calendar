#!/usr/bin/env python3
"""
Scraper for Oregon Zoo events.

Fetches events from https://www.oregonzoo.org/events. The site is Drupal-based
with a "Burnham" theme. Events are sparse (1-3 at a time) with simple card
markup on the listing page. Detail pages provide additional description and images.

Event links may be at /events/<slug> or short paths like /hop, /brew, /lights.

Usage:
    python scrapers/oregon_zoo.py -o oregon_zoo.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import logging
import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

from lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://www.oregonzoo.org"
EVENTS_URL = f"{BASE_URL}/events"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}
TZ = ZoneInfo("America/Los_Angeles")


def parse_date_time(text: str) -> tuple[datetime | None, datetime | None]:
    """
    Parse date and time from text like "April 4, 9 a.m. to 5 p.m." or
    "March 15, 6 to 9 p.m." or "December 5 - January 3".

    Returns (dtstart, dtend) as timezone-aware datetimes, or (None, None).
    """
    if not text:
        return None, None

    text = text.strip()

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Skip entries like "Daily" or "Weekends" which aren't specific dates
    if re.match(r'^(Daily|Weekends|Every)\b', text, re.IGNORECASE):
        return None, None

    # Try to extract a date portion: "Month Day" with optional year
    # Handles: "April 4", "April 4, 2026", "December 5 - January 3"
    month_re = (r'(?:January|February|March|April|May|June|July|August|'
                r'September|October|November|December)')

    # Pattern: "Month Day" with optional year
    date_match = re.search(
        rf'({month_re})\s+(\d{{1,2}})(?:,?\s+(\d{{4}}))?', text
    )
    if not date_match:
        return None, None

    month_str = date_match.group(1)
    day = int(date_match.group(2))
    year = int(date_match.group(3)) if date_match.group(3) else None

    # If no year, guess based on current date
    if year is None:
        now = datetime.now(TZ)
        # Try current year first; if the date is more than 2 months ago, use next year
        try:
            candidate = datetime.strptime(f"{month_str} {day}", "%B %d").replace(
                year=now.year, tzinfo=TZ
            )
        except ValueError:
            return None, None
        if candidate.month < now.month - 2:
            candidate = candidate.replace(year=now.year + 1)
        year = candidate.year

    try:
        dtstart = datetime.strptime(f"{month_str} {day} {year}", "%B %d %Y").replace(
            tzinfo=TZ
        )
    except ValueError:
        return None, None

    dtend = None

    # Extract time: "9 a.m. to 5 p.m." or "6 to 9 p.m." or "7 p.m."
    # Normalize a.m./p.m. to am/pm
    time_text = re.sub(r'a\.m\.', 'am', text)
    time_text = re.sub(r'p\.m\.', 'pm', time_text)

    # Pattern: "H:MM am/pm to H:MM am/pm" or "H am/pm to H pm" etc.
    time_range = re.search(
        r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*(?:to|-|–)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)',
        time_text, re.IGNORECASE
    )
    if time_range:
        start_h = int(time_range.group(1))
        start_m = int(time_range.group(2) or 0)
        start_ampm = time_range.group(3)
        end_h = int(time_range.group(4))
        end_m = int(time_range.group(5) or 0)
        end_ampm = time_range.group(6)

        # If start has no am/pm, infer from end
        if not start_ampm:
            # "6 to 9 pm" -> start is 6 pm if start < end, else 6 am
            if start_h <= end_h:
                start_ampm = end_ampm
            else:
                start_ampm = 'am' if end_ampm.lower() == 'pm' else 'pm'

        try:
            start_time = datetime.strptime(f"{start_h}:{start_m:02d} {start_ampm}", "%I:%M %p")
            end_time = datetime.strptime(f"{end_h}:{end_m:02d} {end_ampm}", "%I:%M %p")
            dtstart = dtstart.replace(hour=start_time.hour, minute=start_time.minute)
            dtend = dtstart.replace(hour=end_time.hour, minute=end_time.minute)
        except ValueError:
            pass
    else:
        # Single time: "7 p.m." or "10 am"
        single_time = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', time_text, re.IGNORECASE)
        if single_time:
            h = int(single_time.group(1))
            m = int(single_time.group(2) or 0)
            ampm = single_time.group(3)
            try:
                t = datetime.strptime(f"{h}:{m:02d} {ampm}", "%I:%M %p")
                dtstart = dtstart.replace(hour=t.hour, minute=t.minute)
            except ValueError:
                pass

    return dtstart, dtend


class OregonZooScraper(BaseScraper):
    """Scraper for Oregon Zoo events."""

    name = "Oregon Zoo"
    domain = "oregonzoo.org"
    timezone = "America/Los_Angeles"

    def _parse_listing_page(self, html: str) -> list[dict[str, Any]]:
        """Parse event cards from the listing page.

        Actual card structure (Drupal Burnham theme):
            <a class="card-dynamic" href="/hop">
              <div class="card-dynamic__media reveal-image">
                <figure class="media__image">
                  <img class="image" src="/sites/default/files/styles/4x3_fallback/public/..." alt="..."/>
                </figure>
              </div>
              <div class="card-dynamic__content">
                <h3 class="card-dynamic__title h3">
                  <span>Hop into Spring</span>
                </h3>
                <span class="card-dynamic__sub-title h3">
                  <span><span>April 4, 9 a.m. to 5 p.m.</span></span>
                </span>
                <div class="wysiwyg">
                  <p>Celebrate spring with special fun family activities...</p>
                </div>
              </div>
            </a>
        """
        soup = BeautifulSoup(html, "html.parser")
        events = []

        # Find all event card links with class "card-dynamic"
        for link in soup.find_all("a", class_="card-dynamic", href=True):
            href = link["href"]

            # Title from h3.card-dynamic__title
            h3 = link.find("h3", class_=re.compile(r"card-dynamic__title"))
            if not h3:
                continue
            title = h3.get_text(strip=True)
            if not title:
                continue

            # Build full URL
            if href.startswith("/"):
                url = f"{BASE_URL}{href}"
            elif href.startswith("http"):
                url = href
            else:
                continue

            # Date/time from span.card-dynamic__sub-title
            date_text = ""
            subtitle = link.find("span", class_=re.compile(r"card-dynamic__sub-title"))
            if subtitle:
                date_text = subtitle.get_text(strip=True)

            # Description from div.wysiwyg
            description = ""
            wysiwyg = link.find("div", class_="wysiwyg")
            if wysiwyg:
                description = wysiwyg.get_text(strip=True)

            # Parse date/time from the first paragraph
            dtstart, dtend = parse_date_time(date_text)
            if not dtstart:
                logger.debug(f"Could not parse date from '{date_text}' for '{title}', skipping")
                continue

            # Skip past events
            now = datetime.now(TZ)
            if dtstart < now and (not dtend or dtend < now):
                continue

            # Image from the card
            img = link.find("img")
            image_url = None
            if img and img.get("src"):
                src = img["src"]
                if src.startswith("/"):
                    image_url = f"{BASE_URL}{src}"
                elif src.startswith("http"):
                    image_url = src
                # Strip query params for cleaner URL (optional)
                if image_url and "?" in image_url:
                    image_url = image_url.split("?")[0]

            events.append({
                "title": title,
                "dtstart": dtstart,
                "dtend": dtend,
                "description": description,
                "url": url,
                "image_url": image_url,
                "location": "Oregon Zoo, 4001 SW Canyon Road, Portland, OR 97221",
            })

        return events

    def _enrich_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Fetch event detail page for richer description and image."""
        url = event.get("url", "")
        if not url:
            return event

        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                logger.debug(f"HTTP {resp.status_code} for detail page {url}")
                return event

            soup = BeautifulSoup(resp.text, "html.parser")

            # Try og:image meta tag
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                img_url = og_image["content"]
                if img_url.startswith("/"):
                    img_url = f"{BASE_URL}{img_url}"
                event["image_url"] = img_url

            # Try og:description for a richer description
            og_desc = soup.find("meta", property="og:description")
            if og_desc and og_desc.get("content"):
                desc = og_desc["content"].strip()
                if len(desc) > len(event.get("description", "")):
                    event["description"] = desc

            # Look for body/description text in the main content area
            # Drupal typically uses field--name-body or similar
            body_field = soup.find(class_=re.compile(r"field--name-body"))
            if body_field:
                body_text = body_field.get_text(" ", strip=True)[:500]
                if len(body_text) > len(event.get("description", "")):
                    event["description"] = body_text

            # Try to extract more precise date/time from detail page
            # Look for "Date:" and "Time:" labels
            page_text = soup.get_text()
            date_match = re.search(r'Date:\s*(.+?)(?:\n|Time:)', page_text)
            time_match = re.search(r'Time:\s*(.+?)(?:\n|$)', page_text)
            if date_match and time_match:
                combined = f"{date_match.group(1).strip()}, {time_match.group(1).strip()}"
                dtstart, dtend = parse_date_time(combined)
                if dtstart:
                    event["dtstart"] = dtstart
                    if dtend:
                        event["dtend"] = dtend

        except Exception as e:
            logger.debug(f"Failed to enrich {url}: {e}")

        return event

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch all events from the listing page and enrich from detail pages."""
        all_events = []

        # The zoo typically has very few events; check page 0 and page 1
        for page in range(3):  # safety limit
            url = f"{EVENTS_URL}?page={page}" if page > 0 else EVENTS_URL
            self.logger.info(f"Fetching listing page {page}: {url}")

            try:
                resp = requests.get(url, headers=HEADERS, timeout=30)
                if resp.status_code != 200:
                    self.logger.warning(f"HTTP {resp.status_code} for page {page}")
                    break
            except Exception as e:
                self.logger.warning(f"Failed to fetch page {page}: {e}")
                break

            events = self._parse_listing_page(resp.text)
            if not events:
                self.logger.info(f"  No events on page {page}, stopping pagination")
                break

            all_events.extend(events)
            self.logger.info(f"  Got {len(events)} events (total: {len(all_events)})")

            # Check for next page link
            if f"page={page + 1}" not in resp.text:
                break

        # Enrich all events from detail pages (few events, so this is fine)
        self.logger.info(f"Enriching {len(all_events)} events from detail pages...")
        for i, event in enumerate(all_events):
            all_events[i] = self._enrich_event(event)

        return all_events


def main():
    OregonZooScraper.main()


if __name__ == '__main__':
    main()
