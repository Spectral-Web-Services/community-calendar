#!/usr/bin/env python3
"""
Scraper for Chicago Botanic Garden calendar.

The calendar is a Drupal site with paginated event listings at
/calendar?page=N. Each event card has a title, date/time in the
subtitle, and a link to a detail page. The URL query parameter
range_start=YYYY-MM-DD provides the year context.

Usage:
    python scrapers/chicagobotanic.py --output cities/evanston/chicago_botanic.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import logging
import re
from datetime import datetime, date
from typing import Any
from urllib.parse import urljoin, parse_qs, urlparse
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup

from lib.base import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.chicagobotanic.org"
CALENDAR_URL = f"{BASE_URL}/calendar"


class ChicagoBotanicScraper(BaseScraper):
    name = "Chicago Botanic Garden"
    domain = "chicagobotanic.org"
    timezone = "America/Chicago"

    def fetch_events(self) -> list[dict[str, Any]]:
        events = []
        seen_urls = set()

        for page in range(20):  # safety limit
            url = f"{CALENDAR_URL}?page={page}" if page > 0 else CALENDAR_URL
            logger.info("Fetching page %d: %s", page, url)

            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            try:
                with urlopen(req, timeout=30) as resp:
                    html = resp.read().decode()
            except Exception as e:
                logger.error("Failed to fetch page %d: %s", page, e)
                break

            soup = BeautifulSoup(html, 'html.parser')
            cards = soup.select('article.card--calendar')

            if not cards:
                logger.info("No more events on page %d, stopping", page)
                break

            for card in cards:
                event = self._parse_card(card)
                if event and event.get('url') not in seen_urls:
                    events.append(event)
                    if event.get('url'):
                        seen_urls.add(event['url'])

            # Pagination is JS-rendered, so just keep going until no cards
            if len(cards) < 10:
                break

        logger.info("Found %d events total", len(events))
        return events

    def _parse_card(self, card) -> dict[str, Any] | None:
        heading = card.select_one('h2.card__heading')
        if not heading:
            return None

        a = heading.find('a')
        title = a.get_text(strip=True) if a else heading.get_text(strip=True)
        if not title:
            return None

        href = a['href'] if a and a.get('href') else ''
        event_url = urljoin(BASE_URL, href) if href else None

        # Extract year from range_start parameter if present
        year = None
        if href:
            qs = parse_qs(urlparse(href).query)
            if 'range_start' in qs:
                try:
                    year = int(qs['range_start'][0][:4])
                except (ValueError, IndexError):
                    pass

        # Get date/time from subtitle
        subtitle = card.select_one('.card__subtitle')
        body = card.select_one('.card__body')

        date_text = ''
        if subtitle:
            date_text = subtitle.get_text(' ', strip=True)
        if not date_text and body:
            date_text = body.get_text(' ', strip=True)

        dtstart = self._parse_date(date_text, year)
        if not dtstart:
            return None

        dtend = self._parse_end_time(date_text, dtstart)

        # Get image
        img = card.select_one('img')
        image_url = None
        if img and img.get('src'):
            image_url = urljoin(BASE_URL, img['src'])

        # Get description from body (price info or short desc)
        description = None
        if body and subtitle:
            # If subtitle had the date, body has price/description
            body_text = body.get_text(strip=True)
            # Skip if it's just a price
            if not re.match(r'^\$[\d,/]+$', body_text):
                description = body_text[:500]

        event = {
            'title': title,
            'dtstart': dtstart,
            'url': event_url,
        }
        if dtend:
            event['dtend'] = dtend
        if description:
            event['description'] = description
        if image_url:
            event['image_url'] = image_url
        event['location'] = 'Chicago Botanic Garden, 1000 Lake Cook Rd, Glencoe, IL 60022'

        return event

    def _parse_date(self, text: str, year: int | None = None) -> datetime | None:
        if not text:
            return None

        if not year:
            year = datetime.now().year

        # Pattern: "Wednesday, March 11" or "Saturday, March 14"
        m = re.search(r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+'
                      r'(January|February|March|April|May|June|July|August|'
                      r'September|October|November|December)\s+(\d{1,2})', text)
        if m:
            month_str, day_str = m.group(1), m.group(2)
            # Parse time: "10 – 11 a.m." or "6:30 – 7:45 p.m." or "9 a.m. – noon"
            time = self._parse_start_time(text)
            try:
                dt_str = f"{month_str} {day_str}, {year}"
                if time:
                    return datetime.strptime(f"{dt_str} {time}", "%B %d, %Y %I:%M %p")
                else:
                    return datetime.strptime(dt_str, "%B %d, %Y")
            except ValueError:
                return None

        # Pattern: "February 7 – March 22, 2026" (date range, use start)
        m = re.search(r'(January|February|March|April|May|June|July|August|'
                      r'September|October|November|December)\s+(\d{1,2})\s*[–—-]', text)
        if m:
            month_str, day_str = m.group(1), m.group(2)
            # Look for explicit year
            y_match = re.search(r',?\s*(20\d{2})', text)
            if y_match:
                year = int(y_match.group(1))
            try:
                dt_str = f"{month_str} {day_str}, {year}"
                return datetime.strptime(dt_str, "%B %d, %Y")
            except ValueError:
                return None

        # Pattern: "Mar. 12 & 19" — abbreviated month
        m = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(\d{1,2})', text)
        if m:
            month_str, day_str = m.group(1), m.group(2)
            try:
                dt_str = f"{month_str} {day_str}, {year}"
                return datetime.strptime(dt_str, "%b %d, %Y")
            except ValueError:
                return None

        return None

    def _parse_start_time(self, text: str) -> str | None:
        """Extract start time from text like '6:30 – 7:45 p.m.' or '10 – 11 a.m.'"""
        # Try range first: "6:30 – 7:45 p.m." or "10 – 11 a.m." or "9 a.m. – 3:30 p.m."
        # With am/pm on start: "9 a.m. – 3:30 p.m."
        m = re.search(r'(\d{1,2}(?::\d{2})?)\s*(a\.m\.|p\.m\.)\s*[–—-]', text)
        if m:
            time_str = m.group(1)
            am_pm = 'AM' if 'a.m.' in m.group(2) else 'PM'
            if ':' not in time_str:
                time_str += ':00'
            return f"{time_str} {am_pm}"

        # Without am/pm on start, inherits from end: "6:30 – 7:45 p.m."
        m = re.search(r'(\d{1,2}(?::\d{2})?)\s*[–—-]\s*\d{1,2}(?::\d{2})?\s*(a\.m\.|p\.m\.)', text)
        if m:
            time_str = m.group(1)
            am_pm = 'AM' if 'a.m.' in m.group(2) else 'PM'
            if ':' not in time_str:
                time_str += ':00'
            return f"{time_str} {am_pm}"

        # Standalone time: "10 a.m." (no range)
        m = re.search(r'(\d{1,2}(?::\d{2})?)\s*(a\.m\.|p\.m\.)', text)
        if m:
            time_str = m.group(1)
            am_pm = 'AM' if 'a.m.' in m.group(2) else 'PM'
            if ':' not in time_str:
                time_str += ':00'
            return f"{time_str} {am_pm}"

        return None

    def _parse_end_time(self, text: str, dtstart: datetime) -> datetime | None:
        """Extract end time and combine with dtstart's date."""
        # "6:30 – 7:45 p.m." or "10 – 11 a.m." or "9 a.m. – 3:30 p.m."
        m = re.search(r'[–—-]\s*(\d{1,2}(?::\d{2})?)\s*(a\.m\.|p\.m\.)', text)
        if m:
            time_str = m.group(1)
            am_pm = 'AM' if 'a.m.' in m.group(2) else 'PM'
            if ':' not in time_str:
                time_str += ':00'
            try:
                end_time = datetime.strptime(f"{time_str} {am_pm}", "%I:%M %p")
                return dtstart.replace(hour=end_time.hour, minute=end_time.minute)
            except ValueError:
                pass

        # "noon"
        if re.search(r'[–—-]\s*noon', text, re.IGNORECASE):
            return dtstart.replace(hour=12, minute=0)

        return None


if __name__ == "__main__":
    ChicagoBotanicScraper.setup_logging()
    args = ChicagoBotanicScraper.parse_args(
        description="Scrape events from Chicago Botanic Garden calendar"
    )
    scraper = ChicagoBotanicScraper()
    scraper.run(output=args.output)
