#!/usr/bin/env python3
"""
Scraper for Usher Gallery Petaluma events.
https://ushergallerypetaluma.com/

Shopify site using the "AI Event Block" Shopify app. Each event renders
as a div with class containing 'ai-event-card', with child elements for
title, date, time, location, and description.
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


class UsherGalleryScraper(BaseScraper):
    name = "Usher Gallery"
    domain = "ushergallerypetaluma.com"
    timezone = "America/Los_Angeles"

    PAGE_URL = "https://ushergallerypetaluma.com/"
    VENUE = "Usher Gallery, 142 Petaluma Blvd N, Petaluma, CA 94952"

    def fetch_events(self) -> list[dict[str, Any]]:
        self.logger.info(f"Fetching {self.PAGE_URL}")
        response = requests.get(self.PAGE_URL, headers=DEFAULT_HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.select('[class*="ai-event-card"]')
        self.logger.info(f"Found {len(cards)} event cards")

        tz = ZoneInfo(self.timezone)
        events = []
        for card in cards:
            try:
                event = self._parse_card(card, tz)
                if event:
                    events.append(event)
            except Exception as e:
                self.logger.warning(f"Skipping card: {e}")
        return events

    def _parse_card(self, card, tz: ZoneInfo) -> dict[str, Any] | None:
        title_el = card.select_one('[class*="ai-event-title"]')
        date_el = card.select_one('[class*="ai-event-date"]')
        time_el = card.select_one('[class*="ai-event-time"]')
        loc_el = card.select_one('[class*="ai-event-location"]')
        desc_el = card.select_one('[class*="ai-event-description"]')

        if not title_el or not date_el:
            return None

        title = title_el.get_text(strip=True)
        # Strip leading "Date:" label written by the widget
        date_text = re.sub(r'^Date:\s*', '', date_el.get_text(' ', strip=True), flags=re.IGNORECASE)
        time_text = re.sub(r'^Time:\s*', '', time_el.get_text(' ', strip=True), flags=re.IGNORECASE) if time_el else ''
        loc_text = re.sub(r'^Location:\s*', '', loc_el.get_text(' ', strip=True), flags=re.IGNORECASE) if loc_el else ''

        dtstart, dtend = self._parse_when(date_text, time_text, tz)
        if not dtstart:
            self.logger.warning(f"Could not parse date '{date_text}' / time '{time_text}' for: {title}")
            return None

        description = ' '.join(p.get_text(' ', strip=True) for p in desc_el.find_all('p')) if desc_el else ''

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend,
            'url': self.PAGE_URL,
            'location': loc_text or self.VENUE,
            'description': description,
        }

    @staticmethod
    def _parse_when(date_text: str, time_text: str, tz: ZoneInfo) -> tuple[datetime | None, datetime | None]:
        """
        Parse date strings like 'Friday, April 17th, 2026' or 'May 2nd, 2026'
        plus time strings like '5:00 PM - 8:00 PM'.
        """
        # Strip ordinal suffixes (1st, 2nd, 3rd, 4th, ...)
        clean_date = re.sub(r'(\d+)(st|nd|rd|th)\b', r'\1', date_text, flags=re.IGNORECASE)
        # Try a few common formats
        date_only = None
        for fmt in ('%A, %B %d, %Y', '%B %d, %Y', '%a, %b %d, %Y', '%b %d, %Y'):
            try:
                date_only = datetime.strptime(clean_date.strip(), fmt)
                break
            except ValueError:
                continue
        if not date_only:
            return None, None

        # Parse 'H:MM AM - H:MM PM' (or single time)
        times = re.findall(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_text, re.IGNORECASE)
        if times:
            sh, sm, sap = times[0]
            start = date_only.replace(hour=_to_24(sh, sap), minute=int(sm), tzinfo=tz)
            if len(times) > 1:
                eh, em, eap = times[1]
                end = date_only.replace(hour=_to_24(eh, eap), minute=int(em), tzinfo=tz)
                if end <= start:
                    end = start + timedelta(hours=2)
            else:
                end = start + timedelta(hours=2)
            return start, end

        # Default: full-day starting noon
        start = date_only.replace(hour=12, minute=0, tzinfo=tz)
        return start, start + timedelta(hours=2)


def _to_24(hour_str: str, ampm: str) -> int:
    h = int(hour_str)
    if ampm.upper() == 'PM' and h != 12:
        return h + 12
    if ampm.upper() == 'AM' and h == 12:
        return 0
    return h


if __name__ == '__main__':
    UsherGalleryScraper.main()
