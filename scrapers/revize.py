#!/usr/bin/env python3
"""
Scraper for Revize CMS calendars.

Revize CMS exposes calendar data as JSON via a PHP endpoint.
This scraper fetches that JSON and converts it to ICS format.

Usage:
    python scrapers/revize.py \
        --webspace evanstonil \
        --name "City of Evanston" \
        --output cities/evanston/city_of_evanston.ics

    # Filter to specific calendar categories:
    python scrapers/revize.py \
        --webspace evanstonil \
        --name "City of Evanston" \
        --categories "Events" \
        --output cities/evanston/city_of_evanston_events.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import argparse
import json
import logging
from datetime import datetime
from typing import Any
from urllib.parse import quote, unquote
from urllib.request import urlopen, Request

from lib.base import BaseScraper

logger = logging.getLogger(__name__)

DATA_URL = "https://{host}/_assets_/plugins/revizeCalendar/calendar_data_handler.php?webspace={webspace}&relative_revize_url=https://cms6.revize.com/revize/{webspace}&protocol=https"


class RevizeScraper(BaseScraper):
    name = "Revize Calendar"
    domain = "revize.com"
    timezone = "America/Chicago"

    def __init__(self, webspace: str, host: str | None = None,
                 categories: list[str] | None = None,
                 source_name: str | None = None):
        super().__init__()
        self.webspace = webspace
        self.host = host
        self.categories = categories
        if source_name:
            self.name = source_name

    def fetch_events(self) -> list[dict[str, Any]]:
        host = self.host or f"{self.webspace.replace('il', '')}.org"
        # Try common host patterns
        hosts_to_try = [self.host] if self.host else [
            f"cityof{self.webspace.replace('il', '')}.org",
            f"www.cityof{self.webspace.replace('il', '')}.org",
        ]

        data = None
        for h in hosts_to_try:
            url = DATA_URL.format(host=h, webspace=self.webspace)
            try:
                req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read())
                logger.info("Fetched %d events from %s", len(data), h)
                break
            except Exception as e:
                logger.debug("Failed to fetch from %s: %s", h, e)
                continue

        if not data:
            logger.error("Could not fetch calendar data for webspace: %s", self.webspace)
            return []

        events = []
        for item in data:
            title = item.get("title", "").strip()
            if not title:
                continue

            cat = item.get("primary_calendar_name", "")
            if self.categories and cat not in self.categories:
                continue

            start_str = item.get("start", "")
            end_str = item.get("end", "")
            if not start_str:
                continue

            try:
                dtstart = datetime.fromisoformat(start_str)
            except ValueError:
                continue

            if dtstart < datetime.now():
                continue

            dtend = None
            if end_str:
                try:
                    dtend = datetime.fromisoformat(end_str)
                except ValueError:
                    pass

            desc = unquote(item.get("desc", ""))
            # Strip HTML tags and decode entities
            import re
            import html as html_mod
            desc = re.sub(r'<[^>]+>', '', desc)
            desc = html_mod.unescape(desc).strip()

            location = item.get("location", "").strip()
            event_url = item.get("url", "").strip()

            event = {
                "title": title,
                "dtstart": dtstart,
                "description": desc if desc else None,
            }
            if dtend:
                event["dtend"] = dtend
            if location:
                event["location"] = location
            if event_url:
                event["url"] = event_url

            events.append(event)

        return events

    @classmethod
    def parse_args(cls, description=None):
        parser = argparse.ArgumentParser(
            description=description or "Scrape events from a Revize CMS calendar"
        )
        parser.add_argument("--output", "-o", type=str, help="Output filename")
        parser.add_argument("--webspace", required=True, help="Revize webspace ID (e.g. evanstonil)")
        parser.add_argument("--host", type=str, help="Website hostname (e.g. cityofevanston.org)")
        parser.add_argument("--name", type=str, default="Revize Calendar", help="Source name")
        parser.add_argument("--categories", type=str, help="Comma-separated calendar categories to include (e.g. 'Events,Meetings')")
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")
        return parser.parse_args()


if __name__ == "__main__":
    RevizeScraper.setup_logging()
    args = RevizeScraper.parse_args()
    categories = [c.strip() for c in args.categories.split(",")] if args.categories else None
    scraper = RevizeScraper(
        webspace=args.webspace,
        host=args.host,
        categories=categories,
        source_name=args.name,
    )
    scraper.run(output=args.output)
