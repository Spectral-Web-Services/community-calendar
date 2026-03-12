#!/usr/bin/env python3
"""
Scraper for Multnomah County Library events.

Fetches events from multcolib.org via Drupal Views AJAX endpoint, which returns
JSON with HTML fragments. Paginates through all result pages (20 events per page,
up to 90 pages).

Usage:
    python scrapers/multcolib.py -o multcolib.ics
    python scrapers/multcolib.py --max-pages 5 -o multcolib.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import argparse
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Optional
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

from lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

AJAX_URL = "https://multcolib.org/views/ajax"
BASE_URL = "https://multcolib.org"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json',
}
TZ = ZoneInfo("America/Los_Angeles")
MAX_PAGES = 90
EVENTS_PER_PAGE = 20


class MultcolibScraper(BaseScraper):
    """Scraper for Multnomah County Library events."""

    name = "Multnomah County Library"
    domain = "multcolib.org"
    timezone = "America/Los_Angeles"

    def __init__(self, max_pages: int = MAX_PAGES):
        self.max_pages = max_pages
        super().__init__()

    def _fetch_page(self, page: int) -> Optional[str]:
        """Fetch a single page from the Drupal Views AJAX endpoint.

        The endpoint returns JSON wrapped in a <textarea> tag. The JSON is an
        array of command objects; we extract the one with HTML event data.

        Returns the HTML fragment string, or None on failure.
        """
        import json

        params = {
            'view_name': 'events_list',
            'view_display_id': 'page_1',
            'page': str(page),
        }
        try:
            resp = requests.get(AJAX_URL, params=params, headers=HEADERS, timeout=30)
            if resp.status_code != 200:
                self.logger.warning(f"HTTP {resp.status_code} for page {page}")
                return None

            text = resp.text

            # Drupal wraps the JSON response in <textarea> tags
            textarea_match = re.search(r'<textarea>(.*)</textarea>', text, re.DOTALL)
            if textarea_match:
                text = textarea_match.group(1)

            data = json.loads(text)

            # Response is a JSON array of commands; find the one with HTML data
            for item in data:
                if isinstance(item, dict) and item.get('data'):
                    html = item['data']
                    # Only return items that look like they contain event markup
                    if 'event' in html.lower():
                        return html

            self.logger.warning(f"No HTML data found in JSON response for page {page}")
            return None

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Invalid JSON response for page {page}: {e}")
            return None
        except Exception as e:
            self.logger.warning(f"Failed to fetch page {page}: {e}")
            return None

    def _infer_year(self, month: int, day: int) -> int:
        """Infer the year for a date that only has month and day.

        Assumes events are in the future. If the date has already passed this
        year, assume it's next year.
        """
        now = datetime.now(TZ)
        candidate = datetime(now.year, month, day, tzinfo=TZ)
        # If the date is more than 30 days in the past, assume next year
        if candidate < now - timedelta(days=30):
            return now.year + 1
        return now.year

    def _parse_time_range(self, time_text: str) -> tuple[Optional[tuple[int, int]], Optional[tuple[int, int]]]:
        """Parse a time range string like '10:00 AM - 11:45 AM'.

        Returns ((start_hour, start_min), (end_hour, end_min)) or (None, None).
        """
        time_text = time_text.strip()
        # Match patterns like "10:00 AM - 11:45 AM" or "2:00 PM - 4:00 PM"
        match = re.search(
            r'(\d{1,2}:\d{2})\s*(AM|PM)\s*-\s*(\d{1,2}:\d{2})\s*(AM|PM)',
            time_text,
            re.IGNORECASE,
        )
        if match:
            start_str = f"{match.group(1)} {match.group(2)}"
            end_str = f"{match.group(3)} {match.group(4)}"
            try:
                start_t = datetime.strptime(start_str, "%I:%M %p")
                end_t = datetime.strptime(end_str, "%I:%M %p")
                return (start_t.hour, start_t.minute), (end_t.hour, end_t.minute)
            except ValueError:
                pass

        # Try single time like "10:00 AM"
        match = re.search(r'(\d{1,2}:\d{2})\s*(AM|PM)', time_text, re.IGNORECASE)
        if match:
            try:
                t = datetime.strptime(f"{match.group(1)} {match.group(2)}", "%I:%M %p")
                return (t.hour, t.minute), None
            except ValueError:
                pass

        return None, None

    def _parse_date_text(self, date_text: str) -> Optional[tuple[int, int]]:
        """Parse date text like 'Thu Mar 12' into (month, day).

        Returns (month, day) or None.
        """
        date_text = date_text.strip()
        # Remove day-of-week prefix and any icon artifacts
        # Match "Mon Jan 1" or "Jan 1" patterns
        match = re.search(r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)?\s*([A-Z][a-z]{2})\s+(\d{1,2})', date_text)
        if match:
            month_str = match.group(1)
            day = int(match.group(2))
            try:
                month = datetime.strptime(month_str, "%b").month
                return month, day
            except ValueError:
                pass
        return None

    def _parse_event_card(self, card) -> Optional[dict[str, Any]]:
        """Parse a single event card div into an event dict."""
        # Title and URL
        title_el = card.select_one('.event__title a')
        if not title_el:
            title_el = card.select_one('.event__title')
        if not title_el:
            return None

        title = title_el.get_text(strip=True)
        if not title:
            return None

        href = ""
        link = title_el if title_el.name == 'a' else title_el.find('a')
        if link:
            href = link.get('href', '')

        url = ""
        if href:
            if href.startswith('/'):
                url = f"{BASE_URL}{href}"
            elif href.startswith('http'):
                url = href

        # Date
        date_el = card.select_one('.event__date')
        if not date_el:
            return None

        date_text = date_el.get_text(strip=True)
        parsed_date = self._parse_date_text(date_text)
        if not parsed_date:
            self.logger.debug(f"Could not parse date '{date_text}' for event '{title}'")
            return None

        month, day = parsed_date
        year = self._infer_year(month, day)

        # Time
        start_time = None
        end_time = None
        time_el = card.select_one('.event__time')
        if time_el:
            time_text = time_el.get_text(strip=True)
            start_time, end_time = self._parse_time_range(time_text)

        # Build datetime objects
        try:
            if start_time:
                dtstart = datetime(year, month, day, start_time[0], start_time[1], tzinfo=TZ)
            else:
                dtstart = datetime(year, month, day, tzinfo=TZ)

            if end_time:
                dtend = datetime(year, month, day, end_time[0], end_time[1], tzinfo=TZ)
                # Handle end time crossing midnight (unlikely for library events but safe)
                if dtend <= dtstart:
                    dtend += timedelta(days=1)
            elif start_time:
                # Default to 1 hour duration if only start time is known
                dtend = dtstart + timedelta(hours=1)
            else:
                dtend = None
        except ValueError as e:
            self.logger.debug(f"Invalid date for event '{title}': {e}")
            return None

        # Location
        location = ""
        loc_el = card.select_one('.event__location')
        if loc_el:
            location = loc_el.get_text(strip=True)

        # Description / summary
        description = ""
        summary_el = card.select_one('.event__summary')
        if summary_el:
            description = summary_el.get_text(strip=True)[:500]

        # Image URL
        image_url = ""
        img_el = card.select_one('img')
        if img_el:
            src = img_el.get('src', '')
            if src:
                if src.startswith('/'):
                    image_url = f"{BASE_URL}{src}"
                elif src.startswith('http'):
                    image_url = src

        event = {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend,
            'url': url,
            'location': location,
            'description': description,
        }
        if image_url:
            event['image_url'] = image_url

        return event

    def _parse_html_fragment(self, html: str) -> list[dict[str, Any]]:
        """Parse all event cards from an HTML fragment."""
        soup = BeautifulSoup(html, 'html.parser')
        events = []

        # Each event is in a div with class "event"
        cards = soup.select('div.event')
        if not cards:
            # Fallback: look for the field-content wrappers
            cards = soup.select('div.field-content')

        for card in cards:
            try:
                event = self._parse_event_card(card)
                if event:
                    events.append(event)
            except Exception as e:
                self.logger.debug(f"Error parsing event card: {e}")
                continue

        return events

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch all events by paginating through the AJAX endpoint."""
        all_events = []
        empty_pages = 0

        for page in range(self.max_pages):
            self.logger.info(f"Fetching page {page + 1}/{self.max_pages}...")

            html = self._fetch_page(page)
            if html is None:
                self.logger.info(f"No response for page {page}, stopping.")
                break

            events = self._parse_html_fragment(html)
            if not events:
                empty_pages += 1
                # Allow a couple of empty pages in case of gaps, then stop
                if empty_pages >= 3:
                    self.logger.info(f"Got {empty_pages} consecutive empty pages, stopping.")
                    break
                continue
            else:
                empty_pages = 0

            all_events.extend(events)
            self.logger.info(f"  Got {len(events)} events (total: {len(all_events)})")

        self.logger.info(f"Fetched {len(all_events)} events total from {page + 1} pages")
        return all_events


def main():
    parser = argparse.ArgumentParser(description="Scrape Multnomah County Library events")
    parser.add_argument('--output', '-o', help='Output ICS file')
    parser.add_argument('--max-pages', type=int, default=MAX_PAGES,
                        help=f'Maximum number of pages to fetch (default: {MAX_PAGES})')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    scraper = MultcolibScraper(max_pages=args.max_pages)
    scraper.run(args.output)


if __name__ == '__main__':
    main()
