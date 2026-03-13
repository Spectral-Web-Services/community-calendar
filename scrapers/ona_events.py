#!/usr/bin/env python3
"""
Scraper for Online News Association (ONA) events.
https://journalists.org/events/

Events are server-rendered HTML with date stubs like "Mar17" or "Mar30to/Apr1"
and optional time ranges like "3:00 PM - 4:00 PM".

Usage:
    python scrapers/ona_events.py --output cities/publisher-resources/ona_events.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import re
from datetime import datetime, timedelta
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

from lib.base import BaseScraper

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}

BASE_URL = "https://journalists.org"
EVENTS_URL = f"{BASE_URL}/events/"

MONTHS = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
}


class ONAEventsScraper(BaseScraper):
    """Scraper for ONA events."""

    name = "Online News Association"
    domain = "journalists.org"
    timezone = "America/New_York"

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch events from the ONA events page."""
        response = requests.get(EVENTS_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        events = []

        for event_div in soup.select('div.event'):
            event = self._parse_event(event_div)
            if event:
                events.append(event)

        return events

    def _parse_event(self, div) -> Optional[dict[str, Any]]:
        """Parse a single event from a div.event element."""
        # Title and URL
        a = div.select_one('a')
        if not a:
            return None
        title = a.get_text(strip=True)
        if not title:
            return None
        href = a.get('href', '')
        url = href if href.startswith('http') else f"{BASE_URL}{href}"

        # Date from stub text (e.g. "Mar17", "Mar30to/Apr1")
        date_stub = div.select_one('div.c-event-date-stub__wrapper')
        stub_text = date_stub.get_text(strip=True) if date_stub else ''
        if not stub_text:
            # Fallback: get from event-table text
            table = div.select_one('div.event-table')
            if table:
                stub_text = table.get_text(strip=True)[:20]

        dtstart, dtend = self._parse_date_stub(stub_text)
        if not dtstart:
            self.logger.debug(f"Could not parse date from stub '{stub_text}' for: {title}")
            return None

        # Time range
        time_el = div.select_one('span.c-event-date-stub__time')
        if time_el:
            time_text = time_el.get_text(strip=True)
            dtstart, dtend = self._apply_time(dtstart, dtend, time_text)

        self.logger.info(f"Found: {title} on {dtstart.strftime('%Y-%m-%d')}")

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend or dtstart,
            'url': url,
            'description': '',
        }

    @staticmethod
    def _parse_date_stub(text: str) -> tuple:
        """Parse date stubs like 'Mar17', 'Mar30to/Apr1'.

        Returns (dtstart, dtend) or (None, None).
        Infers year as current or next based on whether date has passed.
        """
        now = datetime.now()
        current_year = now.year

        def make_dt(month_num: int, day: int) -> datetime:
            dt = datetime(current_year, month_num, day)
            if dt.date() < now.date():
                dt = datetime(current_year + 1, month_num, day)
            return dt

        # Multi-day: "Mar30to/Apr1" or "Mar30to Apr1"
        m = re.match(r'([A-Za-z]+)(\d+)\s*to\s*/?\s*([A-Za-z]+)(\d+)', text)
        if m:
            month1 = MONTHS.get(m.group(1)[:3])
            day1 = int(m.group(2))
            month2 = MONTHS.get(m.group(3)[:3])
            day2 = int(m.group(4))
            if month1 and month2:
                try:
                    return make_dt(month1, day1), make_dt(month2, day2)
                except ValueError:
                    pass

        # Single day: "Mar17"
        m = re.match(r'([A-Za-z]+)(\d+)', text)
        if m:
            month = MONTHS.get(m.group(1)[:3])
            day = int(m.group(2))
            if month:
                try:
                    return make_dt(month, day), None
                except ValueError:
                    pass

        return None, None

    @staticmethod
    def _apply_time(dtstart: datetime, dtend: Optional[datetime], time_text: str) -> tuple:
        """Apply time range like '3:00 PM - 4:00 PM' to date(s)."""
        m = re.match(r'(\d+:\d+\s*[APap][Mm])\s*-\s*(\d+:\d+\s*[APap][Mm])', time_text)
        if m:
            try:
                start_time = datetime.strptime(m.group(1).strip(), '%I:%M %p')
                end_time = datetime.strptime(m.group(2).strip(), '%I:%M %p')
                dtstart = dtstart.replace(hour=start_time.hour, minute=start_time.minute)
                end_date = dtend or dtstart
                dtend = end_date.replace(hour=end_time.hour, minute=end_time.minute)
                return dtstart, dtend
            except ValueError:
                pass

        # Single time: "3:00 PM"
        m = re.match(r'(\d+:\d+\s*[APap][Mm])', time_text)
        if m:
            try:
                start_time = datetime.strptime(m.group(1).strip(), '%I:%M %p')
                dtstart = dtstart.replace(hour=start_time.hour, minute=start_time.minute)
                return dtstart, dtend
            except ValueError:
                pass

        return dtstart, dtend


if __name__ == '__main__':
    ONAEventsScraper.main()
