#!/usr/bin/env python3
"""
Scraper for Lenfest Institute events.
https://www.lenfestinstitute.org/get-involved/events/

WordPress site with server-rendered HTML. The listing page has event cards
with h5 titles, short descriptions, and links to detail pages. Dates are
extracted from the detail page content (prose paragraphs with natural-
language dates like "Thursday, April 9" or "May 18-20, 2026").

Usage:
    python scrapers/lenfest_events.py --output cities/publisher-resources/lenfest.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import re
from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

from lib.base import BaseScraper

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}

EVENTS_URL = "https://www.lenfestinstitute.org/get-involved/events/"
BASE_URL = "https://www.lenfestinstitute.org"


class LenfestEventsScraper(BaseScraper):
    """Scraper for Lenfest Institute events."""

    name = "Lenfest Institute"
    domain = "lenfestinstitute.org"
    timezone = "America/New_York"

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch events from the Lenfest events listing page."""
        self.logger.info(f"Fetching events listing: {EVENTS_URL}")
        resp = requests.get(EVENTS_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        events = []

        # Events are listed under h5 headings with links to detail pages
        for h5 in soup.find_all('h5'):
            link = h5.find('a', href=True)
            title = h5.get_text(strip=True)
            if not title:
                continue

            # Get detail page URL
            detail_url = None
            if link:
                href = link['href']
                if href.startswith('/'):
                    detail_url = BASE_URL + href
                elif href.startswith('http'):
                    detail_url = href

            # Also check for a sibling/nearby link if not in the heading
            if not detail_url:
                parent = h5.parent
                if parent:
                    nearby_link = parent.find('a', href=True)
                    if nearby_link:
                        href = nearby_link['href']
                        if href.startswith('/'):
                            detail_url = BASE_URL + href
                        elif href.startswith('http'):
                            detail_url = href

            # Get description from the next paragraph sibling
            description = ''
            for sib in h5.find_next_siblings():
                if sib.name == 'p':
                    description = sib.get_text(strip=True)
                    break
                if sib.name == 'h5':
                    break

            # Try to scrape the detail page for date info
            event = None
            if detail_url:
                event = self._scrape_detail_page(detail_url, title, description)

            # Fall back to extracting date from description text
            if not event:
                event = self._parse_from_description(title, description, detail_url)

            if event:
                events.append(event)

        self.logger.info(f"Found {len(events)} events")
        return events

    def _scrape_detail_page(self, url: str, title: str, listing_desc: str) -> Optional[dict[str, Any]]:
        """Scrape a detail page for date and event info."""
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            self.logger.warning(f"Failed to fetch {url}: {e}")
            return None

        soup = BeautifulSoup(resp.text, 'html.parser')
        tz = ZoneInfo(self.timezone)

        # Use page h1 for title if available
        h1 = soup.find('h1')
        if h1:
            page_title = h1.get_text(strip=True)
            if page_title:
                title = page_title

        # Collect all text content to search for dates
        body = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'entry-content|post-content'))
        if not body:
            body = soup

        text_blocks = [p.get_text(strip=True) for p in body.find_all(['p', 'h2', 'h3', 'h4', 'h5', 'li'])]
        all_text = ' '.join(text_blocks)

        dtstart, dtend = self._extract_dates(all_text, tz)

        if not dtstart:
            return None

        # Extract description from the page
        description = listing_desc
        if not description:
            main_content = soup.find('main') or soup.find('article')
            if main_content:
                paras = main_content.find_all('p')
                description = '\n'.join(p.get_text(strip=True) for p in paras[:3] if p.get_text(strip=True))

        # Find registration link
        reg_url = self._find_registration_link(soup) or url

        self.logger.info(f"Found: {title} on {dtstart.strftime('%Y-%m-%d')}")

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend,
            'url': reg_url,
            'location': self._find_location(all_text),
            'description': description[:2000] if description else '',
        }

    def _extract_dates(self, text: str, tz: ZoneInfo) -> tuple[Optional[datetime], Optional[datetime]]:
        """Extract dates from page text content."""
        current_year = datetime.now().year

        # Try "Month D-D, YYYY" (multi-day range with year)
        m = re.search(r'(\w+)\s+(\d{1,2})\s*[-–—]\s*(\d{1,2}),?\s+(\d{4})', text)
        if m:
            dtstart = self._parse_date(m.group(1), m.group(2), m.group(4), tz)
            dtend = self._parse_date(m.group(1), m.group(3), m.group(4), tz)
            if dtstart:
                return dtstart, dtend

        # Try "Month D, YYYY to Month D, YYYY"
        m = re.search(
            r'(\w+\s+\d{1,2}),?\s+(\d{4})\s*(?:to|through|–|—|-)\s*(\w+\s+\d{1,2}),?\s+(\d{4})',
            text, re.I
        )
        if m:
            dtstart = self._parse_single_date(f"{m.group(1)}, {m.group(2)}", tz)
            dtend = self._parse_single_date(f"{m.group(3)}, {m.group(4)}", tz)
            if dtstart:
                return dtstart, dtend

        # Try "Month D, YYYY" (single date with year)
        m = re.search(r'(\w+)\s+(\d{1,2}),?\s+(\d{4})', text)
        if m:
            dtstart = self._parse_date(m.group(1), m.group(2), m.group(3), tz)
            if dtstart:
                return dtstart, None

        # Try "Day, Month D" without year (assume current or next year)
        m = re.search(r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+(\w+)\.?\s+(\d{1,2})', text, re.I)
        if m:
            month_str = m.group(1)
            day_str = m.group(2)
            # Try current year first, then next year
            for year in [current_year, current_year + 1]:
                dtstart = self._parse_date(month_str, day_str, str(year), tz)
                if dtstart and dtstart >= datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0):
                    return dtstart, None

        return None, None

    def _parse_date(self, month: str, day: str, year: str, tz: ZoneInfo) -> Optional[datetime]:
        """Parse a date from month name/abbreviation, day, and year."""
        # Normalize abbreviated months (e.g., "Feb." -> "Feb")
        month = month.rstrip('.')
        for fmt in ('%B', '%b'):
            try:
                dt = datetime.strptime(f"{month} {day} {year}", f"{fmt} %d %Y")
                return dt.replace(tzinfo=tz)
            except ValueError:
                continue
        return None

    def _parse_single_date(self, text: str, tz: ZoneInfo) -> Optional[datetime]:
        """Parse a single date string like 'April 7, 2026'."""
        text = text.strip().replace(",", ", ").replace("  ", " ").strip(", ")
        for fmt in ("%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y"):
            try:
                dt = datetime.strptime(text, fmt)
                return dt.replace(tzinfo=tz)
            except ValueError:
                continue
        return None

    def _find_location(self, text: str) -> str:
        """Infer location from page text."""
        if re.search(r'\bvirtual\b|\bonline\b|\bzoom\b|\bwebinar\b', text, re.I):
            return 'Virtual'
        # Look for "in City, ST" or "in City" patterns
        m = re.search(r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,?\s+[A-Z]{2})\b', text)
        if m:
            return m.group(1)
        return ''

    def _find_registration_link(self, soup: BeautifulSoup) -> Optional[str]:
        """Find external registration link."""
        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True).lower()
            href = link['href']
            if any(kw in text for kw in ['register', 'sign up', 'rsvp', 'learn more']):
                if href.startswith('http') and self.domain not in href:
                    return href
        return None

    def _parse_from_description(self, title: str, description: str, url: Optional[str]) -> Optional[dict[str, Any]]:
        """Try to extract date from the listing description text."""
        if not description:
            return None
        tz = ZoneInfo(self.timezone)
        dtstart, dtend = self._extract_dates(description, tz)
        if not dtstart:
            return None

        self.logger.info(f"Found (from listing): {title} on {dtstart.strftime('%Y-%m-%d')}")
        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend,
            'url': url or EVENTS_URL,
            'location': self._find_location(description),
            'description': description[:2000],
        }


if __name__ == '__main__':
    LenfestEventsScraper.main()
