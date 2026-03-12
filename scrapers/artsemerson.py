#!/usr/bin/env python3
"""
Scraper for ArtsEmerson events via WordPress Tribe Events REST API.

The ICS feed at artsemerson.org/events/?ical=1 is broken (returns only 1
event), but the Tribe Events REST API works and returns all performances.

Usage:
    python scrapers/artsemerson.py -o cities/boston/artsemerson.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from datetime import datetime
from typing import Any

import requests
from scrapers.lib.base import BaseScraper
from scrapers.lib.utils import DEFAULT_HEADERS


class ArtsEmersonScraper(BaseScraper):
    name = "ArtsEmerson"
    domain = "artsemerson.org"
    timezone = "America/New_York"

    API_URL = "https://artsemerson.org/wp-json/tribe/events/v1/events"

    def fetch_events(self) -> list[dict[str, Any]]:
        events = []
        page = 1
        while True:
            params = {'per_page': 50, 'page': page}
            self.logger.info(f"Fetching page {page}")
            resp = requests.get(self.API_URL, params=params, headers=DEFAULT_HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            for item in data.get('events', []):
                title = item.get('title', '').strip()
                if not title:
                    continue

                try:
                    dtstart = datetime.strptime(item['start_date'], '%Y-%m-%d %H:%M:%S')
                    dtend = datetime.strptime(item['end_date'], '%Y-%m-%d %H:%M:%S')
                except (KeyError, ValueError):
                    continue

                venue = item.get('venue', {})
                location = venue.get('venue', '')
                if venue.get('address'):
                    location += f", {venue['address']}"
                if venue.get('city'):
                    location += f", {venue['city']}"
                if venue.get('state'):
                    location += f", {venue['state']}"

                url = item.get('url', '')
                description = item.get('description', '')
                # Strip HTML
                import re
                description = re.sub(r'<[^>]+>', '', description).strip()[:500]

                image = item.get('image')
                image_url = image.get('url', '') if isinstance(image, dict) else ''

                events.append({
                    'title': title,
                    'dtstart': dtstart,
                    'dtend': dtend,
                    'url': url,
                    'location': location,
                    'description': description,
                    'image_url': image_url,
                })

            if page >= data.get('total_pages', 1):
                break
            page += 1

        return events

    @classmethod
    def main(cls):
        cls.setup_logging()
        args = cls.parse_args()
        if args.debug:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
        scraper = cls()
        scraper.run(output=args.output)


if __name__ == '__main__':
    ArtsEmersonScraper.main()
