#!/usr/bin/env python3
"""Scraper for Evanston American Legion (e-Legion Club) Google Calendar.

Filters out internal/private events (bar schedules, private parties,
board meetings, etc.) to keep only public community events.
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import re
from typing import Any

from lib.ics import IcsScraper

# Patterns indicating internal/private events (case-insensitive)
EXCLUDE_PATTERNS = [
    r'\bbar open\b',
    r'\bbar closed\b',
    r'\bprivate party\b',
    r'\bprivate event\b',
    r'\bprivate lessons?\b',
    r'\bbartender\b',
    r'\bkeg delivery\b',
    r'\bboard meeting\b',
    r'\blegion board\b',
    r'\btemp hold\b',
    r'\btentative\b',
    r'\bcraft setup\b',
    r'\bgraduation\b',
    r'\brehearsal\b',
    r'\bdistrict meeting\b',
]

EXCLUDE_RE = re.compile('|'.join(EXCLUDE_PATTERNS), re.IGNORECASE)


class EvanstonLegionScraper(IcsScraper):
    name = "Evanston American Legion"
    domain = "calendar.google.com"
    ics_url = "https://calendar.google.com/calendar/ical/elegionclub%40gmail.com/public/basic.ics"

    def filter_event(self, event: dict[str, Any]) -> bool:
        title = event.get('title', '')
        return not EXCLUDE_RE.search(title)


if __name__ == '__main__':
    EvanstonLegionScraper.main()
