#!/usr/bin/env python3
"""
Scraper for OvationTix (AudienceView Professional) venues.

OvationTix hosts ticketing for many small/mid-size theaters. The ci.ovationtix.com
frontend is a React SPA behind Cloudflare, but web.ovationtix.com serves
server-rendered HTML:
  - /trs/cal/{orgId}         — lists all current productions
  - /trs/cal/{orgId}?productionId={id} — shows individual performance dates/times

Usage:
    python scrapers/ovationtix.py --org 2462 --name "Central Square Theater" -o cities/boston/central_square.ics
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

BASE_URL = 'https://web.ovationtix.com/trs/cal'


class OvationTixScraper(BaseScraper):
    name = 'OvationTix Venue'
    domain = 'ovationtix.com'
    timezone = 'America/New_York'

    def __init__(self, org_id, tz='America/New_York'):
        super().__init__()
        self.org_id = org_id
        self.tz = ZoneInfo(tz)
        self.timezone = tz
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; CommunityCalendar/1.0)'
        })

    def fetch_events(self):
        """Fetch all productions and their individual performances."""
        productions = self._fetch_productions()
        logger.info(f'Found {len(productions)} productions')

        events = []
        for prod in productions:
            perfs = self._fetch_performances(prod)
            events.extend(perfs)

        logger.info(f'Found {len(events)} total performances')
        return events

    def _fetch_productions(self):
        """Fetch the production listing page and extract production IDs/titles."""
        url = f'{BASE_URL}/{self.org_id}'
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f'Failed to fetch productions: {e}')
            return []

        soup = BeautifulSoup(resp.text, 'html.parser')
        productions = []

        # Productions are linked as ci.ovationtix.com/{orgId}/production/{prodId}
        for link in soup.find_all('a', href=re.compile(r'/production/(\d+)')):
            m = re.search(r'/production/(\d+)', link['href'])
            if not m:
                continue
            prod_id = m.group(1)
            text = link.get_text(strip=True)

            # Skip generic links like "buy now"
            if text.lower() in ('buy now »', 'buy now', ''):
                continue

            # Check if we already have this production
            if any(p['id'] == prod_id for p in productions):
                continue

            productions.append({'id': prod_id, 'title': text})

        # Collect all link texts per production
        merged = {}
        for link in soup.find_all('a', href=re.compile(r'/production/(\d+)')):
            m = re.search(r'/production/(\d+)', link['href'])
            if not m:
                continue
            prod_id = m.group(1)
            text = link.get_text(strip=True)
            if text.lower() in ('buy now »', 'buy now', ''):
                continue
            merged.setdefault(prod_id, []).append(text)

        # Also collect surrounding text for each production link (for sites
        # where titles are outside the <a> tags, e.g. Wheelock)
        context_titles = {}
        for link in soup.find_all('a', href=re.compile(r'/production/(\d+)')):
            m = re.search(r'/production/(\d+)', link['href'])
            if not m or m.group(1) in context_titles:
                continue
            prod_id = m.group(1)
            # Walk up to find a parent cell/div with meaningful text
            for parent in link.parents:
                if parent.name in ('td', 'div', 'li', 'tr'):
                    # Get text from bold/strong elements or direct text
                    for el in parent.find_all(['b', 'strong']):
                        t = el.get_text(strip=True)
                        if len(t) > 3 and not re.match(r'^\d{1,2}:\d{2}', t):
                            context_titles[prod_id] = t
                            break
                    if prod_id in context_titles:
                        break
                    # Try all text in the parent, filtering out times, subtitles, dates
                    title_candidates = []
                    for s in parent.stripped_strings:
                        if (len(s) > 3
                                and not re.match(r'^\d{1,2}:\d{2}', s)
                                and not re.match(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', s)
                                and not s.lower().startswith('based on')
                                and not s.lower().startswith('directed by')
                                and s.lower() not in ('buy now »', 'buy now', 'see schedule')
                                and '»' not in s):
                            title_candidates.append(s)
                    if title_candidates:
                        context_titles[prod_id] = title_candidates[0]
                    if prod_id in context_titles:
                        break

        # Build final production list
        TIME_RE = re.compile(r'^\d{1,2}:\d{2}\s*(am|pm|AM|PM)')
        final = []
        seen = set()
        for prod_id, texts in merged.items():
            if prod_id in seen:
                continue
            seen.add(prod_id)
            # Filter out times, author credits, director credits
            candidates = [t for t in texts
                          if not t.lower().startswith('directed by')
                          and not re.match(r".+('s|'s)$", t)
                          and not TIME_RE.match(t)]
            if candidates:
                title = candidates[0]
            elif prod_id in context_titles:
                title = context_titles[prod_id]
            else:
                title = texts[0]
            final.append({'id': prod_id, 'title': title})

        return final

    def _fetch_performances(self, production):
        """Fetch individual performance dates/times for a production.

        Handles two OvationTix calendar formats:
        1. List view: full dates like "Thursday, April 2, 2026" with times below
        2. Grid view: month/year header with day numbers in table cells
        """
        url = f'{BASE_URL}/{self.org_id}?productionId={production["id"]}'
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            logger.warning(f'Failed to fetch performances for {production["title"]}: {e}')
            return []

        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text()
        prod_url = f'https://ci.ovationtix.com/{self.org_id}/production/{production["id"]}'
        venue = self._venue_name(soup)

        # Strategy 1: List view with full dates ("Thursday, April 2, 2026")
        events = self._parse_list_view(text, production, prod_url, venue)
        if events:
            return events

        # Strategy 2: Grid/calendar view — find performance links and resolve
        # dates from the calendar grid structure
        events = self._parse_grid_view(soup, production, prod_url, venue)
        if events:
            return events

        logger.warning(f'No performances found for {production["title"]}')
        return []

    def _parse_list_view(self, text, production, prod_url, venue):
        """Parse list-style calendar with full date headers."""
        events = []
        current_date = None
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue

            date_match = re.match(
                r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+'
                r'(\w+ \d{1,2},\s*\d{4})', line
            )
            if date_match:
                try:
                    current_date = datetime.strptime(date_match.group(1), '%B %d, %Y')
                except ValueError:
                    pass
                continue

            if current_date:
                times = re.findall(r'(\d{1,2}:\d{2}\s*[AP]M)', line, re.IGNORECASE)
                for time_str in times:
                    dt = self._combine_date_time(current_date, time_str)
                    if dt:
                        events.append({
                            'title': production['title'],
                            'dtstart': dt,
                            'dtend': dt + timedelta(hours=2),
                            'url': prod_url,
                            'location': venue,
                        })
        return events

    def _parse_grid_view(self, soup, production, prod_url, venue):
        """Parse grid/calendar view with month header and day-number cells.

        Performance links (ci.ovationtix.com/.../production/X?performanceId=Y)
        sit inside table cells. We find the month/year from the page, then
        resolve each cell's day number to a full date.
        """
        # Find month/year — look for "March 2026" pattern in page text
        text = soup.get_text()
        months_found = re.findall(r'(January|February|March|April|May|June|July|'
                                  r'August|September|October|November|December)\s+(\d{4})', text)
        if not months_found:
            return []

        # Use the first month found (current view)
        month_name, year_str = months_found[0]
        base_month = datetime.strptime(f'{month_name} {year_str}', '%B %Y')

        events = []
        # Find all performance links for this production
        for link in soup.find_all('a', href=re.compile(rf'/production/{production["id"]}\b')):
            time_text = link.get_text(strip=True)
            time_match = re.match(r'(\d{1,2}:\d{2}\s*[ap]m)', time_text, re.IGNORECASE)
            if not time_match:
                continue

            # Walk up to find the day number in a parent cell
            day = self._find_day_in_parents(link)
            if not day:
                continue

            # Determine the correct month — if day < current month's first
            # performance day and we have multiple months, it might be next month
            dt = base_month.replace(day=day)

            # If multiple months are shown, check if this day belongs to a later month
            if len(months_found) > 1:
                # Find which month section this link falls in by checking
                # position relative to month headers in the HTML
                for mn, yr in months_found:
                    try:
                        candidate = datetime.strptime(f'{mn} {day} {yr}', '%B %d %Y')
                        # Simple heuristic: use later month if day is small
                        # and appears after the first month's days
                        dt = candidate
                    except ValueError:
                        continue

            full_dt = self._combine_date_time(dt, time_match.group(1))
            if full_dt:
                events.append({
                    'title': production['title'],
                    'dtstart': full_dt,
                    'dtend': full_dt + timedelta(hours=2),
                    'url': prod_url,
                    'location': venue,
                })

        return events

    def _find_day_in_parents(self, element):
        """Walk up from a link to find the day number in a parent table cell."""
        for parent in element.parents:
            if parent.name == 'td':
                # Look for a bare number (day of month) in the cell
                for s in parent.stripped_strings:
                    m = re.match(r'^(\d{1,2})$', s.strip())
                    if m:
                        day = int(m.group(1))
                        if 1 <= day <= 31:
                            return day
                break
        return None

    def _combine_date_time(self, date, time_str):
        """Combine a date object with a time string like '7:30 PM'."""
        time_str = time_str.strip().upper()
        m = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str)
        if not m:
            return None
        hour, minute, ampm = int(m.group(1)), int(m.group(2)), m.group(3)
        if ampm == 'PM' and hour != 12:
            hour += 12
        elif ampm == 'AM' and hour == 12:
            hour = 0
        return date.replace(hour=hour, minute=minute, tzinfo=self.tz)

    def _venue_name(self, soup):
        """Extract venue name from the page, or return default."""
        # Look for venue in table cells
        for td in soup.find_all('td'):
            text = td.get_text(strip=True)
            if 'theater' in text.lower() or 'theatre' in text.lower():
                if len(text) < 100:
                    return text
        return self.name

    @classmethod
    def parse_args(cls, description=None):
        parser = argparse.ArgumentParser(description=description or 'Scrape OvationTix venue')
        parser.add_argument('--org', required=True, help='OvationTix organization ID')
        parser.add_argument('--output', '-o', type=str, help='Output filename')
        parser.add_argument('--name', type=str, help='Source name override')
        parser.add_argument('--timezone', type=str, default='America/New_York', help='Timezone')
        parser.add_argument('--debug', action='store_true', help='Enable debug logging')
        return parser.parse_args()

    @classmethod
    def main(cls):
        cls.setup_logging()
        args = cls.parse_args()
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        scraper = cls(org_id=args.org, tz=args.timezone)
        if args.name:
            scraper.name = args.name
        scraper.run(output=args.output)


if __name__ == '__main__':
    OvationTixScraper.main()
