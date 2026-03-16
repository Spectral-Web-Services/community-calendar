#!/usr/bin/env python3
"""
Scraper for Sidearm Sports v3 athletics calendars.

Uses the /api/v2/Calendar endpoint which returns game data with
opponents, locations, times, and media links.

Usage:
    # All IU sports:
    python scrapers/sidearm.py \
        --base-url https://iuhoosiers.com \
        --name "IU Athletics" \
        --timezone America/Indiana/Indianapolis \
        --output cities/bloomington/iu_athletics.ics

    # Home games only:
    python scrapers/sidearm.py \
        --base-url https://iuhoosiers.com \
        --name "IU Athletics" \
        --home-only \
        --output cities/bloomington/iu_athletics_home.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import argparse
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Optional
from urllib.request import urlopen, Request
from zoneinfo import ZoneInfo

from lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SidearmScraper(BaseScraper):
    """Scraper for Sidearm Sports v3 calendar API."""

    domain = "sidearm"

    def __init__(self, base_url: str, source_name: str, tz: str = "America/New_York",
                 home_only: bool = False):
        self.base_url = base_url.rstrip('/')
        self.name = source_name
        self.domain = base_url.split('/')[2]
        self.timezone = tz
        self.home_only = home_only
        super().__init__()

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch events from the Sidearm calendar API."""
        tz = ZoneInfo(self.timezone)
        now = datetime.now(tz)
        end = now + timedelta(days=180)

        start_str = now.strftime("%-m-%-d-%Y")
        end_str = end.strftime("%-m-%-d-%Y")

        url = f"{self.base_url}/api/v2/Calendar/from/{start_str}/to/{end_str}"
        self.logger.info(f"Fetching {url}")

        req = Request(url, headers={
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (compatible; community-calendar/1.0)',
        })
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())

        events = []
        for day in data:
            for e in day.get('events', []):
                parsed = self._parse_event(e, day.get('date', ''))
                if parsed:
                    events.append(parsed)

        self.logger.info(f"Parsed {len(events)} events")
        return events

    def _parse_event(self, e: dict, day_date: str) -> Optional[dict[str, Any]]:
        """Parse a single game event."""
        opponent = e.get('opponent', {})
        opponent_name = opponent.get('title', '')
        sport_data = e.get('sport', {})
        sport = sport_data.get('title', '') if isinstance(sport_data, dict) else ''
        location_indicator = e.get('locationIndicator', '')

        # Filter home-only if requested
        if self.home_only and location_indicator == 'A':
            return None

        # Skip non-play entries
        if e.get('status') != 'A':
            return None

        # Build title
        at_vs = e.get('atVs', 'vs')
        if sport and opponent_name:
            title = f"IU {sport} {at_vs} {opponent_name}"
        elif sport:
            title = f"IU {sport}"
        elif opponent_name:
            title = f"IU {at_vs} {opponent_name}"
        else:
            return None

        # Parse date/time
        dtstart = self._parse_datetime(day_date, e.get('time', ''))
        if not dtstart:
            return None

        # Location
        location = e.get('location', '')

        # URL
        url = ''
        opponent_website = opponent.get('website', '')
        if location_indicator != 'A' and opponent_website:
            url = opponent_website

        # Image
        image_url = e.get('gameImageUrl', '') or ''

        event = {
            'title': title,
            'dtstart': dtstart,
            'url': url,
            'location': location,
            'description': '',
        }
        if image_url:
            event['image_url'] = image_url
        return event

    def _parse_datetime(self, day_date: str, time_str: str) -> Optional[datetime]:
        """Parse date from API and time string like '7 p.m.'."""
        tz = ZoneInfo(self.timezone)

        # day_date is like "2026-03-16T00:00:00"
        try:
            dt = datetime.fromisoformat(day_date.replace('Z', '+00:00'))
            dt = dt.replace(tzinfo=None)  # treat as local
        except (ValueError, AttributeError):
            return None

        # Parse time like "7 p.m.", "1:05 p.m.", "Noon", "TBA"
        if time_str:
            time_str = time_str.strip().lower()
            if time_str in ('noon', '12 p.m.'):
                dt = dt.replace(hour=12, minute=0)
            elif time_str in ('tba', 'tbd', ''):
                dt = dt.replace(hour=12, minute=0)
            else:
                # "7 p.m." or "1:05 p.m."
                time_str = time_str.replace('.', '').replace(' ', '')
                # Now: "7pm" or "1:05pm"
                try:
                    if ':' in time_str:
                        t = datetime.strptime(time_str, "%I:%M%p")
                    else:
                        t = datetime.strptime(time_str, "%I%p")
                    dt = dt.replace(hour=t.hour, minute=t.minute)
                except ValueError:
                    dt = dt.replace(hour=12, minute=0)

        return dt.replace(tzinfo=tz)


def main():
    parser = argparse.ArgumentParser(description="Scrape Sidearm Sports v3 calendar")
    parser.add_argument('--base-url', required=True, help='Athletics site base URL')
    parser.add_argument('--name', default='Athletics', help='Source name')
    parser.add_argument('--output', '-o', help='Output ICS file')
    parser.add_argument('--timezone', default='America/New_York', help='Timezone')
    parser.add_argument('--home-only', action='store_true', help='Only include home games')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    scraper = SidearmScraper(
        base_url=args.base_url,
        source_name=args.name,
        tz=args.timezone,
        home_only=args.home_only,
    )
    scraper.run(args.output)


if __name__ == '__main__':
    main()
