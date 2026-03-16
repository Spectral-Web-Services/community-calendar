#!/usr/bin/env python3
"""
Scraper for CampusLabs / beINvolved event platforms.

Uses the public discovery API to fetch events with images, which the raw
ICS feed does not include.

Usage:
    python scrapers/campuslabs.py \
        --base-url "https://iub.campuslabs.com/engage" \
        --name "IU beINvolved Student Orgs" \
        --timezone America/Indiana/Indianapolis \
        -o cities/bloomington/iu_campuslabs.ics

    python scrapers/campuslabs.py \
        --base-url "https://montclair.campuslabs.com/engage" \
        --name "Montclair Engage Events" \
        --timezone America/New_York \
        -o cities/montclair/montclair_engage_events_ics.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import argparse
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

IMAGE_BASE = "https://se-images.campuslabs.com/clink/images/"
PAGE_SIZE = 100


class CampusLabsScraper(BaseScraper):
    """Scraper for CampusLabs/beINvolved event discovery API."""

    domain = "campuslabs.com"

    def __init__(self, base_url: str, source_name: str, tz: str):
        self.base_url = base_url.rstrip('/')
        self.name = source_name
        self.timezone = tz
        super().__init__()

    def _fetch_json(self, url: str) -> Optional[dict]:
        """Fetch a URL and return parsed JSON."""
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except (HTTPError, URLError, json.JSONDecodeError) as e:
            self.logger.warning(f"Failed to fetch {url}: {e}")
            return None

    def _event_image_url(self, event: dict) -> str:
        """Return the best available image URL for an event."""
        if event.get('imagePath'):
            return IMAGE_BASE + event['imagePath']
        if event.get('organizationProfilePicture'):
            return IMAGE_BASE + event['organizationProfilePicture']
        return ''

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch all upcoming events from the CampusLabs discovery API."""
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        api_base = (
            f"{self.base_url}/api/discovery/event/search"
            f"?orderByField=endsOn&orderByDirection=ascending"
            f"&status=Approved&take={PAGE_SIZE}"
            f"&startsAfter={now}"
        )

        events = []
        skip = 0

        while True:
            url = f"{api_base}&skip={skip}"
            self.logger.info(f"Fetching events (skip={skip})...")
            data = self._fetch_json(url)
            if not data or 'value' not in data:
                break

            items = data['value']
            if not items:
                break

            for item in items:
                parsed = self._parse_event(item)
                if parsed:
                    events.append(parsed)

            # CampusLabs returns @odata.count or we just check if we got a full page
            if len(items) < PAGE_SIZE:
                break
            skip += PAGE_SIZE

        self.logger.info(f"Fetched {len(events)} events total")
        return events

    def _parse_event(self, item: dict) -> Optional[dict[str, Any]]:
        """Parse a single event from the API response."""
        name = item.get('name', '').strip()
        if not name:
            return None

        start_str = item.get('startsOn', '')
        if not start_str:
            return None

        try:
            dtstart = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        except ValueError:
            return None

        dtend = None
        end_str = item.get('endsOn', '')
        if end_str:
            try:
                dtend = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            except ValueError:
                pass

        # Build description from HTML description + org name
        desc = item.get('description', '') or ''
        # Strip HTML tags
        desc = re.sub(r'<[^>]+>', ' ', desc).strip()
        desc = re.sub(r'\s+', ' ', desc)

        org_name = item.get('organizationName', '')
        if org_name:
            desc = f"Hosted by: {org_name}\n\n{desc}" if desc else f"Hosted by: {org_name}"

        event_id = item.get('id', '')
        event_url = f"{self.base_url}/event/{event_id}" if event_id else ''

        location = item.get('location', '') or ''

        return {
            'title': name,
            'dtstart': dtstart,
            'dtend': dtend,
            'location': location,
            'description': desc[:1000] if desc else '',
            'url': event_url,
            'image_url': self._event_image_url(item),
            'uid': event_url,
        }


def main():
    parser = argparse.ArgumentParser(description="Scrape CampusLabs/beINvolved events via API")
    parser.add_argument('--base-url', required=True,
                        help='Base engage URL (e.g. https://iub.campuslabs.com/engage)')
    parser.add_argument('--name', required=True, help='Source name')
    parser.add_argument('--timezone', default='America/New_York', help='Timezone')
    parser.add_argument('--output', '-o', help='Output ICS file')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    scraper = CampusLabsScraper(
        base_url=args.base_url,
        source_name=args.name,
        tz=args.timezone,
    )
    scraper.run(args.output)


if __name__ == '__main__':
    main()
