#!/usr/bin/env python3
"""
Scraper for Sunlight Research events.
https://www.sunlightresearch.net/research-training

Wix-hosted site. The listing page contains event cards as static HTML with
titles, dates, and registration links rendered in document order. Some events
also have dedicated Wix event-detail pages with embedded JSON; for those we
can fetch richer data. But the listing page is the canonical source of what's
currently promoted.

Card structure in document order:
  [TITLE] Event Name
  [TITLE] Day, Month DD, H to H p.m. ET
  [LINK]  Register → URL (event-detail page or Zoom)

Usage:
    python scrapers/sunlight_research.py --output cities/publisher-resources/sunlight_research.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import re
from datetime import datetime
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

from lib.base import BaseScraper

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}

LISTING_URL = "https://www.sunlightresearch.net/research-training"
BASE_URL = "https://www.sunlightresearch.net"

# Matches dates like "Wednesday, March 11, 1 to 2 p.m. ET"
# or "Thursday, Mar. 26, 1 to 2 p.m. ET"
# or "Thursday, March 12, 12 to 1 p.m. ET"
DATE_RE = re.compile(
    r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+'
    r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?)\s+'
    r'(\d{1,2})\s*,?\s+'
    r'(\d{1,2}(?::\d{2})?)\s+to\s+(\d{1,2}(?::\d{2})?)\s+'
    r'([ap]\.?m\.?)\s+(E[SDT]?T)',
    re.IGNORECASE,
)

# Titles that are not events (footer/section headings on the page)
SKIP_TITLES = {
    'Our Impact',
    'Access all our previous trainings',
    'Follow us on YouTube to stay connected',
}


class SunlightResearchScraper(BaseScraper):
    """Scraper for Sunlight Research events."""

    name = "Sunlight Research"
    domain = "sunlightresearch.net"
    timezone = "America/New_York"

    def fetch_events(self) -> list[dict[str, Any]]:
        """Parse the listing page for event cards."""
        response = requests.get(LISTING_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()

        html = response.text
        items = self._extract_items(html)
        return self._group_into_events(items)

    def _extract_items(self, html: str) -> list[tuple[int, str, str]]:
        """Extract titles, dates, and register links in document order.

        Returns list of (position, kind, text) where kind is
        'title', 'date', or 'link'.  Uses regex for position-accurate
        ordering since BeautifulSoup's str() can differ from source HTML.
        """
        items = []

        # h2 elements containing event titles and dates
        for m in re.finditer(
            r'<h2\s+class="font_4[^"]*"[^>]*>(.*?)</h2>', html, re.DOTALL
        ):
            inner = m.group(1)
            text = re.sub(r'<[^>]+>', ' ', inner)
            text = re.sub(r'\s+', ' ', text).strip()
            text = text.replace('\xa0', ' ').replace('&#39;', "'")
            if not text or len(text) < 5:
                continue
            if any(skip in text for skip in SKIP_TITLES):
                continue
            if DATE_RE.search(text):
                items.append((m.start(), 'date', text))
            else:
                items.append((m.start(), 'title', text))

        # Register links (data-testid="linkElement" with aria-label containing Register)
        for m in re.finditer(
            r'<a\b[^>]*data-testid="linkElement"[^>]*>', html
        ):
            tag = m.group(0)
            label_m = re.search(r'aria-label="([^"]*)"', tag)
            href_m = re.search(r'href="([^"]*)"', tag)
            if not label_m or not href_m:
                continue
            if 'egister' not in label_m.group(1):
                continue
            items.append((m.start(), 'link', href_m.group(1)))

        items.sort(key=lambda x: x[0])
        return items

    def _group_into_events(self, items: list[tuple[int, str, str]]) -> list[dict[str, Any]]:
        """Group sequential title → date → link items into events."""
        events = []
        i = 0
        while i < len(items):
            pos, kind, text = items[i]
            if kind != 'title':
                i += 1
                continue

            title = text
            date_text = None
            link = None

            # Look ahead for date and link
            for j in range(i + 1, min(i + 4, len(items))):
                _, next_kind, next_text = items[j]
                if next_kind == 'title':
                    break
                if next_kind == 'date' and not date_text:
                    date_text = next_text
                if next_kind == 'link' and not link:
                    link = next_text

            if not date_text:
                i += 1
                continue

            dtstart, dtend = self._parse_date(date_text)
            if not dtstart:
                self.logger.debug(f"Could not parse date '{date_text}' for: {title}")
                i += 1
                continue

            url = link or LISTING_URL
            self.logger.info(f"Found: {title} on {dtstart.strftime('%Y-%m-%d')}")

            events.append({
                'title': title,
                'dtstart': dtstart,
                'dtend': dtend or dtstart,
                'url': url,
                'location': 'Online',
                'description': '',
            })

            i += 1

        return events

    @staticmethod
    def _parse_date(text: str) -> tuple[Optional[datetime], Optional[datetime]]:
        """Parse date string like 'Wednesday, March 18, 1 to 2 p.m. ET'.

        Returns (dtstart, dtend) or (None, None).
        """
        m = DATE_RE.search(text)
        if not m:
            return None, None

        month_str, day_str, start_time, end_time, ampm, _ = m.groups()

        # Normalize month: "Mar." → "Mar"
        month_str = month_str.rstrip('.')

        now = datetime.now()
        year = now.year

        try:
            # Try full month name first, then abbreviated
            for fmt in ('%B', '%b'):
                try:
                    month = datetime.strptime(month_str, fmt).month
                    break
                except ValueError:
                    continue
            else:
                return None, None

            day = int(day_str)

            # Normalize am/pm
            ampm_clean = ampm.replace('.', '').lower()

            def parse_time(t: str, ampm_str: str) -> tuple[int, int]:
                if ':' in t:
                    h, mn = t.split(':')
                    h, mn = int(h), int(mn)
                else:
                    h, mn = int(t), 0
                if ampm_str == 'pm' and h != 12:
                    h += 12
                elif ampm_str == 'am' and h == 12:
                    h = 0
                return h, mn

            start_h, start_m = parse_time(start_time, ampm_clean)
            end_h, end_m = parse_time(end_time, ampm_clean)

            dtstart = datetime(year, month, day, start_h, start_m)
            dtend = datetime(year, month, day, end_h, end_m)

            # Skip recent past events (< 1 month old) rather than
            # bumping them to next year. Dates without a year on a listing
            # page are almost always current-year.
            if dtstart.date() < now.date():
                return None, None

            return dtstart, dtend

        except (ValueError, TypeError):
            return None, None


if __name__ == '__main__':
    SunlightResearchScraper.main()
