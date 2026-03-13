#!/usr/bin/env python3
"""
Scraper for LION Publishers events.
https://lionpublishers.com/events/

Parses the "Current Events" section which uses free-form WordPress HTML.
Events are listed as bullet points with links and date sub-items.

Usage:
    python scrapers/lion_publishers.py --output cities/publisher-resources/lion_publishers.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import re
from datetime import datetime
from typing import Any

import requests
from bs4 import BeautifulSoup

from lib.base import BaseScraper

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}

URL = "https://lionpublishers.com/events/"


class LIONPublishersScraper(BaseScraper):
    """Scraper for LION Publishers events."""

    name = "LION Publishers"
    domain = "lionpublishers.com"
    timezone = "America/New_York"

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch events from the LION Publishers events page."""
        response = requests.get(URL, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        events = []

        # Find the "Current Events" heading, then parse the next rich-text block
        current_heading = None
        for h3 in soup.select('h3.fl-heading'):
            if 'Current Events' in h3.get_text():
                current_heading = h3
                break

        if not current_heading:
            self.logger.warning("Could not find 'Current Events' section")
            return events

        # Walk forward through fl-module-content divs until we hit "Past Events"
        module = current_heading.find_parent('div', class_='fl-module')
        while module:
            module = module.find_next_sibling('div', class_='fl-module')
            if not module:
                break
            text = module.get_text()
            if 'Past Events' in text:
                break
            # Look for event list items in rich-text blocks
            for li in module.select('li'):
                event = self._parse_event_li(li)
                if event:
                    events.append(event)

        return events

    def _parse_event_li(self, li) -> dict[str, Any] | None:
        """Parse an event from a top-level <li> element.

        Expected structure:
        <li>
          The <a href="..."><strong>Event Title</strong></a> ...
          <ul>
            <li>September 9-11, 2026, in San Diego, CA</li>
            ...
          </ul>
        </li>
        """
        # Only parse top-level list items (not nested sub-items)
        if li.parent and li.parent.parent and li.parent.parent.name == 'li':
            return None

        # Get title from the link
        a = li.find('a')
        if not a:
            return None
        title = a.get_text(strip=True)
        if not title:
            return None
        url = a.get('href', '')

        # Look for date in sub-list items
        sub_items = li.select('ul > li')
        dtstart = None
        dtend = None
        location = None

        for sub in sub_items:
            text = sub.get_text(strip=True)
            parsed = self._parse_date_location(text)
            if parsed[0]:
                dtstart, dtend, location = parsed
                break

        if not dtstart:
            self.logger.debug(f"No date found for: {title}")
            return None

        self.logger.info(f"Found: {title} on {dtstart.strftime('%Y-%m-%d')}")

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend or dtstart,
            'url': url,
            'location': location or '',
            'description': '',
        }

    @staticmethod
    def _parse_date_location(text: str) -> tuple:
        """Parse date and location from text like 'September 9-11, 2026, in San Diego, CA'.

        Returns (dtstart, dtend, location) or (None, None, None).
        """
        # Split on ' in ' to separate date from location
        parts = re.split(r',?\s+in\s+', text, maxsplit=1)
        date_text = parts[0].strip().rstrip(',')
        location = parts[1].strip() if len(parts) > 1 else None

        # Try "Month D-D, YYYY" (date range)
        m = re.match(r'(\w+)\s+(\d+)\s*[-–]\s*(\d+),?\s+(\d{4})', date_text)
        if m:
            month, start_day, end_day, year = m.group(1), m.group(2), m.group(3), m.group(4)
            try:
                dtstart = datetime.strptime(f"{month} {start_day}, {year}", '%B %d, %Y')
                dtend = datetime.strptime(f"{month} {end_day}, {year}", '%B %d, %Y')
                return dtstart, dtend, location
            except ValueError:
                pass

        # Try "Month D, YYYY"
        m = re.match(r'(\w+ \d+),?\s+(\d{4})', date_text)
        if m:
            try:
                dtstart = datetime.strptime(f"{m.group(1)}, {m.group(2)}", '%B %d, %Y')
                return dtstart, None, location
            except ValueError:
                pass

        return None, None, None


if __name__ == '__main__':
    LIONPublishersScraper.main()
