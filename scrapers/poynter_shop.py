#!/usr/bin/env python3
"""
Scraper for Poynter Institute training courses (shop/catalog).
https://www.poynter.org/shop/

This is separate from the Poynter events ICS feed (/events/?ical=1).
The shop page lists paid/free courses and workshops with structured
WooCommerce HTML. Self-paced courses without dates are skipped.

Usage:
    python scrapers/poynter_shop.py --output cities/publisher-resources/poynter_shop.ics
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

SHOP_URL = "https://www.poynter.org/shop/"


class PoynterShopScraper(BaseScraper):
    """Scraper for Poynter Institute training catalog."""

    name = "Poynter Institute Training"
    domain = "poynter.org"
    timezone = "America/New_York"

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch courses from the Poynter shop page."""
        response = requests.get(SHOP_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        events = []
        seen = set()

        for product in soup.select('li.product'):
            event = self._parse_product(product)
            if not event:
                continue
            # Deduplicate by title + start date
            key = (event['title'], event['dtstart'])
            if key in seen:
                continue
            seen.add(key)
            events.append(event)

        return events

    def _parse_product(self, product) -> Optional[dict[str, Any]]:
        """Parse a single product card into an event dict."""
        # Title
        title_el = product.select_one('.woocommerce-loop-product__title')
        if not title_el:
            return None
        title = title_el.get_text(strip=True)

        # Dates — skip self-paced courses without dates
        start_el = product.select_one('.course-datetime__start-date')
        if not start_el:
            return None
        dtstart = self._parse_date(start_el.get_text(strip=True))
        if not dtstart:
            return None

        # Skip past events
        if dtstart.date() < datetime.now().date():
            return None

        end_el = product.select_one('.course-datetime__end-date')
        dtend = None
        if end_el:
            end_text = end_el.get_text(strip=True).lstrip('–—- ')
            dtend = self._parse_date(end_text)

        # URL
        link = product.select_one('a.woocommerce-LoopProduct-link')
        url = link['href'] if link and link.get('href') else SHOP_URL

        # Location
        loc_el = product.select_one('.product__location')
        location = loc_el.get_text(strip=True) if loc_el else 'Online'

        # Instructor(s)
        instructors = [el.get_text(strip=True)
                       for el in product.select('.instructor__name')]
        description = f"Instructor(s): {', '.join(instructors)}" if instructors else ''

        self.logger.info(f"Found: {title} on {dtstart.strftime('%Y-%m-%d')}")

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend or dtstart,
            'url': url,
            'location': location,
            'description': description,
        }

    @staticmethod
    def _parse_date(text: str) -> Optional[datetime]:
        """Parse date like 'May 18, 2026' or 'March 12, 2026'."""
        text = text.strip()
        for fmt in ('%B %d, %Y', '%b %d, %Y', '%b. %d, %Y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        return None


if __name__ == '__main__':
    PoynterShopScraper.main()
