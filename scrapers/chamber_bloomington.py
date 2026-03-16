#!/usr/bin/env python3
"""
Scraper for Greater Bloomington Chamber of Commerce events.
https://web.chamberbloomington.org/atlas/calendar

Uses the mobile events page which renders server-side HTML.
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import re
from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

from lib.base import BaseScraper

BASE_URL = "https://web.chamberbloomington.org"
EVENTS_URL = f"{BASE_URL}/mobile/events.aspx"
TZ = ZoneInfo("America/Indiana/Indianapolis")


class ChamberBloomingtonScraper(BaseScraper):
    """Scraper for Bloomington Chamber of Commerce events."""

    name = "Bloomington Chamber of Commerce"
    domain = "chamberbloomington.org"
    timezone = "America/Indiana/Indianapolis"

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch events from the mobile events page."""
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; community-calendar/1.0)'}
        resp = requests.get(EVENTS_URL, headers=headers, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        events = []
        for link in soup.select('li a[href*=eventDetail]'):
            event = self._parse_listing(link)
            if event:
                events.append(event)

        self.logger.info(f"Found {len(events)} events")
        return events

    def _parse_listing(self, link) -> Optional[dict[str, Any]]:
        """Parse an event from the listing page link."""
        text = link.get_text(strip=True)
        if not text:
            return None

        href = link.get('href', '')
        url = f"{BASE_URL}{href}" if href.startswith('/') else href

        # Parse title and date from text like:
        # "Event Name3/20/2026 | 1:30 PM - 2:30 PM"
        # "Event Name3/20/2026 - 3/29/2026"
        match = re.match(r'^(.+?)(\d{1,2}/\d{1,2}/\d{4})\s*(?:\|\s*(.+))?(?:\s*-\s*(\d{1,2}/\d{1,2}/\d{4}))?', text)
        if not match:
            return None

        title = match.group(1).strip()
        date_str = match.group(2)
        time_str = match.group(3)  # e.g. "1:30 PM - 2:30 PM" or None
        end_date_str = match.group(4)  # e.g. "3/29/2026" or None

        dtstart = self._parse_datetime(date_str, time_str)
        if not dtstart:
            return None

        return {
            'title': title,
            'dtstart': dtstart,
            'url': url,
            'location': '',
            'description': '',
        }

    def _parse_datetime(self, date_str: str, time_str: Optional[str]) -> Optional[datetime]:
        """Parse date and optional time."""
        try:
            dt = datetime.strptime(date_str, "%m/%d/%Y")
        except ValueError:
            return None

        if time_str:
            # Extract start time from "1:30 PM - 2:30 PM" or "6:00 PM"
            time_match = re.match(r'(\d{1,2}:\d{2}\s*[AP]M)', time_str.strip())
            if time_match:
                try:
                    t = datetime.strptime(time_match.group(1).strip(), "%I:%M %p")
                    dt = dt.replace(hour=t.hour, minute=t.minute)
                except ValueError:
                    pass

        return dt.replace(tzinfo=TZ)


if __name__ == '__main__':
    ChamberBloomingtonScraper.main()
