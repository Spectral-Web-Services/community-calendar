#!/usr/bin/env python3
"""Scraper for Visit Chicago North Shore events.

Discovers event URLs from the sitemap at /events.xml, then fetches each
page for JSON-LD structured data. Handles non-standard date formats
("Wednesday, June 17, 2026") used by their ColdFusion CMS.
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import html as html_mod
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import quote, urlparse

from lib.jsonld import JsonLdScraper, extract_jsonld_blocks, extract_events_from_blocks, parse_location


def parse_informal_date(s: str) -> Optional[datetime]:
    """Parse dates like 'Wednesday, June 17, 2026' or 'June 17, 2026'."""
    s = s.strip()
    # Strip leading day name
    s = re.sub(r'^[A-Za-z]+day,\s*', '', s)
    for fmt in ('%B %d, %Y', '%b %d, %Y', '%m/%d/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # Try ISO as last resort
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    except ValueError:
        return None


class VisitChicagoNorthShoreScraper(JsonLdScraper):
    name = "Visit Chicago North Shore"
    domain = "visitchicagonorthshore.com"
    url = ""
    default_location = "Chicago North Shore"
    sitemap_url = "https://www.visitchicagonorthshore.com/events.xml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    def get_urls(self) -> list[str]:
        """Fetch event URLs from the sitemap."""
        html = self.fetch_html(self.sitemap_url)
        if not html:
            return []
        try:
            root = ET.fromstring(html)
            ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = []
            for loc in root.findall('.//sm:loc', ns):
                if loc.text:
                    # Encode non-ASCII characters in URL path
                    parsed = urlparse(loc.text)
                    encoded = parsed._replace(path=quote(parsed.path, safe='/:@!$&\'()*+,;=-._~'))
                    urls.append(encoded.geturl())
            self.logger.info(f"Found {len(urls)} event URLs in sitemap")
            return urls
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse sitemap: {e}")
            return []

    def _parse_event(self, item: dict) -> Optional[dict[str, Any]]:
        """Parse JSON-LD with non-standard date formats and image extraction."""
        title = html_mod.unescape(item.get('name', 'Untitled'))
        start_str = item.get('startDate', '')

        if not start_str:
            return None

        dtstart = parse_informal_date(start_str)
        if not dtstart:
            self.logger.debug(f"Skipping {title}: unparseable startDate '{start_str}'")
            return None

        # Skip past events
        now = datetime.now(timezone.utc)
        start_aware = dtstart if dtstart.tzinfo else dtstart.replace(tzinfo=timezone.utc)
        if start_aware < now:
            return None

        # End date
        dtend = None
        end_str = item.get('endDate', '')
        if end_str:
            dtend = parse_informal_date(end_str)

        # Location
        location = parse_location(item.get('location'), self.default_location)

        # Description
        desc = item.get('description', '') or ''
        desc = html_mod.unescape(desc)
        desc = re.sub(r'<[^>]+>', ' ', desc).strip()
        desc = re.sub(r'\s+', ' ', desc)

        # Image
        image_url = ''
        images = item.get('image', [])
        if isinstance(images, list) and images:
            image_url = images[0]
        elif isinstance(images, str):
            image_url = images

        url = item.get('url', '')

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend,
            'location': location,
            'description': desc[:500] if desc else '',
            'url': url,
            'image_url': image_url,
        }


if __name__ == '__main__':
    VisitChicagoNorthShoreScraper.main()
