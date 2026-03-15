#!/usr/bin/env python3
"""Scraper for Old Town School of Folk Music concerts.

Parses the concerts listing page HTML for event data. Each concert
entry has structured markup with date, time, venue, title, and URL.
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

CONCERTS_URL = "https://www.oldtownschool.org/concerts/"


class OldTownSchoolScraper(BaseScraper):
    name = "Old Town School of Folk Music"
    domain = "oldtownschool.org"

    def fetch_events(self) -> list[dict[str, Any]]:
        resp = requests.get(CONCERTS_URL, timeout=30,
                            headers={'User-Agent': 'Mozilla/5.0 (compatible; CommunityCalendar/1.0)'})
        resp.raise_for_status()
        html = resp.text
        if not html:
            return []

        events = []
        # Each concert is in a div.upcoming-event with:
        # <p>Saturday · March 14 2026 · 6:00 PM CDT · Maurer Hall</p>
        # <h3><a href='/concerts/...'>Artist Name</a></h3>
        # <img src='/images/concerts/...' />
        pattern = re.compile(
            r"<div class='upcoming-event[^']*concertListing[^']*'>"
            r"([\s\S]*?)"
            r"(?=<div class='upcoming-event|$)",
            re.DOTALL
        )

        for match in pattern.finditer(html):
            block = match.group(1)
            parsed = self._parse_concert(block)
            if parsed:
                events.append(parsed)

        logger.info(f"Parsed {len(events)} concerts from listing page")
        return events

    def _parse_concert(self, block: str) -> dict[str, Any] | None:
        # Title and URL from <h3><a href='...'>Title</a></h3>
        title_m = re.search(r"<h3[^>]*><a[^>]+href='([^']+)'[^>]*>(.*?)</a>", block)
        if not title_m:
            return None
        url = f"https://www.oldtownschool.org{title_m.group(1)}"
        title = html_mod.unescape(re.sub(r'<[^>]+>', '', title_m.group(2)).strip())

        # Date/time/venue from <p>Day · Month DD YYYY · Time · Venue</p>
        info_m = re.search(r'<p>(.*?)</p>', block)
        if not info_m:
            return None
        info = html_mod.unescape(info_m.group(1))
        # Parse: "Saturday · March 14 2026 · 6:00 PM CDT · Maurer Hall"
        parts = [p.strip() for p in info.split('·')]
        if len(parts) < 3:
            parts = [p.strip() for p in info.split('&middot;')]
        if len(parts) < 3:
            return None

        # parts[0] = day name, parts[1] = date, parts[2] = time, parts[3] = venue
        date_str = parts[1].strip() if len(parts) > 1 else ''
        time_str = parts[2].strip() if len(parts) > 2 else ''
        venue = parts[3].strip() if len(parts) > 3 else 'Old Town School of Folk Music'

        # Remove timezone abbreviation from time
        time_str = re.sub(r'\s+(CDT|CST|CT)\s*$', '', time_str)

        try:
            dtstart = datetime.strptime(f"{date_str} {time_str}", "%B %d %Y %I:%M %p")
        except ValueError:
            try:
                dtstart = datetime.strptime(date_str, "%B %d %Y")
            except ValueError:
                return None

        # Skip past events
        if dtstart.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return None

        # Image
        img_m = re.search(r"<img[^>]+src='([^']+)'", block)
        image_url = f"https://www.oldtownschool.org{img_m.group(1)}" if img_m else ''

        location = f"{venue}, Old Town School of Folk Music, 4544 N Lincoln Ave, Chicago, IL"

        return {
            'title': title,
            'dtstart': dtstart,
            'location': location,
            'url': url,
            'image_url': image_url,
        }


if __name__ == '__main__':
    OldTownSchoolScraper.main()
