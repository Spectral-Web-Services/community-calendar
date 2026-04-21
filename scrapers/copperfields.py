#!/usr/bin/env python3
"""
Scraper for Copperfield's Books Petaluma events.
https://copperfieldsbooks.com/upcoming-events?tags=2073

Drupal/IndieCommerce event listing. The tags=2073 query filters to the
Petaluma store. Each event renders as a `.views-row` containing an
`article.event-list` with structured date/time/place/details fields.
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import re
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

from lib.base import BaseScraper
from lib.utils import DEFAULT_HEADERS


class CopperfieldsScraper(BaseScraper):
    name = "Copperfield's Books Petaluma"
    domain = "copperfieldsbooks.com"
    timezone = "America/Los_Angeles"

    PAGE_URL = "https://copperfieldsbooks.com/upcoming-events?tags=2073"
    BASE_URL = "https://copperfieldsbooks.com"

    def fetch_events(self) -> list[dict[str, Any]]:
        self.logger.info(f"Fetching {self.PAGE_URL}")
        response = requests.get(self.PAGE_URL, headers=DEFAULT_HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.select('.views-row article.event-list, .views-row .event-list')
        if not rows:
            rows = soup.select('.views-row')
        self.logger.info(f"Found {len(rows)} event rows")

        tz = ZoneInfo(self.timezone)
        events = []
        for row in rows:
            try:
                event = self._parse_row(row, tz)
                if event:
                    events.append(event)
            except Exception as e:
                self.logger.warning(f"Skipping row: {e}")
        return events

    def _parse_row(self, row, tz: ZoneInfo) -> dict[str, Any] | None:
        title_el = row.select_one('.event-list__title a')
        if not title_el:
            return None
        title = title_el.get_text(strip=True)
        href = title_el.get('href', '')
        event_url = (self.BASE_URL + href) if href.startswith('/') else (href or self.PAGE_URL)

        date_text = self._field_value(row, 'Date:')
        time_text = self._field_value(row, 'Time:')
        place_text = self._field_value(row, 'Place:')

        dtstart, dtend = self._parse_when(date_text, time_text, tz)
        if not dtstart:
            self.logger.warning(f"Could not parse date '{date_text}' / time '{time_text}' for: {title}")
            return None

        body_el = row.select_one('.event-list__body')
        description = body_el.get_text(' ', strip=True) if body_el else ''

        rsvp_el = row.select_one('a.event-list__links--rsvp')
        if rsvp_el and rsvp_el.get('href'):
            description = (description + f"\nRSVP: {rsvp_el['href']}").strip()

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend,
            'url': event_url,
            'location': self._format_location(place_text),
            'description': description,
        }

    @staticmethod
    def _field_value(row, label: str) -> str:
        """Return text of `.event-list__details--item` whose label matches."""
        for item in row.select('.event-list__details--item'):
            label_el = item.select_one('.event-list__details--label')
            if label_el and label_el.get_text(strip=True).rstrip(':') == label.rstrip(':'):
                full = item.get_text(' ', strip=True)
                return re.sub(r'^' + re.escape(label) + r'\s*', '', full).strip()
        return ''

    @staticmethod
    def _parse_when(date_text: str, time_text: str, tz: ZoneInfo) -> tuple[datetime | None, datetime | None]:
        """Parse 'Thu, 4/23/2026' + '7:00pm' (optionally a range)."""
        if not date_text:
            return None, None
        clean = re.sub(r'^(Sun|Mon|Tue|Wed|Thu|Fri|Sat)[a-z]*,?\s*', '', date_text, flags=re.IGNORECASE)
        date_only = None
        for fmt in ('%m/%d/%Y', '%B %d, %Y', '%b %d, %Y'):
            try:
                date_only = datetime.strptime(clean.strip(), fmt)
                break
            except ValueError:
                continue
        if not date_only:
            return None, None

        times = re.findall(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', time_text or '', re.IGNORECASE)
        if times:
            sh, sm, sap = times[0]
            start = date_only.replace(hour=_to_24(sh, sap), minute=int(sm or 0), tzinfo=tz)
            if len(times) > 1:
                eh, em, eap = times[1]
                end = date_only.replace(hour=_to_24(eh, eap), minute=int(em or 0), tzinfo=tz)
                if end <= start:
                    end = start + timedelta(hours=1)
            else:
                end = start + timedelta(hours=1)
            return start, end

        start = date_only.replace(hour=19, minute=0, tzinfo=tz)
        return start, start + timedelta(hours=1)

    @staticmethod
    def _format_location(place_text: str) -> str:
        if not place_text:
            return "Copperfield's Books Petaluma, 140 Kentucky St, Petaluma, CA 94952"
        cleaned = re.sub(r'^Petaluma\s+', '', place_text)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return f"Copperfield's Books Petaluma, {cleaned}" if 'petaluma' not in cleaned.lower() else cleaned


def _to_24(hour_str: str, ampm: str) -> int:
    h = int(hour_str)
    if ampm.upper() == 'PM' and h != 12:
        return h + 12
    if ampm.upper() == 'AM' and h == 12:
        return 0
    return h


if __name__ == '__main__':
    CopperfieldsScraper.main()
