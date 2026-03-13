#!/usr/bin/env python3
"""
Scraper for Editor & Publisher industry calendar.
https://www.editorandpublisher.com/calendar/

Events appear as:
- Featured: div.content-item with h3 headings containing "Title | Date"
- List: a.single-story-head links containing "Title | Date"

Dates are embedded in the title text after a pipe character.

Usage:
    python scrapers/editor_publisher.py --output cities/publisher-resources/editor_publisher.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import re
from datetime import datetime
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

from lib.base import BaseScraper

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}

BASE_URL = "https://www.editorandpublisher.com"
CALENDAR_URL = f"{BASE_URL}/calendar/"


class EditorPublisherScraper(BaseScraper):
    """Scraper for Editor & Publisher industry events calendar."""

    name = "Editor & Publisher"
    domain = "editorandpublisher.com"
    timezone = "America/New_York"

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch events from the E&P calendar page."""
        response = requests.get(CALENDAR_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        events = []
        seen_hrefs = set()

        # Featured events: div.content-item with h3 containing title | date
        for item in soup.select('div.content-item'):
            h3 = item.find('h3')
            if not h3:
                continue
            a = h3.find('a') or item.find('a', href=True)
            href = a.get('href', '') if a else ''
            if not href or '/stories/' not in href:
                continue
            if href in seen_hrefs:
                continue
            seen_hrefs.add(href)

            event = self._parse_title_date(h3.get_text(strip=True), href)
            if event:
                events.append(event)

        # List events: a.single-story-head
        for a in soup.select('a.single-story-head'):
            href = a.get('href', '')
            if href in seen_hrefs:
                continue
            seen_hrefs.add(href)

            event = self._parse_title_date(a.get_text(strip=True), href)
            if event:
                events.append(event)

        return events

    def _parse_title_date(self, text: str, href: str) -> Optional[dict[str, Any]]:
        """Parse event from combined 'Title | Date' text and href."""
        # Split on pipe to separate title from date
        if '|' in text:
            parts = text.rsplit('|', 1)
            title = parts[0].strip()
            date_str = parts[1].strip()
        else:
            title = text.strip()
            date_str = ''

        if not title:
            return None

        dtstart, dtend = self._parse_date_range(date_str)
        if not dtstart:
            self.logger.debug(f"Could not parse date from: {text}")
            return None

        url = href if href.startswith('http') else f"{BASE_URL}{href}"

        self.logger.info(f"Found: {title} on {dtstart.strftime('%Y-%m-%d')}")

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend or dtstart,
            'url': url,
            'description': '',
        }

    @staticmethod
    def _parse_date_range(text: str) -> tuple:
        """Parse date ranges like 'March 30 - April 1', 'April 26-27', 'May 8', 'Sept. 14-16'.

        Infers year as current or next year based on whether the date has passed.
        Returns (dtstart, dtend) or (None, None).
        """
        text = text.strip()
        if not text:
            return None, None

        now = datetime.now()
        current_year = now.year

        # Normalize abbreviated months
        abbrevs = {
            'Jan.': 'January', 'Feb.': 'February', 'Mar.': 'March',
            'Apr.': 'April', 'Jun.': 'June', 'Jul.': 'July',
            'Aug.': 'August', 'Sept.': 'September', 'Oct.': 'October',
            'Nov.': 'November', 'Dec.': 'December',
        }
        for abbr, full in abbrevs.items():
            text = text.replace(abbr, full)

        def pick_year(month_str: str, day: int) -> int:
            """Pick current or next year so the date is in the future."""
            try:
                dt = datetime.strptime(f"{month_str} {day}, {current_year}", '%B %d, %Y')
                return current_year if dt >= now.replace(hour=0, minute=0, second=0) else current_year + 1
            except ValueError:
                return current_year

        # Pattern: "Month D - Month D" (cross-month range)
        m = re.match(r'(\w+)\s+(\d+)\s*[-–]\s*(\w+)\s+(\d+)', text)
        if m:
            month1, day1, month2, day2 = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
            year = pick_year(month1, day1)
            try:
                dtstart = datetime.strptime(f"{month1} {day1}, {year}", '%B %d, %Y')
                dtend = datetime.strptime(f"{month2} {day2}, {year}", '%B %d, %Y')
                return dtstart, dtend
            except ValueError:
                pass

        # Pattern: "Month D-D" (same-month range)
        m = re.match(r'(\w+)\s+(\d+)\s*[-–]\s*(\d+)', text)
        if m:
            month, day1, day2 = m.group(1), int(m.group(2)), int(m.group(3))
            year = pick_year(month, day1)
            try:
                dtstart = datetime.strptime(f"{month} {day1}, {year}", '%B %d, %Y')
                dtend = datetime.strptime(f"{month} {day2}, {year}", '%B %d, %Y')
                return dtstart, dtend
            except ValueError:
                pass

        # Pattern: "Month D" (single day)
        m = re.match(r'(\w+)\s+(\d+)$', text)
        if m:
            month, day = m.group(1), int(m.group(2))
            year = pick_year(month, day)
            try:
                dtstart = datetime.strptime(f"{month} {day}, {year}", '%B %d, %Y')
                return dtstart, None
            except ValueError:
                pass

        return None, None


if __name__ == '__main__':
    EditorPublisherScraper.main()
