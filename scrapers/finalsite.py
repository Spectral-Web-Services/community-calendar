#!/usr/bin/env python3
"""
Scraper for Finalsite school/organization calendars.

Finalsite renders calendar events server-side in a monthly view.
Events have datetime attributes on <time> elements and detail page URLs.

Usage:
    python scrapers/finalsite.py \
        --url "https://www.district65.net/about/calendar" \
        --name "District 65" \
        --output cities/evanston/district65.ics

    python scrapers/finalsite.py \
        --url "https://www.eths202.org/calendar" \
        --name "ETHS District 202" \
        --output cities/evanston/eths202.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import argparse
import logging
import re
from datetime import datetime
from typing import Any
from urllib.parse import urljoin
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup

from lib.base import BaseScraper

logger = logging.getLogger(__name__)


class FinalsiteScraper(BaseScraper):
    name = "Finalsite Calendar"
    domain = "finalsite.net"
    timezone = "America/Chicago"

    def __init__(self, url: str, source_name: str | None = None):
        super().__init__()
        self.url = url
        if source_name:
            self.name = source_name
            # Use the domain from the URL
            from urllib.parse import urlparse
            self.domain = urlparse(url).netloc

    def fetch_events(self) -> list[dict[str, Any]]:
        req = Request(self.url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as resp:
            html = resp.read().decode()

        soup = BeautifulSoup(html, 'html.parser')
        events = []
        seen = set()

        current_date_text = None

        for cell in soup.select('.fsCalendarDaybox'):
            date_el = cell.select_one('.fsCalendarDate')
            if date_el:
                current_date_text = date_el.get_text(strip=True)

            for info in cell.select('.fsCalendarInfo'):
                event = self._parse_event(info, current_date_text)
                if event:
                    key = (event['title'], str(event['dtstart']))
                    if key not in seen:
                        seen.add(key)
                        events.append(event)

        logger.info("Found %d events from %s", len(events), self.url)
        return events

    def _parse_event(self, info, date_text: str | None) -> dict[str, Any] | None:
        title_el = info.select_one('.fsCalendarEventTitle')
        if not title_el:
            return None

        title = title_el.get_text(strip=True)
        if not title:
            return None

        # Get URL
        a = title_el if title_el.name == 'a' else title_el.find('a')
        event_url = None
        if a and a.get('href'):
            event_url = urljoin(self.url, a['href'])

        # Get datetime from <time> element
        dtstart = None
        dtend = None

        start_time = info.select_one('time.fsStartTime')
        if start_time and start_time.get('datetime'):
            try:
                dtstart = datetime.fromisoformat(start_time['datetime'])
            except ValueError:
                pass

        end_time = info.select_one('time.fsEndTime')
        if end_time and end_time.get('datetime'):
            try:
                dtend = datetime.fromisoformat(end_time['datetime'])
            except ValueError:
                pass

        # Fall back to date text if no <time> element
        if not dtstart and date_text:
            dtstart = self._parse_date_text(date_text)

        if not dtstart:
            return None

        event = {
            'title': title,
            'dtstart': dtstart,
        }
        if dtend:
            event['dtend'] = dtend
        if event_url:
            event['url'] = event_url

        return event

    def _parse_date_text(self, text: str) -> datetime | None:
        """Parse date from text like 'Wednesday,March4' or 'Sunday,March22'."""
        # Normalize: add space before day number
        text = re.sub(r'(\w),?(\w+?)(\d+)', r'\1, \2 \3', text)
        now = datetime.now()

        for fmt in ['%A, %B %d', '%A, %b %d']:
            try:
                dt = datetime.strptime(text, fmt)
                # Add current year, handle year boundary
                dt = dt.replace(year=now.year)
                if dt.month < now.month - 1:
                    dt = dt.replace(year=now.year + 1)
                return dt
            except ValueError:
                continue
        return None

    @classmethod
    def parse_args(cls, description=None):
        parser = argparse.ArgumentParser(
            description=description or "Scrape events from a Finalsite calendar"
        )
        parser.add_argument("--output", "-o", type=str, help="Output filename")
        parser.add_argument("--url", required=True, help="Calendar page URL")
        parser.add_argument("--name", type=str, default="Finalsite Calendar", help="Source name")
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")
        return parser.parse_args()


if __name__ == "__main__":
    FinalsiteScraper.setup_logging()
    args = FinalsiteScraper.parse_args()
    scraper = FinalsiteScraper(url=args.url, source_name=args.name)
    scraper.run(output=args.output)
