#!/usr/bin/env python3
"""
Scraper for Northwestern University's PlanIt Purple calendar (Localist).

PlanIt Purple exposes an XML feed at /xmlfeed with parameters for
calendar groups, categories, and date ranges.

Usage:
    python scrapers/planitpurple.py \
        --categories 2,9 \
        --days 60 \
        --output cities/evanston/northwestern.ics

Category IDs:
    2  = Arts/Humanities
    9  = Fitness/Sports
    0  = All categories (or omit --categories)
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import argparse
import html as html_mod
import logging
import re
from datetime import datetime, timezone
from typing import Any
from urllib.request import urlopen, Request
from xml.etree import ElementTree

from lib.base import BaseScraper

logger = logging.getLogger(__name__)

FEED_URL = "https://planitpurple.northwestern.edu/xmlfeed"


class PlanItPurpleScraper(BaseScraper):
    name = "Northwestern University"
    domain = "northwestern.edu"
    timezone = "America/Chicago"

    def __init__(self, categories: str | None = None, days: int = 60,
                 source_name: str | None = None):
        super().__init__()
        self.categories = categories
        self.days = days
        if source_name:
            self.name = source_name

    def fetch_events(self) -> list[dict[str, Any]]:
        params = f"cal=0&days={self.days}"
        if self.categories:
            params += f"&category={self.categories}"
        url = f"{FEED_URL}?{params}"

        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as resp:
            xml_data = resp.read()

        root = ElementTree.fromstring(xml_data)
        events = []

        for item in root.findall('.//event'):
            title = (item.findtext('title') or '').strip()
            if not title:
                continue

            # Parse start/end from unix timestamps
            start_ts = item.findtext('start_datetime')
            end_ts = item.findtext('end_datetime')
            if not start_ts:
                continue

            try:
                dtstart = datetime.fromtimestamp(int(start_ts), tz=timezone.utc)
            except (ValueError, OSError):
                continue

            dtend = None
            if end_ts and end_ts != start_ts:
                try:
                    dtend = datetime.fromtimestamp(int(end_ts), tz=timezone.utc)
                except (ValueError, OSError):
                    pass

            # Build location from address elements
            location_parts = []
            addr = item.find('address')
            if addr is not None:
                building = (addr.findtext('building_name') or '').strip()
                addr1 = (addr.findtext('address_1') or '').strip()
                city = (addr.findtext('city') or '').strip()
                state = (addr.findtext('state') or '').strip()
                if building:
                    location_parts.append(building)
                if addr1:
                    location_parts.append(addr1)
                if city:
                    location_parts.append(f"{city}, {state}" if state else city)

            location = ', '.join(location_parts) if location_parts else None

            # Description: prefer plain text, strip HTML
            desc = item.findtext('description') or ''
            desc = re.sub(r'<[^>]+>', '', desc)
            desc = html_mod.unescape(desc).strip()

            # URL: prefer external URL, fall back to PlanIt Purple URL
            event_url = (item.findtext('externalurl') or '').strip()
            if not event_url:
                event_url = (item.findtext('ppurl') or '').strip()

            event = {
                'title': title,
                'dtstart': dtstart,
                'description': desc if desc else None,
            }
            if dtend:
                event['dtend'] = dtend
            if location:
                event['location'] = location
            if event_url:
                event['url'] = event_url

            events.append(event)

        logger.info("Fetched %d events from PlanIt Purple", len(events))
        return events

    @classmethod
    def parse_args(cls, description=None):
        parser = argparse.ArgumentParser(
            description=description or "Scrape events from Northwestern PlanIt Purple"
        )
        parser.add_argument("--output", "-o", type=str, help="Output filename")
        parser.add_argument("--categories", type=str,
                            help="Comma-separated category IDs (2=Arts, 9=Sports, 0=all)")
        parser.add_argument("--days", type=int, default=60,
                            help="Number of days to fetch (default: 60)")
        parser.add_argument("--name", type=str, default="Northwestern University",
                            help="Source name")
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")
        return parser.parse_args()


if __name__ == "__main__":
    PlanItPurpleScraper.setup_logging()
    args = PlanItPurpleScraper.parse_args()
    scraper = PlanItPurpleScraper(
        categories=args.categories,
        days=args.days,
        source_name=args.name,
    )
    scraper.run(output=args.output)
