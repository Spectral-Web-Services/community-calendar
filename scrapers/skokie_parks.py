#!/usr/bin/env python3
"""Scraper for Skokie Park District events.

Parses the server-rendered events listing page. Each event has
structured HTML with title, date/time, location, and detail URL.
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import html as html_mod
import logging
import re
from datetime import datetime, timezone
from typing import Any

import requests

from lib.base import BaseScraper

logger = logging.getLogger(__name__)

EVENTS_URL = "https://www.skokieparks.org/events/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}


class SkokieParksScraper(BaseScraper):
    name = "Skokie Park District"
    domain = "skokieparks.org"

    def fetch_events(self) -> list[dict[str, Any]]:
        resp = requests.get(EVENTS_URL, timeout=30, headers=HEADERS)
        resp.raise_for_status()
        html = resp.text

        events = []
        # Each event is an <a> with name="EventAnchor_..."
        pattern = re.compile(
            r'<a\s+href="(/events/[^"]+)"[^>]*name="EventAnchor_\d+[^"]*">'
            r'([\s\S]*?)</a>',
            re.DOTALL
        )

        for m in pattern.finditer(html):
            parsed = self._parse_event(m.group(1), m.group(2))
            if parsed:
                events.append(parsed)

        logger.info(f"Parsed {len(events)} events from listing page")
        return events

    def _parse_event(self, href: str, block: str) -> dict[str, Any] | None:
        # Title
        title_m = re.search(r'<h2 class="title">([^<]+)</h2>', block)
        if not title_m:
            return None
        title = html_mod.unescape(title_m.group(1).strip())

        # Skip cancelled events
        if title.upper().startswith('CANCELLED'):
            return None

        # Date/time: after <span class="visually-hidden">Date</span>
        date_m = re.search(
            r'class="event-date">\s*<span[^>]*>Date</span>\s*([^<]+)',
            block
        )
        if not date_m:
            return None
        datetext = date_m.group(1).strip()

        # Parse "March 14, 2026 7:00 PM - 9:00 PM" or "March 16-20 (All Day)"
        dtstart = self._parse_date(datetext)
        if not dtstart:
            return None

        # Skip past events
        if dtstart.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return None

        # Location: after <span class="visually-hidden">Location</span>
        loc_m = re.search(
            r'class="event-loc">\s*<span[^>]*>Location</span>\s*([^<]+)',
            block
        )
        location = loc_m.group(1).strip() if loc_m else 'Skokie Park District'

        url = f"https://www.skokieparks.org{href}"

        return {
            'title': title,
            'dtstart': dtstart,
            'location': location,
            'url': url,
        }

    def _parse_date(self, text: str) -> datetime | None:
        """Parse various date formats from Skokie Parks."""
        # "March 14, 2026 7:00 PM - 9:00 PM"
        m = re.match(r'(\w+ \d+, \d{4})\s+(\d+:\d+ [AP]M)', text)
        if m:
            try:
                return datetime.strptime(f"{m.group(1)} {m.group(2)}", "%B %d, %Y %I:%M %p")
            except ValueError:
                pass

        # "March 14, 2026" (all day)
        m = re.match(r'(\w+ \d+, \d{4})', text)
        if m:
            try:
                return datetime.strptime(m.group(1), "%B %d, %Y")
            except ValueError:
                pass

        # "March 16-20" range - take start date
        m = re.match(r'(\w+) (\d+)-\d+', text)
        if m:
            # Need year context - assume current/next year
            month_day = f"{m.group(1)} {m.group(2)}"
            for year in [2026, 2027]:
                try:
                    return datetime.strptime(f"{month_day}, {year}", "%B %d, %Y")
                except ValueError:
                    pass

        return None


if __name__ == '__main__':
    SkokieParksScraper.main()
