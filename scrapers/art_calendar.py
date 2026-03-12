#!/usr/bin/env python3
"""
Scraper for American Repertory Theater (A.R.T.) calendar.

A.R.T.'s calendar page embeds a JavaScript `var attendable = {...}` object
containing all calendar instances with dates, titles, and booking URLs.
We extract this JSON and parse it into events.

Usage:
    python scrapers/art_calendar.py -o cities/boston/art.ics
"""

import argparse
import json
import logging
import re
from datetime import datetime, timedelta

import requests
from zoneinfo import ZoneInfo

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from scrapers.lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CALENDAR_URL = 'https://americanrepertorytheater.org/calendar/'
TZ = ZoneInfo('America/New_York')


class ArtCalendarScraper(BaseScraper):
    name = 'American Repertory Theater'
    domain = 'americanrepertorytheater.org'
    timezone = 'America/New_York'

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; CommunityCalendar/1.0)'
        })

    def fetch_events(self):
        """Fetch the calendar page and extract events from embedded JSON."""
        try:
            resp = self.session.get(CALENDAR_URL, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f'Failed to fetch calendar page: {e}')
            return []

        # Extract the attendable JSON object with calendarInstances (there are
        # two var attendable declarations; the first is empty config)
        match = re.search(r'var\s+attendable\s*=\s*(\{"calendarInstances".+?\});\s*\n', resp.text, re.DOTALL)
        if not match:
            logger.error('Could not find attendable JSON in page')
            return []

        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError as e:
            logger.error(f'Failed to parse attendable JSON: {e}')
            return []

        instances = data.get('calendarInstances', [])
        logger.info(f'Found {len(instances)} calendar instances in JSON')

        events = []
        seen = set()
        for inst in instances:
            # Skip draft/non-published entries
            status = inst.get('post_status', '')
            if status == 'draft':
                continue

            # Get the date
            date_str = inst.get('post_date', '')
            if not date_str:
                continue

            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                dt = dt.replace(tzinfo=TZ)
            except ValueError:
                continue

            # Get the parent event info (production title, description)
            parent = inst.get('parent', {})
            title = parent.get('post_title', '')
            if not title:
                title = inst.get('post_title', '')
            if not title:
                continue
            # Strip HTML tags from title
            title = re.sub(r'<[^>]+>', '', title).strip()

            # Skip past events
            if dt < datetime.now(TZ):
                continue

            # Dedup by title + datetime
            key = f'{title}|{dt.isoformat()}'
            if key in seen:
                continue
            seen.add(key)

            # Build booking URL
            booking_url = inst.get('bookingURL', '')
            if not booking_url:
                post_name = parent.get('post_name', '')
                booking_url = f'https://americanrepertorytheater.org/shows-events/{post_name}/' if post_name else CALENDAR_URL

            # Description from excerpt
            excerpt = parent.get('post_excerpt', '')
            # Strip HTML tags from excerpt
            if excerpt:
                excerpt = re.sub(r'<[^>]+>', '', excerpt).strip()

            events.append({
                'title': title,
                'dtstart': dt,
                'dtend': dt + timedelta(hours=2, minutes=30),
                'url': booking_url,
                'location': 'American Repertory Theater, Cambridge, MA',
                'description': excerpt[:500] if excerpt else '',
            })

        logger.info(f'Found {len(events)} upcoming events')
        return events

    @classmethod
    def main(cls):
        cls.setup_logging()
        args = cls.parse_args(description='Scrape A.R.T. calendar')
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        scraper = cls()
        scraper.run(output=args.output)


if __name__ == '__main__':
    ArtCalendarScraper.main()
