#!/usr/bin/env python3
"""
Scraper for Boston University College of Fine Arts calendar.

The BU CFA calendar is a WordPress site with date-filtered listing pages.
Events are organized by date headers (h3.calendar-list-event-date) with
time spans and title divs as siblings. We parse the listing page directly
and optionally enrich from detail pages.

Usage:
    python scrapers/bu_cfa.py --topic 8637 --name "BU School of Theatre" -o cities/boston/bu_theatre.ics
"""

import argparse
import logging
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from scrapers.lib.base import BaseScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = 'https://www.bu.edu/cfa/news/calendar/'
TZ = ZoneInfo('America/New_York')


class BuCfaScraper(BaseScraper):
    name = 'BU College of Fine Arts'
    domain = 'bu.edu'
    timezone = 'America/New_York'

    def __init__(self, topic=None):
        super().__init__()
        self.topic = topic
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; CommunityCalendar/1.0)'
        })

    def fetch_events(self):
        """Fetch events by paginating month-by-month through the listing."""
        events = []
        seen_keys = set()
        now = datetime.now(TZ)
        year = now.year

        for month_offset in range(5):
            dt = now + timedelta(days=month_offset * 30)
            date_param = dt.strftime('%Y%m01')
            params = {'date': date_param}
            if self.topic:
                params['topic'] = self.topic

            try:
                resp = self.session.get(BASE_URL, params=params, timeout=15)
                resp.raise_for_status()
            except Exception as e:
                logger.warning(f'Failed to fetch listing for {date_param}: {e}')
                continue

            page_events = self._parse_listing(resp.text, year)
            for ev in page_events:
                key = f"{ev['title']}|{ev['dtstart'].isoformat()}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    events.append(ev)

        logger.info(f'Found {len(events)} events from listing pages')

        # Enrich events with detail page data (description, image, location)
        for ev in events:
            if ev.get('detail_url'):
                self._enrich_from_detail(ev)

        return events

    def _parse_listing(self, html, year):
        """Parse the listing page HTML into event dicts."""
        soup = BeautifulSoup(html, 'html.parser')
        events = []

        current_date_str = None
        current_time_str = None

        # Walk through all elements inside the calendar list article
        article = soup.find('article', class_='calendar-list')
        if not article:
            return events

        for el in article.descendants:
            if not hasattr(el, 'get'):
                continue

            classes = el.get('class', [])

            # Date header: "Thursday, April 9"
            if el.name == 'h3' and 'calendar-list-event-date' in classes:
                current_date_str = el.get_text(strip=True)
                current_time_str = None  # reset time for new date

            # Time: "7:30 PM"
            elif el.name == 'span' and 'calendar-list-event-time' in classes:
                current_time_str = el.get_text(strip=True)

            # Event title + link
            elif el.name == 'div' and 'calendar-list-event-link' in classes:
                title_text = None
                detail_url = None

                # Title is in the text content, link is in an <a> child
                for child in el.children:
                    if hasattr(child, 'name') and child.name == 'a':
                        href = child.get('href', '')
                        if 'eid=' in href:
                            detail_url = href
                    elif hasattr(child, 'strip'):
                        t = child.strip()
                        if t:
                            title_text = t

                # Also check direct text
                if not title_text:
                    # Get text excluding the "Details" link
                    texts = [c.strip() for c in el.stripped_strings if c.strip() != 'Details']
                    title_text = texts[0] if texts else None

                if not title_text or not current_date_str:
                    continue

                dtstart = self._parse_date_time(current_date_str, current_time_str, year)
                if not dtstart:
                    continue

                events.append({
                    'title': title_text,
                    'dtstart': dtstart,
                    'dtend': dtstart + timedelta(hours=2),
                    'url': detail_url or BASE_URL,
                    'detail_url': detail_url,
                    'location': 'Boston University, Boston, MA',
                })

        return events

    def _parse_date_time(self, date_str, time_str, year):
        """Parse 'Thursday, April 9' + '7:30 PM' into a datetime."""
        # Strip day-of-week prefix
        date_str = re.sub(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s*', '', date_str)

        # Try parsing "April 9" with the year
        for fmt in ('%B %d', '%b %d'):
            try:
                dt = datetime.strptime(f'{date_str} {year}', f'{fmt} %Y')
                break
            except ValueError:
                continue
        else:
            return None

        # Add time
        if time_str:
            time_str = time_str.strip().upper()
            m = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str)
            if m:
                hour, minute, ampm = int(m.group(1)), int(m.group(2)), m.group(3)
                if ampm == 'PM' and hour != 12:
                    hour += 12
                elif ampm == 'AM' and hour == 12:
                    hour = 0
                dt = dt.replace(hour=hour, minute=minute)
            else:
                dt = dt.replace(hour=19, minute=30)  # default 7:30 PM
        else:
            dt = dt.replace(hour=19, minute=30)  # default 7:30 PM

        return dt.replace(tzinfo=TZ)

    def _enrich_from_detail(self, event):
        """Fetch the detail page and add description, image, location."""
        url = event['detail_url']
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
        except Exception:
            return

        soup = BeautifulSoup(resp.text, 'html.parser')

        # Image
        img = soup.find('img', src=re.compile(r'/cfa/files/'))
        if img:
            src = img.get('src', '')
            event['image_url'] = f'https://www.bu.edu{src}' if src.startswith('/') else src

        # Location — look for venue info
        for el in soup.find_all(['p', 'div', 'span']):
            text = el.get_text(strip=True)
            if 'Commonwealth Ave' in text and len(text) < 200:
                event['location'] = text
                break

        # Description
        # Look for the main content area after the title
        content = soup.find('div', class_=re.compile(r'entry-content|event-content'))
        if content:
            desc = content.get_text(separator=' ', strip=True)[:500]
            event['description'] = desc
        else:
            # Try paragraphs after the event title
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 50 and 'Commonwealth' not in text and 'experience the arts' not in text.lower():
                    event['description'] = text[:500]
                    break

        # Ticket URL
        ticket_link = soup.find('a', href=re.compile(r'ovationtix\.com|ticketmaster'))
        if ticket_link:
            event['url'] = ticket_link.get('href')

    @classmethod
    def parse_args(cls, description=None):
        parser = argparse.ArgumentParser(description=description or 'Scrape BU CFA calendar')
        parser.add_argument('--output', '-o', type=str, help='Output filename')
        parser.add_argument('--topic', type=str, help='Topic ID filter (e.g., 8637 for Theatre)')
        parser.add_argument('--name', type=str, help='Source name override')
        parser.add_argument('--debug', action='store_true', help='Enable debug logging')
        return parser.parse_args()

    @classmethod
    def main(cls):
        cls.setup_logging()
        args = cls.parse_args()
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        scraper = cls(topic=args.topic)
        if args.name:
            scraper.name = args.name
        scraper.run(output=args.output)


if __name__ == '__main__':
    BuCfaScraper.main()
