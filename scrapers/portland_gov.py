#!/usr/bin/env python3
"""
Scraper for Portland.gov events.

Fetches events from the city's Drupal event listing pages, paginating through
results. Can filter by event type (category) to produce per-category ICS feeds.

Usage:
    # All community events
    python scrapers/portland_gov.py --type 329 --name "Portland Community Events" -o community.ics

    # Volunteer events
    python scrapers/portland_gov.py --type 364 --name "Portland Volunteer Events" -o volunteer.ics

    # All event types
    python scrapers/portland_gov.py --name "Portland City Events" -o all_events.ics

Type IDs:
    329 = Community event
    364 = Volunteer event
    583 = Classes and activities
    332 = Meeting
    333 = Public meeting
    330 = Public hearing
    651 = Council meeting
    626 = Neighborhood association meeting
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import argparse
import logging
import re
from datetime import datetime, date
from typing import Any, Optional
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

from lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://www.portland.gov/events"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}
TZ = ZoneInfo("America/Los_Angeles")


class PortlandGovScraper(BaseScraper):
    """Scraper for Portland.gov city events."""

    name = "Portland City Events"
    domain = "portland.gov"
    timezone = "America/Los_Angeles"

    def __init__(self, type_id: Optional[str] = None, source_name: Optional[str] = None):
        self.type_id = type_id
        if source_name:
            self.name = source_name
        super().__init__()

    def _build_url(self, page: int) -> str:
        """Build listing page URL with optional type filter."""
        params = {"page": str(page)}
        if self.type_id:
            params["f[0]"] = f"type:{self.type_id}"
        return f"{BASE_URL}?{urlencode(params)}"

    def _parse_listing_page(self, html: str) -> list[dict[str, Any]]:
        """Parse event cards from a listing page."""
        soup = BeautifulSoup(html, "html.parser")
        events = []

        # Each event card is in a div.row with an h2 containing the link
        for card in soup.select("h2.h4"):
            link = card.find("a", href=re.compile(r"/events/\d{4}/"))
            if not link:
                continue

            href = link.get("href", "")
            title_span = link.find("span", class_=re.compile("field--name-title"))
            title = title_span.get_text(strip=True) if title_span else link.get_text(strip=True)

            # Get the parent container for more context
            container = card.find_parent("div", class_="row")
            if not container:
                container = card.parent

            # Description - next sibling <p>
            desc = ""
            p_tag = card.find_next_sibling("p")
            if not p_tag and container:
                p_tag = container.find("p")
            if p_tag:
                desc = p_tag.get_text(strip=True)[:500]

            # Dates - find <time> elements in the card area
            time_elements = container.find_all("time") if container else []
            dtstart = None
            dtend = None

            for i, t in enumerate(time_elements):
                dt_str = t.get("datetime", "")
                if dt_str:
                    try:
                        dt = datetime.strptime(dt_str, "%Y-%m-%d").replace(tzinfo=TZ)
                        if i == 0:
                            dtstart = dt
                        elif i == 1:
                            dtend = dt
                    except ValueError:
                        pass

            # Try to extract time-of-day from surrounding text
            if container and dtstart:
                text = container.get_text()
                time_match = re.search(r'(\d{1,2}:\d{2})\s*(am|pm|a\.m\.|p\.m\.)', text, re.IGNORECASE)
                if time_match:
                    hour_min = time_match.group(1)
                    ampm = time_match.group(2).replace('.', '').lower()
                    try:
                        time_obj = datetime.strptime(f"{hour_min} {ampm}", "%I:%M %p")
                        dtstart = dtstart.replace(hour=time_obj.hour, minute=time_obj.minute)
                    except ValueError:
                        pass

            # Category badge
            badge = container.find("div", class_="badge") if container else None
            category = badge.get_text(strip=True) if badge else ""

            if not dtstart:
                continue

            # Skip past events
            now = datetime.now(TZ)
            if dtstart < now and (not dtend or dtend < now):
                continue

            events.append({
                "title": title,
                "dtstart": dtstart,
                "dtend": dtend,
                "description": desc,
                "url": f"https://www.portland.gov{href}" if href.startswith("/") else href,
                "category": category,
            })

        return events

    def _enrich_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Fetch event detail page for location and image."""
        url = event.get("url", "")
        if not url:
            return event

        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                return event

            soup = BeautifulSoup(resp.text, "html.parser")

            # Location
            loc_field = soup.find(class_=re.compile("field--name-field-location"))
            if loc_field:
                loc_text = loc_field.get_text(" ", strip=True)
                # Clean up "Location VenueName Label: Category"
                loc_text = re.sub(r'\s*Label:.*$', '', loc_text)
                loc_text = re.sub(r'^Location\s+', '', loc_text)
                if loc_text:
                    event["location"] = loc_text

            # Image (og:image meta tag)
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                event["image_url"] = og_image["content"]

        except Exception as e:
            self.logger.debug(f"Failed to enrich {url}: {e}")

        return event

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch all events from listing pages with pagination."""
        all_events = []
        page = 0

        while True:
            url = self._build_url(page)
            self.logger.info(f"Fetching page {page}: {url}")

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
                break

            all_events.extend(events)
            self.logger.info(f"  Got {len(events)} events (total: {len(all_events)})")

            # Check for next page
            if f"page={page + 1}" not in resp.text:
                break

            page += 1

            # Safety limit
            if page > 50:
                break

        # Enrich top events with location and images (limit to avoid hammering)
        self.logger.info(f"Enriching up to {min(len(all_events), 200)} events with detail pages...")
        for i, event in enumerate(all_events[:200]):
            event = self._enrich_event(event)
            all_events[i] = event

        return all_events


def main():
    parser = argparse.ArgumentParser(description="Scrape Portland.gov events")
    parser.add_argument('--type', dest='type_id', help='Event type ID (e.g., 329=Community, 364=Volunteer)')
    parser.add_argument('--name', default='Portland City Events', help='Source name')
    parser.add_argument('--output', '-o', help='Output ICS file')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    scraper = PortlandGovScraper(type_id=args.type_id, source_name=args.name)
    scraper.run(args.output)


if __name__ == '__main__':
    main()
