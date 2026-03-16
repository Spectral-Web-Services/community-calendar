#!/usr/bin/env python3
"""
Scraper for Monroe Convention Center (Bloomington, IN) events.
https://www.bloomingtonconvention.com/calendar/

Uses RSS feed at https://www.bloomingtonconvention.com/event/rss/
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import re
from html import unescape
from typing import Any, Optional

from bs4 import BeautifulSoup

from lib.rss import RssScraper


class BloomingtonConventionScraper(RssScraper):
    """Scraper for Monroe Convention Center events."""

    name = "Monroe Convention Center"
    domain = "bloomingtonconvention.com"
    rss_url = "https://www.bloomingtonconvention.com/event/rss/"
    timezone = "America/Indiana/Indianapolis"

    def parse_entry(self, entry: dict) -> Optional[dict[str, Any]]:
        """Parse a single RSS entry into event data."""
        dt_start = self.parse_rss_date(entry)
        if not dt_start:
            return None

        title = entry.get('title', '').strip()
        if not title:
            return None

        # Extract description text and image
        description_html = entry.get('description', '')
        description = self._clean_description(description_html)
        image_url = self._extract_image(description_html)

        event = {
            'title': title,
            'dtstart': dt_start,
            'url': entry.get('link', ''),
            'location': 'Monroe Convention Center, 302 S College Ave, Bloomington, IN',
            'description': description,
        }
        if image_url:
            event['image_url'] = image_url
        return event

    def _clean_description(self, description_html: str) -> str:
        """Clean HTML description for display."""
        if not description_html:
            return ''

        soup = BeautifulSoup(description_html, 'html.parser')
        # Remove img tags
        for img in soup.find_all('img'):
            img.decompose()
        text = unescape(soup.get_text(' ', strip=True))
        # Remove date prefix patterns like "04/23/2026 to 04/23/2026 -"
        text = re.sub(r'^[\d/\s\-to]+\s*-\s*', '', text).strip()
        text = re.sub(r'^Starting\s+[\d/]+\s*-?\s*', '', text).strip()
        text = re.sub(r'\s+', ' ', text)

        if len(text) > 500:
            text = text[:500] + '...'
        return text

    def _extract_image(self, description_html: str) -> Optional[str]:
        """Extract image URL from the description HTML."""
        if not description_html:
            return None
        soup = BeautifulSoup(description_html, 'html.parser')
        img = soup.find('img')
        if img and img.get('src'):
            return img['src']
        return None


if __name__ == '__main__':
    BloomingtonConventionScraper.main()
