#!/usr/bin/env python3
"""
Scraper for Montagne Russe Winery (Petaluma) events.
https://www.russewines.com/Events

Vin65 platform. Top-level events live in `.v65-calendarList-Event`
blocks with title, time span, and venue. A recurring "Live Music |
Saturdays" block carries its weekly artist lineup as a bolded date list
inside the description — we expand those into individual dated events
so the calendar shows the right artist on the right Saturday.
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

MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6, 'jul': 7,
    'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}


class RusseWinesScraper(BaseScraper):
    name = "Montagne Russe Winery"
    domain = "russewines.com"
    timezone = "America/Los_Angeles"

    PAGE_URL = "https://www.russewines.com/Events"
    BASE_URL = "https://www.russewines.com"
    VENUE = "Montagne Russe Winery, 155 Petaluma Blvd N, Petaluma, CA 94952"

    def fetch_events(self) -> list[dict[str, Any]]:
        self.logger.info(f"Fetching {self.PAGE_URL}")
        response = requests.get(self.PAGE_URL, headers=DEFAULT_HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        blocks = soup.select('.v65-calendarList-Event')
        self.logger.info(f"Found {len(blocks)} event blocks")

        tz = ZoneInfo(self.timezone)
        events = []
        for block in blocks:
            try:
                events.extend(self._parse_block(block, tz))
            except Exception as e:
                self.logger.warning(f"Skipping block: {e}")
        return events

    def _parse_block(self, block, tz: ZoneInfo) -> list[dict[str, Any]]:
        title_el = block.select_one('.v65-calendarList-Title a')
        time_span_el = block.select_one('.v65-calendarList-Time')
        desc_el = block.select_one('.v65-calendarList-Description')

        if not title_el:
            return []
        title = title_el.get_text(strip=True)
        href = title_el.get('href', '')
        event_url = (self.BASE_URL + href) if href.startswith('/') else (href or self.PAGE_URL)

        time_span = time_span_el.get_text(' ', strip=True) if time_span_el else ''
        start_hour, start_min, end_hour, end_min = self._parse_time_of_day(block)

        dstart, dend = self._parse_date_span(time_span)
        if not dstart:
            self.logger.warning(f"No parseable date for: {title}")
            return []

        # Recurring block: expand artist lineup from description if present.
        if dend and dend > dstart + timedelta(days=14) and desc_el is not None:
            dated_lines = self._extract_dated_lines(desc_el, dstart.year)
            if dated_lines:
                out = []
                for date, label in dated_lines:
                    start = datetime(date.year, date.month, date.day, start_hour, start_min, tzinfo=tz)
                    end = datetime(date.year, date.month, date.day, end_hour, end_min, tzinfo=tz)
                    if end <= start:
                        end = start + timedelta(hours=2)
                    out.append({
                        'title': f"{title.split('|')[0].strip()}: {label}" if '|' in title else f"{title}: {label}",
                        'dtstart': start,
                        'dtend': end,
                        'url': event_url,
                        'location': self.VENUE,
                        'description': label,
                    })
                return out
            # No dated lines extracted — skip the multi-month parent event (too long to be useful).
            return []

        # Single-date event
        start = datetime(dstart.year, dstart.month, dstart.day, start_hour, start_min, tzinfo=tz)
        end_date = dend or dstart
        end = datetime(end_date.year, end_date.month, end_date.day, end_hour, end_min, tzinfo=tz)
        if end <= start:
            end = start + timedelta(hours=2)

        description = ' '.join(p.get_text(' ', strip=True) for p in desc_el.find_all('p')) if desc_el else ''
        return [{
            'title': title,
            'dtstart': start,
            'dtend': end,
            'url': event_url,
            'location': self.VENUE,
            'description': description[:800],
        }]

    @staticmethod
    def _parse_time_of_day(block) -> tuple[int, int, int, int]:
        """Pull e.g. '5:00 PM to 7:00 PM' out of the block text, with fallback."""
        text = block.get_text(' ', strip=True)
        m = re.search(
            r'(\d{1,2}):(\d{2})\s*(AM|PM)\s*(?:to|-|–)\s*(\d{1,2}):(\d{2})\s*(AM|PM)',
            text, re.IGNORECASE,
        )
        if m:
            sh = _to_24(m.group(1), m.group(3))
            sm = int(m.group(2))
            eh = _to_24(m.group(4), m.group(6))
            em = int(m.group(5))
            return sh, sm, eh, em
        return 18, 0, 20, 0  # default 6-8pm

    @staticmethod
    def _parse_date_span(time_span: str) -> tuple[datetime | None, datetime | None]:
        """Parse 'Sat, May 9, 2026' or 'Sat, Jan 31, 2026 - Sun, Nov 29, 2026'."""
        # Split on en-dash or hyphen between two date strings
        parts = re.split(r'\s+[-–]\s+', time_span)
        dstart = _try_parse_one_date(parts[0]) if parts else None
        dend = _try_parse_one_date(parts[1]) if len(parts) > 1 else None
        return dstart, dend

    @staticmethod
    def _extract_dated_lines(desc_el, default_year: int) -> list[tuple[datetime, str]]:
        """
        Pull '<strong>Month Day</strong> - Artist Name' patterns out of the
        description. The text after the </strong> may continue on the next
        line (the page uses <br/> between date and artist), so we flatten
        the description's text first and then run the regex across the
        whole blob, allowing the separator to span newlines.
        """
        text = desc_el.get_text(' ', strip=False)
        # Collapse runs of whitespace and non-breaking spaces
        text = text.replace('\xa0', ' ')
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r' {2,}', ' ', text).strip()

        out = []
        # Match e.g. "March 21 - Dan Durkin (head vocalist...)" — non-greedy
        # capture up to the next month-day boundary or end of string.
        month_alt = '|'.join(MONTHS)
        pattern = re.compile(
            rf'\b({month_alt})\s+(\d{{1,2}})\s*[-–]\s*(.+?)(?=\s*\b(?:{month_alt})\s+\d{{1,2}}\s*[-–]|$)',
            re.IGNORECASE,
        )
        for m in pattern.finditer(text):
            month = MONTHS[m.group(1).lower()]
            day = int(m.group(2))
            label = m.group(3).strip().rstrip('+').strip()
            # Trim trailing junk like "BUTTER & EGGS FESTIVAL 10AM-5pm"
            try:
                d = datetime(default_year, month, day)
            except ValueError:
                continue
            out.append((d, label[:200]))
        return out


def _to_24(hour_str: str, ampm: str) -> int:
    h = int(hour_str)
    if ampm.upper() == 'PM' and h != 12:
        return h + 12
    if ampm.upper() == 'AM' and h == 12:
        return 0
    return h


def _try_parse_one_date(s: str) -> datetime | None:
    if not s:
        return None
    s = s.strip().rstrip(',')
    # Strip leading weekday (e.g., 'Sat, ')
    s = re.sub(r'^(Sun|Mon|Tue|Wed|Thu|Fri|Sat)[a-z]*,?\s*', '', s, flags=re.IGNORECASE)
    for fmt in ('%b %d, %Y', '%B %d, %Y'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


if __name__ == '__main__':
    RusseWinesScraper.main()
