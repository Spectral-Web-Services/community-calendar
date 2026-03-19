#!/usr/bin/env python3
"""
Scraper for Steelport Knife Co. events via their Shopify Atom feed.

Event dates, times, and locations are embedded in the blog post body
HTML using bold labels (Date/Time/Location or WHAT/WHEN/WHERE).

Usage:
    python scrapers/steelport.py --output cities/portland/steelport.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Optional
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ATOM_URL = 'https://www.steelportknife.com/blogs/events.atom'
DEFAULT_LOCATION = 'STEELPORT Knife Co., 3602 NE Sandy Blvd Suite B, Portland, OR 97232'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}


class SteelportScraper(BaseScraper):
    """Scraper for Steelport Knife Co. events via Shopify Atom feed."""

    name = "Steelport Knife Co."
    domain = "steelportknife.com"
    timezone = "America/Los_Angeles"

    def fetch_events(self) -> list[dict[str, Any]]:
        req = Request(ATOM_URL, headers=HEADERS)
        try:
            with urlopen(req, timeout=30) as resp:
                xml_content = resp.read().decode('utf-8')
        except (HTTPError, URLError) as e:
            self.logger.error(f"Failed to fetch Atom feed: {e}")
            return []

        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        root = ET.fromstring(xml_content)

        events = []
        for entry in root.findall('atom:entry', ns):
            parsed = self._parse_entry(entry, ns)
            if parsed:
                events.append(parsed)

        return events

    def _parse_entry(self, entry, ns) -> Optional[dict[str, Any]]:
        title_el = entry.find('atom:title', ns)
        content_el = entry.find('atom:content', ns)
        link_el = entry.find('atom:link[@rel="alternate"]', ns)

        if title_el is None or title_el.text is None:
            return None

        raw_title = title_el.text.strip()
        url = link_el.get('href', '') if link_el is not None else ''
        html = content_el.text or '' if content_el is not None else ''

        # Strip HTML tags for plain text
        plain = re.sub(r'<[^>]+>', ' ', html)
        plain = re.sub(r'\s+', ' ', plain).strip()

        # Extract date, time, location from body
        dtstart = self._extract_datetime(raw_title, plain)
        if not dtstart:
            self.logger.warning(f"Could not parse date for: {raw_title}")
            return None

        location = self._extract_location(plain)

        # Clean up title — remove leading date prefix like "Mar 28 - " or "Apr 25th - "
        title = re.sub(r'^[A-Z][a-z]{2}\s+\d{1,2}(?:st|nd|rd|th)?\s*[-–]\s*', '', raw_title).strip()

        # Build description from plain text, skip the structured fields
        description = self._extract_description(plain)

        return {
            'title': title,
            'dtstart': dtstart,
            'url': url,
            'location': location,
            'description': description,
            'uid': f"{hash(raw_title) & 0xffffffff:08x}@steelportknife.com",
        }

    def _extract_datetime(self, title: str, text: str) -> Optional[datetime]:
        """Extract event datetime from title or body text."""
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(self.timezone)
        year = datetime.now().year

        # Try "Date: March 28th" or "WHEN: Wednesday, April 1st, 4pm-6pm"
        date_match = re.search(
            r'(?:Date|WHEN)[:\s]+(?:\w+day,?\s+)?(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?',
            text, re.IGNORECASE
        )
        if not date_match:
            # Try from title: "Mar 28 - ..."
            date_match = re.search(r'^(\w{3,})\s+(\d{1,2})', title)

        if not date_match:
            return None

        month_str = date_match.group(1)
        day = int(date_match.group(2))

        try:
            month = datetime.strptime(month_str[:3], '%b').month
        except ValueError:
            return None

        # If month is in the past, assume next year
        now = datetime.now()
        if month < now.month or (month == now.month and day < now.day):
            year = now.year + 1

        # Try to extract time — handles "11:00 AM", "4pm", "4:30pm"
        time_match = re.search(
            r'(?:Time|WHEN)[:\s]+.*?(\d{1,2})(?::(\d{2}))?\s*(AM|PM)',
            text, re.IGNORECASE
        )
        if not time_match:
            time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(AM|PM)', text, re.IGNORECASE)

        hour, minute = 0, 0
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or '0')
            if time_match.group(3).upper() == 'PM' and hour != 12:
                hour += 12
            elif time_match.group(3).upper() == 'AM' and hour == 12:
                hour = 0

        return datetime(year, month, day, hour, minute, tzinfo=tz)

    def _extract_location(self, text: str) -> str:
        """Extract location from body text."""
        loc_match = re.search(
            r'(?:Location|WHERE)[:\s]+(.+?)(?:\s*(?:Date|Time|WHAT|WHEN|$))',
            text, re.IGNORECASE
        )
        if loc_match:
            loc = loc_match.group(1).strip().rstrip('.')
            if loc:
                return loc
        return DEFAULT_LOCATION

    def _extract_description(self, text: str) -> str:
        """Extract a clean description, removing structured fields."""
        # Remove the structured fields
        desc = re.sub(
            r'(?:Date|Time|Location|Class|WHAT|WHEN|WHERE)[:\s]+[^\n]+',
            '', text, flags=re.IGNORECASE
        )
        desc = re.sub(r'\s+', ' ', desc).strip()
        # Trim if too long
        if len(desc) > 500:
            desc = desc[:497] + '...'
        return desc


if __name__ == '__main__':
    SteelportScraper.setup_logging()
    args = SteelportScraper.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    scraper = SteelportScraper()
    scraper.run(args.output)
