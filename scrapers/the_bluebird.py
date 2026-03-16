#!/usr/bin/env python3
"""
Scraper for The Bluebird Nightclub (Bloomington, IN).
https://thebluebird.ws/calendar/

Parses the Seetickets event listings rendered on the calendar page.
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

CALENDAR_URL = "https://thebluebird.ws/calendar/"
TZ = ZoneInfo("America/Indiana/Indianapolis")


class BluebirdScraper(BaseScraper):
    """Scraper for The Bluebird Nightclub events."""

    name = "The Bluebird"
    domain = "thebluebird.ws"
    timezone = "America/Indiana/Indianapolis"

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch and parse events from the calendar page."""
        resp = requests.get(CALENDAR_URL, timeout=30)
        resp.raise_for_status()
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        events = []

        for card in soup.select('.seetickets-list-event-container'):
            event = self._parse_card(card)
            if event:
                events.append(event)

        self.logger.info(f"Found {len(events)} events")
        return events

    def _parse_card(self, card) -> Optional[dict[str, Any]]:
        """Parse a single event card."""
        # Title
        title_el = card.select_one('.title a')
        if not title_el:
            return None
        title = title_el.get_text(strip=True)

        # URL
        url = title_el.get('href', '')

        # Date - format: "Tue Mar 17"
        date_el = card.select_one('.date')
        if not date_el:
            return None
        date_text = date_el.get_text(strip=True)

        # Time - format: "8:00PM"
        time_el = card.select_one('.see-showtime')
        time_text = time_el.get_text(strip=True) if time_el else ''

        dtstart = self._parse_datetime(date_text, time_text)
        if not dtstart:
            return None

        # Image
        img_el = card.select_one('.seetickets-list-view-event-image')
        image_url = img_el.get('src', '') if img_el else ''

        # Supporting info
        headliners = card.select_one('.headliners')
        support = card.select_one('.supporting-talent')
        parts = []
        if headliners and headliners.get_text(strip=True):
            parts.append(headliners.get_text(strip=True))
        if support and support.get_text(strip=True):
            parts.append(f"w/ {support.get_text(strip=True)}")
        description = ' '.join(parts)

        event = {
            'title': title,
            'dtstart': dtstart,
            'url': url,
            'location': 'The Bluebird, 216 N Walnut St, Bloomington, IN',
            'description': description,
        }
        if image_url:
            event['image_url'] = image_url
        return event

    def _parse_datetime(self, date_text: str, time_text: str) -> Optional[datetime]:
        """Parse date like 'Tue Mar 17' and time like '8:00PM'."""
        # Strip day-of-week prefix
        date_text = re.sub(r'^[A-Za-z]+\s+', '', date_text.strip())

        now = datetime.now(TZ)
        year = now.year

        try:
            dt = datetime.strptime(f"{date_text} {year}", "%b %d %Y")
        except ValueError:
            return None

        # If month is before current month, assume next year
        if dt.month < now.month:
            dt = dt.replace(year=year + 1)

        # Parse time
        if time_text:
            try:
                t = datetime.strptime(time_text.strip(), "%I:%M%p")
                dt = dt.replace(hour=t.hour, minute=t.minute)
            except ValueError:
                dt = dt.replace(hour=20)  # default 8 PM
        else:
            dt = dt.replace(hour=20)

        return dt.replace(tzinfo=TZ)


if __name__ == '__main__':
    BluebirdScraper.main()
