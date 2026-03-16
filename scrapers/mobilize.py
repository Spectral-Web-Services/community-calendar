#!/usr/bin/env python3
"""
Scraper for Mobilize.us organization events via their public API.

Usage:
    # By organization slug (looks up ID automatically):
    python scrapers/mobilize.py \
        --org indivisiblesouthcentralindiana \
        --name "Indivisible SCI" \
        --output events.ics

    # By organization ID:
    python scrapers/mobilize.py \
        --org-id 43350 \
        --name "Indivisible SCI" \
        --output events.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import argparse
import json
import logging
import re
from datetime import datetime
from typing import Any, Optional
from urllib.request import urlopen, Request
from zoneinfo import ZoneInfo

from lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE = "https://api.mobilize.us/v1"


class MobilizeScraper(BaseScraper):
    """Scraper for Mobilize.us organization events."""

    domain = "mobilize.us"

    def __init__(self, org_id: int, source_name: str, tz: str = "America/New_York"):
        self.org_id = org_id
        self.name = source_name
        self.timezone = tz
        super().__init__()

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch events from the Mobilize API."""
        url = f"{API_BASE}/events?organization_id={self.org_id}&timeslot_start=gte_now&per_page=100"
        self.logger.info(f"Fetching {url}")

        req = Request(url, headers={
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (compatible; community-calendar/1.0)',
        })
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())

        events = []
        for e in data.get('data', []):
            for parsed in self._parse_event(e):
                events.append(parsed)

        self.logger.info(f"Parsed {len(events)} event timeslots")
        return events

    def _parse_event(self, e: dict) -> list[dict[str, Any]]:
        """Parse a Mobilize event into one event per timeslot."""
        title = e.get('title', 'Untitled')
        url = e.get('browser_url', '')
        description = e.get('description', '')
        image_url = e.get('featured_image_url', '')
        tz_name = e.get('timezone', self.timezone)
        tz = ZoneInfo(tz_name)

        # Location
        loc = e.get('location') or {}
        parts = []
        if loc.get('venue'):
            parts.append(loc['venue'])
        for line in loc.get('address_lines', []):
            if line:
                parts.append(line)
        if loc.get('locality'):
            region = loc.get('region', '')
            parts.append(f"{loc['locality']}, {region}" if region else loc['locality'])
        location = ', '.join(parts)

        if e.get('is_virtual') and not location:
            location = 'Virtual'

        events = []
        for ts in e.get('timeslots', []):
            start_ts = ts.get('start_date')
            end_ts = ts.get('end_date')
            if not start_ts:
                continue

            dtstart = datetime.fromtimestamp(start_ts, tz=tz)
            dtend = datetime.fromtimestamp(end_ts, tz=tz) if end_ts else None

            event = {
                'title': title,
                'dtstart': dtstart,
                'dtend': dtend,
                'url': url,
                'location': location,
                'description': description,
                'uid': f"mobilize-{e['id']}-{ts['id']}@mobilize.us",
            }
            if image_url:
                event['image_url'] = image_url
            events.append(event)

        return events


def resolve_org_id(slug: str) -> int:
    """Look up a Mobilize organization's numeric ID from its slug."""
    url = f"https://www.mobilize.us/{slug}/"
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; community-calendar/1.0)',
    })
    with urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8')
    match = re.search(r'"organization":\s*\{"id":\s*(\d+)', html)
    if not match:
        raise ValueError(f"Could not find organization ID for slug '{slug}'")
    return int(match.group(1))


def main():
    parser = argparse.ArgumentParser(description="Scrape Mobilize.us organization events")
    parser.add_argument('--org', help='Organization slug (e.g., indivisiblesouthcentralindiana)')
    parser.add_argument('--org-id', type=int, help='Organization numeric ID')
    parser.add_argument('--name', default='Mobilize', help='Source name')
    parser.add_argument('--output', '-o', help='Output ICS file')
    parser.add_argument('--timezone', default='America/New_York', help='Timezone')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.org and not args.org_id:
        print("Error: provide --org or --org-id", file=sys.stderr)
        sys.exit(1)

    org_id = args.org_id
    if not org_id:
        logger.info(f"Looking up org ID for slug '{args.org}'")
        org_id = resolve_org_id(args.org)
        logger.info(f"Found org ID: {org_id}")

    scraper = MobilizeScraper(org_id=org_id, source_name=args.name, tz=args.timezone)
    scraper.run(args.output)


if __name__ == '__main__':
    main()
