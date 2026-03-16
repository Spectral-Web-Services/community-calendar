#!/usr/bin/env python3
"""
Scraper for Visit Bloomington events (Simpleview CMS).

Uses the public REST API to fetch events with images, descriptions,
and venue information from visitbloomington.com.

Usage:
    python scrapers/visitbloomington.py -o cities/bloomington/visitbloomington.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import quote
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE = "https://www.visitbloomington.com/includes/rest_v2/plugins_events_events_by_date/find/"
TOKEN = "04143a6fe9ad86b445613f3fb3d88171"
SITE_BASE = "https://www.visitbloomington.com"

# All event category IDs from the site
ALL_CATEGORIES = ["42", "26", "25", "29", "32", "23", "27", "37", "28", "22", "24", "43"]

PAGE_SIZE = 100


class VisitBloomingtonScraper(BaseScraper):
    """Scraper for Visit Bloomington events via Simpleview REST API."""

    name = "Visit Bloomington"
    domain = "visitbloomington.com"
    timezone = "America/Indiana/Indianapolis"

    def _build_api_url(self, start: str, end: str, limit: int, skip: int) -> str:
        """Build the API URL with the JSON query parameter."""
        query = {
            "filter": {
                "active": True,
                "$and": [
                    {"categories.catId": {"$in": ALL_CATEGORIES}}
                ],
                "date_range": {
                    "start": {"$date": start},
                    "end": {"$date": end},
                },
            },
            "options": {
                "limit": limit,
                "skip": skip,
                "count": True,
                "castDocs": False,
                "fields": {
                    "_id": 1, "location": 1, "date": 1, "startDate": 1,
                    "endDate": 1, "recurrence": 1, "recurType": 1,
                    "media_raw": 1, "recid": 1, "title": 1, "url": 1,
                    "categories": 1, "description": 1, "city": 1,
                    "listing.title": 1,
                },
                "hooks": [],
                "sort": {"date": 1, "rank": 1, "title_sort": 1},
            },
        }
        json_str = json.dumps(query, separators=(',', ':'))
        return f"{API_BASE}?json={quote(json_str)}&token={TOKEN}"

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
            self.logger.warning(f"Failed to fetch API: {e}")
            return None

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch all upcoming events from Visit Bloomington."""
        now = datetime.now(timezone.utc)
        start = now.strftime('%Y-%m-%dT04:00:00.000Z')
        # Fetch up to 6 months ahead
        from datetime import timedelta
        end_dt = now + timedelta(days=self.months_ahead * 31)
        end = end_dt.strftime('%Y-%m-%dT04:00:00.000Z')

        events = []
        skip = 0

        while True:
            url = self._build_api_url(start, end, PAGE_SIZE, skip)
            self.logger.info(f"Fetching events (skip={skip})...")
            data = self._fetch_json(url)

            if not data or 'docs' not in data:
                break

            docs_wrapper = data['docs']
            items = docs_wrapper.get('docs', [])
            total = docs_wrapper.get('count', 0)

            if not items:
                break

            for item in items:
                parsed = self._parse_event(item)
                if parsed:
                    events.append(parsed)

            skip += PAGE_SIZE
            if skip >= total:
                break

        self.logger.info(f"Fetched {len(events)} events total")
        return events

    def _parse_event(self, item: dict) -> Optional[dict[str, Any]]:
        """Parse a single event from the API response."""
        title = item.get('title', '').strip()
        if not title:
            return None

        # Parse dates
        start_str = item.get('startDate') or item.get('date', '')
        if not start_str:
            return None

        try:
            dtstart = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        except ValueError:
            return None

        dtend = None
        end_str = item.get('endDate', '')
        if end_str:
            try:
                dtend = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            except ValueError:
                pass

        # Location
        location = item.get('location', '') or ''

        # Description
        desc = item.get('description', '') or ''
        desc = re.sub(r'<[^>]+>', ' ', desc).strip()
        desc = re.sub(r'\s+', ' ', desc)

        # URL
        event_url = ''
        if item.get('url'):
            event_url = SITE_BASE + item['url']

        # Image from media_raw
        image_url = ''
        media = item.get('media_raw') or []
        for m in media:
            if m.get('mediatype') == 'Image' and m.get('mediaurl'):
                image_url = m['mediaurl']
                break

        # UID from recid
        recid = item.get('recid', '')
        uid = f"event-{recid}@visitbloomington.com" if recid else ''

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend,
            'location': location,
            'description': desc[:500] if desc else '',
            'url': event_url,
            'image_url': image_url,
            'uid': uid,
        }


def main():
    parser = VisitBloomingtonScraper.parse_args("Scrape Visit Bloomington events")
    if parser.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    scraper = VisitBloomingtonScraper()
    scraper.run(parser.output)


if __name__ == '__main__':
    main()
