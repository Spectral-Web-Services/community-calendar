#!/usr/bin/env python3
"""
Scraper for Visit Petaluma's curated events listing.
https://www.visitpetaluma.com/find-events/

Visit Petaluma is the city's tourism board and operates a WordPress +
The Events Calendar site. The plugin's iCal export and Tribe REST API
are both disabled, so we scrape the rendered listing pages.

This is an AGGREGATOR — most events also appear in primary venue
sources (Mystic, Phoenix, Russe, etc.). It's added to the aggregators
set in scripts/combine_ics.py so primary sources win during dedup.

For recurring events we only emit the next occurrence shown on the
listing card (the pattern, e.g. "Occurs weekly on Saturday", is
included in the description so a downstream consumer can expand if
desired).
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

MONTH_MAP = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}


class VisitPetalumaScraper(BaseScraper):
    name = "Visit Petaluma"
    domain = "visitpetaluma.com"
    timezone = "America/Los_Angeles"

    BASE_URL = "https://www.visitpetaluma.com"
    LIST_URL = f"{BASE_URL}/find-events/"
    MAX_PAGES = 25

    def fetch_events(self) -> list[dict[str, Any]]:
        tz = ZoneInfo(self.timezone)
        now = datetime.now(tz)
        events: list[dict[str, Any]] = []

        for page in range(1, self.MAX_PAGES + 1):
            url = self.LIST_URL if page == 1 else f"{self.LIST_URL}page/{page}/"
            self.logger.info(f"Fetching page {page}: {url}")
            resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=30)
            if resp.status_code == 404:
                break
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, 'html.parser')
            cards = soup.select('article.event-card')
            if not cards:
                break

            for card in cards:
                try:
                    event = self._parse_card(card, now, tz)
                    if event:
                        events.append(event)
                except Exception as e:
                    self.logger.warning(f"Skipping card: {e}")

            # Stop when the pagination block stops advertising a higher page number.
            max_page = page
            for a in soup.select('.pagination a[href*="/page/"]'):
                m = re.search(r'/page/(\d+)/?', a.get('href', ''))
                if m:
                    max_page = max(max_page, int(m.group(1)))
            if page >= max_page:
                break

        return events

    def _parse_card(self, card, now: datetime, tz: ZoneInfo) -> dict[str, Any] | None:
        title_el = card.select_one('h3.post-title, .post-title, h2.post-title')
        link_el = card.select_one('a.primary-card-link, a[href*="/event/"]')
        if not title_el or not link_el:
            return None
        title = title_el.get_text(strip=True)
        event_url = link_el.get('href', self.LIST_URL).strip()

        month_el = card.select_one('.event-start-date .m')
        day_el = card.select_one('.event-start-date .d')
        if not month_el or not day_el:
            return None
        month_str = month_el.get_text(strip=True).lower()
        day_str = day_el.get_text(strip=True)
        month = MONTH_MAP.get(month_str[:3])
        if not month:
            return None
        try:
            day = int(day_str)
        except ValueError:
            return None
        # Year inference: assume current year, roll forward if the date
        # has clearly already passed (>14 days ago).
        year = now.year
        candidate = datetime(year, month, day, tzinfo=tz)
        if candidate < now - timedelta(days=14):
            year += 1

        time_el = card.select_one('.event-time')
        time_text = time_el.get_text(' ', strip=True) if time_el else ''
        dtstart, dtend = self._parse_time(time_text, year, month, day, tz)

        # Image
        img_el = card.select_one('img[src]')
        image_url = img_el.get('src') if img_el else ''

        # Recurrence note for description
        pattern_el = card.select_one('.event-occurrence-pattern')
        count_el = card.select_one('.event-occurrence-count')
        desc_parts = []
        if pattern_el:
            p = pattern_el.get_text(' ', strip=True)
            if p:
                desc_parts.append(p)
        if count_el:
            c = count_el.get_text(' ', strip=True)
            if c:
                desc_parts.append(f"({c} occurrences)")
        desc_parts.append(f"More info: {event_url}")

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend,
            'url': event_url,
            'location': '',  # not in card; per-event fetches would add it
            'description': ' — '.join(desc_parts) if len(desc_parts) > 1 else desc_parts[0],
            'image_url': image_url,
        }

    @staticmethod
    def _parse_time(time_text: str, year: int, month: int, day: int, tz: ZoneInfo) -> tuple[datetime, datetime]:
        """Parse '7:00 pm - 9:00 pm' (or similar) into datetimes for the given date."""
        times = re.findall(r'(\d{1,2}):(\d{2})\s*(am|pm)', time_text, re.IGNORECASE)
        if times:
            sh, sm, sap = times[0]
            start = datetime(year, month, day, _to_24(sh, sap), int(sm), tzinfo=tz)
            if len(times) > 1:
                eh, em, eap = times[1]
                end = datetime(year, month, day, _to_24(eh, eap), int(em), tzinfo=tz)
                if end <= start:
                    end = start + timedelta(hours=2)
            else:
                end = start + timedelta(hours=2)
            return start, end
        # No time given — default to 7pm for 2 hours
        start = datetime(year, month, day, 19, 0, tzinfo=tz)
        return start, start + timedelta(hours=2)


def _to_24(hour_str: str, ampm: str) -> int:
    h = int(hour_str)
    if ampm.upper() == 'PM' and h != 12:
        return h + 12
    if ampm.upper() == 'AM' and h == 12:
        return 0
    return h


if __name__ == '__main__':
    VisitPetalumaScraper.main()
