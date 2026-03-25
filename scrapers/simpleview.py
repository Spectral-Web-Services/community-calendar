#!/usr/bin/env python3
"""
Scraper for Simpleview CMS event pages (used by tourism/CVB sites).

Fetches event URLs from the RSS feed, then extracts JSON-LD structured
data from each event page.

Usage:
    python scrapers/simpleview.py --url "https://www.visitvancouverwa.com/events/" --name "Visit Vancouver WA" -o visit_vancouver_wa.ics
"""

import argparse
import json
import logging
import re
import time
from datetime import datetime, date
from typing import Any, Optional
from urllib.parse import urlparse, urljoin
from xml.etree import ElementTree
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from scrapers.lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleviewScraper(BaseScraper):
    """Scraper for Simpleview CMS tourism/CVB event pages."""

    name = "Simpleview"
    domain = "simpleview.com"

    def __init__(self, url: str, source_name: str, tz: str = "America/Los_Angeles"):
        parsed = urlparse(url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        self.rss_url = f"{self.base_url}/event/rss/"
        self.name = source_name
        self.domain = parsed.netloc.replace('www.', '')
        self.timezone = tz
        self.tz = ZoneInfo(tz)
        super().__init__()

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch events from RSS, then enrich with JSON-LD from detail pages."""
        event_urls = self._get_event_urls_from_rss()
        logger.info(f"Found {len(event_urls)} event URLs from RSS")

        events = []
        for url in event_urls:
            event = self._fetch_event_jsonld(url)
            if event:
                events.append(event)
            time.sleep(0.5)

        return events

    def _get_event_urls_from_rss(self) -> list[str]:
        """Parse RSS feed to get event detail page URLs."""
        resp = requests.get(self.rss_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        })
        resp.raise_for_status()

        root = ElementTree.fromstring(resp.content)
        urls = []
        for item in root.iter('item'):
            link = item.find('link')
            if link is not None and link.text:
                urls.append(link.text.strip())
        return urls

    def _fetch_event_jsonld(self, url: str) -> Optional[dict[str, Any]]:
        """Fetch a single event page and extract JSON-LD data."""
        try:
            resp = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            })
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None

        soup = BeautifulSoup(resp.text, 'html.parser')

        # Find JSON-LD with Event type
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
            except (json.JSONDecodeError, TypeError):
                continue

            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'Event':
                        return self._parse_jsonld_event(item, url)
            elif isinstance(data, dict) and data.get('@type') == 'Event':
                return self._parse_jsonld_event(data, url)

        logger.warning(f"No JSON-LD Event found at {url}")
        return None

    def _parse_jsonld_event(self, data: dict, url: str) -> Optional[dict[str, Any]]:
        """Parse a JSON-LD Event object into our standard event dict."""
        title = data.get('name')
        if not title:
            return None

        dtstart = self._parse_date(data.get('startDate'))
        if not dtstart:
            logger.warning(f"No parseable startDate for: {title}")
            return None

        dtend = self._parse_date(data.get('endDate'))

        # Build location string
        location = self._build_location(data.get('location'))

        # Description
        description = data.get('description', '')

        # Image
        image_url = data.get('image')
        if isinstance(image_url, list):
            image_url = image_url[0] if image_url else None

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend or dtstart,
            'url': url,
            'location': location,
            'description': description,
            'image_url': image_url,
        }

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse a date string from JSON-LD into a datetime."""
        if not date_str:
            return None

        # Try ISO datetime with timezone
        for fmt in ('%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'):
            try:
                dt = datetime.strptime(date_str, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=self.tz)
                return dt
            except ValueError:
                continue

        return None

    def _build_location(self, location_data: Any) -> str:
        """Build a location string from JSON-LD location object."""
        if not location_data:
            return ''

        if isinstance(location_data, str):
            return location_data

        parts = []
        name = location_data.get('name', '')
        if name:
            parts.append(name)

        address = location_data.get('address')
        if isinstance(address, str):
            parts.append(address)
        elif isinstance(address, dict):
            addr_parts = []
            for field in ('streetAddress', 'addressLocality', 'addressRegion', 'postalCode'):
                val = address.get(field)
                if val:
                    addr_parts.append(val)
            if addr_parts:
                parts.append(', '.join(addr_parts))

        return ', '.join(parts)


def main():
    parser = argparse.ArgumentParser(description='Scrape events from Simpleview CMS sites')
    parser.add_argument('--url', required=True, help='Base events page URL')
    parser.add_argument('--name', required=True, help='Source name')
    parser.add_argument('--timezone', default='America/Los_Angeles', help='Timezone')
    parser.add_argument('--output', '-o', type=str, help='Output filename')
    args = parser.parse_args()

    scraper = SimpleviewScraper(args.url, args.name, args.timezone)
    scraper.run(args.output)


if __name__ == '__main__':
    main()
