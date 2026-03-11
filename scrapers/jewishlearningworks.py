#!/usr/bin/env python3
"""
Scraper for Jewish LearningWorks events (jewishlearning.works).

Uses the WordPress REST API to discover events in the "professional-learning"
category, then fetches each detail page to extract dates and location from
the rendered Elementor content.

Usage:
    python scrapers/jewishlearningworks.py \
        --output cities/jweekly/jewishlearningworks.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import argparse
import json
import logging
import re
from datetime import datetime
from typing import Any, Optional
from urllib.request import urlopen, Request
from urllib.error import HTTPError

from lib.base import BaseScraper

logger = logging.getLogger(__name__)

API_URL = "https://jewishlearning.works/wp-json/wp/v2/events"
CATEGORY_ID = 21  # professional-learning


def fetch_json(url: str) -> Any:
    """Fetch JSON from a URL."""
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_html(url: str) -> str:
    """Fetch HTML from a URL."""
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_date(text: str) -> Optional[datetime]:
    """Parse a date string like 'March 13, 2026 - 10:00 AM PDT'."""
    # Strip timezone abbreviations
    text = re.sub(r'\s+(P[SD]T|E[SD]T|C[SD]T|M[SD]T|UTC)\s*$', '', text.strip())
    for fmt in (
        "%B %d, %Y - %I:%M %p",
        "%B %d, %Y at %I:%M %p",
        "%B %d, %Y %I:%M %p",
        "%B %d, %Y",
    ):
        try:
            return datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue
    return None


def extract_when_from_content(html: str) -> tuple[Optional[datetime], Optional[datetime]]:
    """Extract start/end from 'When:' pattern in content HTML."""
    # Pattern: "When: Tuesday, May 19, 2026 from 11:00 am to 2:00 pm."
    m = re.search(
        r'When:?\s*</(?:span|strong|b)>\s*(?:\w+day,?\s+)?(.+?)(?:\s+from\s+(.+?)\s+to\s+(.+?))[.<]',
        html, re.IGNORECASE | re.DOTALL
    )
    if m:
        date_str = m.group(1).strip()
        start_time = m.group(2).strip()
        end_time = m.group(3).strip()
        dtstart = parse_date(f"{date_str} - {start_time}")
        dtend = parse_date(f"{date_str} - {end_time}")
        if dtstart:
            return dtstart, dtend
    # Pattern: "When: ... at 10:00 am" (with optional timezone like "PT", "PST")
    m = re.search(
        r'When:?\s*</(?:span|strong|b)>\s*(?:\w+day,?\s+)?(.+?)\s+at\s+(.+?)(?:\s+(?:P[SD]T|E[SD]T|C[SD]T|M[SD]T|PT|ET|CT|MT))?[.<]',
        html, re.IGNORECASE | re.DOTALL
    )
    if m:
        date_str = m.group(1).strip()
        time_str = m.group(2).strip()
        dtstart = parse_date(f"{date_str} - {time_str}")
        if dtstart:
            return dtstart, None
    return None, None


def extract_from_detail_page(url: str) -> dict[str, Any]:
    """Fetch detail page and extract date/time and address."""
    result: dict[str, Any] = {}
    try:
        html = fetch_html(url)
    except (HTTPError, Exception) as e:
        logger.warning("Failed to fetch %s: %s", url, e)
        return result

    # Strategy 1: FROM/TO date patterns in various HTML structures
    # Try: <dt>FROM</dt><dd>date</dd>
    # Try: <span>FROM</span>&nbsp; date</div>
    # Try: <strong>FROM</strong> date</p>
    from_patterns = [
        r'FROM\s*</dt>\s*<dd[^>]*>\s*(.+?)</dd>',
        r'FROM\s*</span>(?:\s|&nbsp;)*(.+?)</div>',
        r'FROM\s*</strong>(?:\s|&nbsp;)*(.+?)(?:</p>|</div>)',
    ]
    to_patterns = [
        r'\bTO\s*</dt>\s*<dd[^>]*>\s*(.+?)</dd>',
        r'\bTO\s*</span>(?:\s|&nbsp;)*(.+?)</div>',
        r'\bTO\s*</strong>(?:\s|&nbsp;)*(.+?)(?:</p>|</div>)',
    ]

    for pat in from_patterns:
        from_match = re.search(pat, html, re.IGNORECASE)
        if from_match:
            text = re.sub(r'<[^>]+>', '', from_match.group(1)).strip()
            text = text.replace('\xa0', ' ').strip()
            dtstart = parse_date(text)
            if dtstart:
                result['dtstart'] = dtstart
                break

    for pat in to_patterns:
        to_match = re.search(pat, html, re.IGNORECASE)
        if to_match:
            text = re.sub(r'<[^>]+>', '', to_match.group(1)).strip()
            text = text.replace('\xa0', ' ').strip()
            dtend = parse_date(text)
            if dtend:
                result['dtend'] = dtend
                break

    # Strategy 2: "When:" pattern in content (fallback)
    if 'dtstart' not in result:
        when_start, when_end = extract_when_from_content(html)
        if when_start:
            result['dtstart'] = when_start
        if when_end:
            result['dtend'] = when_end

    # ADDRESS section (definition list or paragraph)
    addr_match = re.search(r'ADDRESS\s*</dt>\s*<dd[^>]*>\s*(.+?)</dd>', html, re.IGNORECASE | re.DOTALL)
    if not addr_match:
        addr_match = re.search(r'ADDRESS</(?:strong|b|span|h\d)>\s*</?\w[^>]*>\s*(.+?)(?:</p>|</div>)', html, re.IGNORECASE | re.DOTALL)
    if addr_match:
        addr = re.sub(r'<[^>]+>', '', addr_match.group(1)).strip()
        if addr:
            result['location'] = addr

    # Where: pattern in content
    if 'location' not in result:
        where_match = re.search(r'Where:?\s*</(?:span|strong|b)>\s*(.+?)(?:</li>|</p>|<br)', html, re.IGNORECASE | re.DOTALL)
        if where_match:
            loc = re.sub(r'<[^>]+>', '', where_match.group(1)).strip()
            if loc:
                result['location'] = loc

    return result


class JewishLearningWorksScraper(BaseScraper):
    name = "Jewish LearningWorks"
    domain = "jewishlearning.works"
    timezone = "America/Los_Angeles"

    def fetch_events(self) -> list[dict[str, Any]]:
        events = []
        page = 1
        per_page = 20

        # Fetch all professional-learning events from WP REST API
        all_items = []
        while True:
            url = f"{API_URL}?event-categories={CATEGORY_ID}&per_page={per_page}&page={page}"
            try:
                items = fetch_json(url)
            except HTTPError as e:
                if e.code == 400:  # past last page
                    break
                raise
            if not items:
                break
            all_items.extend(items)
            if len(items) < per_page:
                break
            page += 1

        logger.info("Found %d events from API", len(all_items))

        for item in all_items:
            title = re.sub(r'<[^>]+>', '', item.get('title', {}).get('rendered', '')).strip()
            link = item.get('link', '')
            content_html = item.get('content', {}).get('rendered', '')
            excerpt = re.sub(r'<[^>]+>', '', item.get('excerpt', {}).get('rendered', '')).strip()

            if not title or not link:
                continue

            # Try to get dates from content "When:" pattern first
            dtstart, dtend = extract_when_from_content(content_html)

            # Fetch detail page for more reliable date/location
            detail = extract_from_detail_page(link)

            # Prefer detail page dates over content dates
            if 'dtstart' in detail:
                dtstart = detail['dtstart']
            if 'dtend' in detail:
                dtend = detail['dtend']

            if not dtstart:
                logger.warning("No date found for: %s", title)
                continue

            # Skip past events
            if dtstart < datetime.now():
                continue

            event = {
                'title': title,
                'dtstart': dtstart,
                'url': link,
                'description': excerpt,
            }
            if dtend:
                event['dtend'] = dtend
            if detail.get('location'):
                event['location'] = detail['location']

            events.append(event)
            logger.info("  %s — %s", dtstart.strftime('%Y-%m-%d'), title)

        return events


if __name__ == '__main__':
    JewishLearningWorksScraper.setup_logging()
    args = JewishLearningWorksScraper.parse_args()
    scraper = JewishLearningWorksScraper()
    scraper.run(output=args.output)
