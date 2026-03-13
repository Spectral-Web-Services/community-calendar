#!/usr/bin/env python3
"""
Scraper for Knight Center for Journalism in the Americas courses and webinars.
https://journalismcourses.org/course-library/

Scrapes both webinars and online courses from the course library.
Skips "On Demand" courses (no specific dates).

Course cards are Elementor loop items with h2.elementor-heading-title elements:
  - First h2: date text (e.g. "April 13 - May 10, 2026")
  - Second h2: course title
Dates may include Spanish/Portuguese prefixes like "Mesa Redonda | 26 de marzo, 2026".

Usage:
    python scrapers/knight_center.py --output cities/publisher-resources/knight_center.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

from lib.base import BaseScraper

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}

BASE_URL = "https://journalismcourses.org"
CATEGORY_URLS = [
    f"{BASE_URL}/course-library/?e-filter-46fa189-product_cat=webinars",
    f"{BASE_URL}/course-library/?e-filter-46fa189-product_cat=online-courses",
]

# Spanish and Portuguese month names to English
MONTH_TRANSLATIONS = {
    'enero': 'January', 'febrero': 'February', 'marzo': 'March',
    'abril': 'April', 'mayo': 'May', 'junio': 'June',
    'julio': 'July', 'agosto': 'August', 'septiembre': 'September',
    'octubre': 'October', 'noviembre': 'November', 'diciembre': 'December',
    'janeiro': 'January', 'fevereiro': 'February', 'março': 'March',
    'maio': 'May', 'junho': 'June', 'julho': 'July',
    'setembro': 'September', 'outubro': 'October', 'novembro': 'November',
    'dezembro': 'December',
}


class KnightCenterScraper(BaseScraper):
    """Scraper for Knight Center courses and webinars."""

    name = "Knight Center for Journalism"
    domain = "journalismcourses.org"
    timezone = "America/Chicago"

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch events from webinar and online-course category pages."""
        events = []
        seen_urls = set()

        for cat_url in CATEGORY_URLS:
            response = requests.get(cat_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for item in soup.select('[class*="e-loop-item"]'):
                event = self._parse_card(item)
                if event and event['url'] not in seen_urls:
                    seen_urls.add(event['url'])
                    events.append(event)

        # Fetch detail pages in parallel for descriptions
        self._enrich_events(events)

        return events

    def _parse_card(self, item) -> Optional[dict[str, Any]]:
        """Parse a course card from the listing page."""
        headings = item.select('h2.elementor-heading-title')
        if len(headings) < 2:
            return None

        date_text = headings[0].get_text(strip=True)
        title = headings[1].get_text(strip=True)

        if not title or not date_text:
            return None

        # Skip on-demand courses
        if 'on demand' in date_text.lower():
            self.logger.debug(f"Skipping on-demand: {title}")
            return None

        dtstart, dtend = self._parse_date_range(date_text)
        if not dtstart:
            self.logger.debug(f"Could not parse date '{date_text}' for: {title}")
            return None

        # Find link
        link = item.find('a', href=True)
        url = ''
        if link:
            href = link.get('href', '')
            url = href if href.startswith('http') else f"{BASE_URL}{href}"

        self.logger.info(f"Found: {title} on {dtstart.strftime('%Y-%m-%d')}")

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend or dtstart,
            'url': url,
            'description': '',
        }

    def _enrich_events(self, events: list[dict[str, Any]]) -> None:
        """Fetch detail pages to get descriptions."""
        def fetch_description(event):
            url = event.get('url')
            if not url:
                return
            try:
                resp = requests.get(url, headers=HEADERS, timeout=30)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')

                # Try og:description first, fall back to first substantial paragraph
                meta = soup.find('meta', attrs={'property': 'og:description'})
                if meta and meta.get('content'):
                    event['description'] = meta['content'].strip()[:500]
                else:
                    for p in soup.find_all('p'):
                        text = p.get_text(strip=True)
                        if len(text) > 80:
                            event['description'] = text[:500]
                            break
            except Exception as e:
                self.logger.debug(f"Could not fetch details for {url}: {e}")

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fetch_description, e) for e in events]
            for f in as_completed(futures):
                f.result()

    @staticmethod
    def _normalize_date_text(text: str) -> str:
        """Strip prefixes like 'Mesa Redonda |' and translate non-English months."""
        # Remove prefix before pipe (e.g. "Mesa Redonda | 26 de marzo, 2026")
        if '|' in text:
            text = text.split('|', 1)[1].strip()

        # Remove "de" (Spanish/Portuguese connector)
        text = re.sub(r'\bde\b', '', text)

        # Translate month names
        text_lower = text.lower()
        for foreign, english in MONTH_TRANSLATIONS.items():
            if foreign in text_lower:
                text = re.sub(re.escape(foreign), english, text, flags=re.IGNORECASE)
                break

        # Normalize dashes and extra spaces
        text = text.replace('–', '-').replace('—', '-')
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @staticmethod
    def _parse_date_range(text: str) -> tuple:
        """Parse date ranges from the course listings.

        Handles formats like:
        - "April 13 - May 10, 2026"
        - "March 26, 2026"
        - "February 9 – March 8, 2026"
        - "Mesa Redonda | 26 de marzo, 2026"

        Returns (dtstart, dtend) or (None, None).
        """
        text = KnightCenterScraper._normalize_date_text(text)
        if not text:
            return None, None

        # Pattern: "Month D - Month D, Year"
        m = re.match(r'(\w+)\s+(\d+)\s*-\s*(\w+)\s+(\d+),?\s*(\d{4})', text)
        if m:
            month1, day1, month2, day2, year = (
                m.group(1), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
            )
            try:
                dtstart = datetime.strptime(f"{month1} {day1}, {year}", '%B %d, %Y')
                dtend = datetime.strptime(f"{month2} {day2}, {year}", '%B %d, %Y')
                return dtstart, dtend
            except ValueError:
                pass

        # Pattern: "Month D-D, Year" (same month)
        m = re.match(r'(\w+)\s+(\d+)\s*-\s*(\d+),?\s*(\d{4})', text)
        if m:
            month, day1, day2, year = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
            try:
                dtstart = datetime.strptime(f"{month} {day1}, {year}", '%B %d, %Y')
                dtend = datetime.strptime(f"{month} {day2}, {year}", '%B %d, %Y')
                return dtstart, dtend
            except ValueError:
                pass

        # Pattern: "D Month, Year" (day-first, e.g. "26 March, 2026" after translation)
        m = re.match(r'(\d+)\s+(\w+),?\s*(\d{4})', text)
        if m:
            day, month, year = int(m.group(1)), m.group(2), int(m.group(3))
            try:
                dtstart = datetime.strptime(f"{month} {day}, {year}", '%B %d, %Y')
                return dtstart, None
            except ValueError:
                pass

        # Pattern: "Month D, Year" (single day)
        m = re.match(r'(\w+)\s+(\d+),?\s*(\d{4})', text)
        if m:
            month, day, year = m.group(1), int(m.group(2)), int(m.group(3))
            try:
                dtstart = datetime.strptime(f"{month} {day}, {year}", '%B %d, %Y')
                return dtstart, None
            except ValueError:
                pass

        # Pattern without year: "Month D - Month D" (infer year)
        now = datetime.now()
        m = re.match(r'(\w+)\s+(\d+)\s*-\s*(\w+)\s+(\d+)$', text)
        if m:
            month1, day1, month2, day2 = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
            year = now.year
            try:
                dtstart = datetime.strptime(f"{month1} {day1}, {year}", '%B %d, %Y')
                if dtstart.date() < now.date():
                    year += 1
                    dtstart = datetime.strptime(f"{month1} {day1}, {year}", '%B %d, %Y')
                dtend = datetime.strptime(f"{month2} {day2}, {year}", '%B %d, %Y')
                return dtstart, dtend
            except ValueError:
                pass

        # Pattern without year: "Month D" (infer year)
        m = re.match(r'(\w+)\s+(\d+)$', text)
        if m:
            month, day = m.group(1), int(m.group(2))
            year = now.year
            try:
                dtstart = datetime.strptime(f"{month} {day}, {year}", '%B %d, %Y')
                if dtstart.date() < now.date():
                    dtstart = datetime.strptime(f"{month} {day}, {year + 1}", '%B %d, %Y')
                return dtstart, None
            except ValueError:
                pass

        return None, None


if __name__ == '__main__':
    KnightCenterScraper.main()
