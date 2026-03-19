#!/usr/bin/env python3
"""
Scraper for Travel Portland events via their WordPress REST API.

The API at /wp-json/events/v2/events returns all events in a single
JSON response with full details including dates, venues, and images.

Usage:
    python scrapers/travelportland.py \
        --output cities/portland/travelportland.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import json
import logging
from datetime import datetime
from typing import Any
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_URL = 'https://www.travelportland.com/wp-json/events/v2/events'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
}


class TravelPortlandScraper(BaseScraper):
    """Scraper for Travel Portland events via WP REST API."""

    name = "Travel Portland"
    domain = "travelportland.com"
    timezone = "America/Los_Angeles"

    def fetch_events(self) -> list[dict[str, Any]]:
        req = Request(API_URL, headers=HEADERS)
        try:
            with urlopen(req, timeout=30) as resp:
                raw = json.loads(resp.read().decode('utf-8'))
        except (HTTPError, URLError) as e:
            self.logger.error(f"Failed to fetch API: {e}")
            return []

        data = raw.get('data', {}).get('events', [])
        self.logger.info(f"API returned {len(data)} events")

        events = []
        for item in data:
            parsed = self._parse_event(item)
            if parsed:
                events.extend(parsed)

        return events

    def _parse_event(self, item: dict) -> list[dict[str, Any]]:
        """Parse a Travel Portland event into one or more event dicts.

        Events with multiple instances (recurring) produce one dict per instance.
        """
        title = item.get('title', '').strip()
        if not title:
            return []

        description = item.get('description_short') or item.get('description') or ''
        # Strip HTML tags from description
        import re
        description = re.sub(r'<[^>]+>', '', description).strip()

        location_parts = []
        if item.get('location_name'):
            location_parts.append(item['location_name'])
        if item.get('address'):
            location_parts.append(item['address'])
        location = ', '.join(location_parts)

        # Prefer venue's own page; fall back to Travel Portland's page
        aggregator_url = item.get('url') or ''
        url = item.get('website_url') or item.get('ticket_url') or aggregator_url
        source_urls = {'Travel Portland': aggregator_url} if aggregator_url else {}
        image_url = item.get('featured_image') or ''

        # Price info
        price = item.get('display_price', '')
        if price and description:
            description = f"{description}\n\nPrice: {price}"
        elif price:
            description = f"Price: {price}"

        uid_base = item.get('id') or title

        instances = item.get('event_instances') or []
        if not instances:
            # Fall back to first_date / last_date
            dtstart = self._parse_dt(item.get('first_date'))
            if not dtstart:
                return []
            dtend = self._parse_dt(item.get('last_date')) or dtstart
            return [{
                'title': title,
                'dtstart': dtstart,
                'dtend': dtend,
                'url': url,
                'location': location,
                'description': description,
                'image_url': image_url,
                'source_urls': source_urls,
                'uid': f"{uid_base}@travelportland.com",
            }]

        results = []
        for i, inst in enumerate(instances):
            # Instances are wrapped: {'event_instance': {'start': ..., 'end': ...}}
            inner = inst.get('event_instance', inst)
            dtstart = self._parse_dt(inner.get('start'))
            if not dtstart:
                continue
            dtend = self._parse_dt(inner.get('end')) or dtstart
            uid = f"{uid_base}-{i}@travelportland.com" if len(instances) > 1 else f"{uid_base}@travelportland.com"
            results.append({
                'title': title,
                'dtstart': dtstart,
                'dtend': dtend,
                'url': url,
                'location': location,
                'description': description,
                'image_url': image_url,
                'source_urls': source_urls,
                'uid': uid,
            })

        return results

    def _parse_dt(self, dt_str: str) -> datetime | None:
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str)
        except (ValueError, TypeError):
            self.logger.warning(f"Could not parse datetime: {dt_str}")
            return None


if __name__ == '__main__':
    TravelPortlandScraper.setup_logging()
    args = TravelPortlandScraper.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    scraper = TravelPortlandScraper()
    scraper.run(args.output)
