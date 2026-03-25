#!/usr/bin/env python3
"""
Scraper for OSU Extension Master Gardener events.

Scrapes the event listing page and individual event detail pages from
extension.oregonstate.edu. Filters to a specific program group (e.g. Metro).

Usage:
    python scrapers/osu_extension.py --group metro --name "OSU Extension Master Gardeners" -o osu_extension_mg.ics
"""

import argparse
import logging
import re
import time
from datetime import datetime, date
from typing import Any, Optional
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from scrapers.lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "https://extension.oregonstate.edu"
LISTING_URL = f"{BASE_URL}/program/all/mg/events"


class OSUExtensionScraper(BaseScraper):
    """Scraper for OSU Extension Master Gardener events."""

    name = "OSU Extension"
    domain = "extension.oregonstate.edu"
    timezone = "America/Los_Angeles"

    def __init__(self, group: str, source_name: str):
        self.group = group.lower()
        self.name = source_name
        self.tz = ZoneInfo(self.timezone)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        })
        super().__init__()

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch events from listing page, filter to group, enrich from detail pages."""
        event_urls = self._get_event_urls()
        logger.info(f"Found {len(event_urls)} event URLs for group '{self.group}'")

        events = []
        for url in event_urls:
            event = self._fetch_event_detail(url)
            if event:
                events.append(event)
            time.sleep(0.5)

        return events

    def _get_event_urls(self) -> list[str]:
        """Parse listing page and filter to group-specific event URLs."""
        resp = self.session.get(LISTING_URL, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        urls = []

        # Event links follow pattern: /mg/{group}/events/{slug}
        pattern = f"/mg/{self.group}/events/"
        for link in soup.find_all('a', href=True):
            href = link['href']
            if pattern in href:
                full_url = urljoin(BASE_URL, href)
                if full_url not in urls:
                    urls.append(full_url)

        return urls

    def _fetch_event_detail(self, url: str) -> Optional[dict[str, Any]]:
        """Fetch a single event detail page and extract data."""
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None

        soup = BeautifulSoup(resp.text, 'html.parser')

        # Title from h1
        h1 = soup.find('h1')
        if not h1:
            logger.warning(f"No title found at {url}")
            return None
        title = h1.get_text(strip=True).rstrip('*')

        # Date/time from event-details section
        details_div = soup.find('div', class_='event-details')
        if not details_div:
            logger.warning(f"No event-details found at {url}")
            return None

        date_text = details_div.find('p')
        if not date_text:
            return None

        date_str = date_text.get_text(strip=True)
        dtstart, dtend = self._parse_event_datetime(date_str)
        if not dtstart:
            logger.warning(f"Could not parse date '{date_str}' at {url}")
            return None

        # Location from event-location div
        location = ''
        loc_div = soup.find('div', class_='event-location')
        if loc_div:
            location = loc_div.get_text(strip=True)

        # If no location in div, check the date text for location info
        if not location and 'Online' in date_str:
            location = 'Online'

        # Description from field--name-body (first one in the article)
        description = ''
        article = soup.find('article', class_='event-page')
        if article:
            body = article.find('div', class_='field--name-body')
            if body:
                description = body.get_text(strip=True)

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend or dtstart,
            'url': url,
            'location': location,
            'description': description,
        }

    def _parse_event_datetime(self, text: str) -> tuple[Optional[datetime], Optional[datetime]]:
        """Parse date/time string like 'Mar 25, 2026 12:00 pm - 1:00 pm PDTFREERegister'."""
        # Clean up: remove FREE, Register, accommodation text
        text = re.split(r'FREE|Register|Accommodation', text)[0].strip()

        # Pattern: "Mon DD, YYYY HH:MM am/pm - HH:MM am/pm TZ"
        # or: "Mon DD, YYYY HH:MM am/pm TZ"
        # or: "Mon DD, YYYY"
        match = re.match(
            r'(\w+ \d{1,2}, \d{4})\s+'
            r'(\d{1,2}:\d{2}\s*[ap]m)\s*'
            r'(?:-\s*(\d{1,2}:\d{2}\s*[ap]m)\s*)?'
            r'(P[DS]T|P[DS]T)?',
            text
        )
        if not match:
            # Try date-only
            date_match = re.match(r'(\w+ \d{1,2}, \d{4})', text)
            if date_match:
                try:
                    dt = datetime.strptime(date_match.group(1), '%b %d, %Y')
                    return dt.replace(tzinfo=self.tz), None
                except ValueError:
                    return None, None
            return None, None

        date_str = match.group(1)
        start_time = match.group(2).strip()
        end_time = match.group(3).strip() if match.group(3) else None

        try:
            dtstart = datetime.strptime(f"{date_str} {start_time}", '%b %d, %Y %I:%M %p')
            dtstart = dtstart.replace(tzinfo=self.tz)
        except ValueError:
            return None, None

        dtend = None
        if end_time:
            try:
                dtend = datetime.strptime(f"{date_str} {end_time}", '%b %d, %Y %I:%M %p')
                dtend = dtend.replace(tzinfo=self.tz)
            except ValueError:
                pass

        return dtstart, dtend


def main():
    parser = argparse.ArgumentParser(description='Scrape OSU Extension Master Gardener events')
    parser.add_argument('--group', required=True, help='Program group slug (e.g. metro, marion)')
    parser.add_argument('--name', required=True, help='Source name')
    parser.add_argument('--output', '-o', type=str, help='Output filename')
    args = parser.parse_args()

    scraper = OSUExtensionScraper(args.group, args.name)
    scraper.run(args.output)


if __name__ == '__main__':
    main()
