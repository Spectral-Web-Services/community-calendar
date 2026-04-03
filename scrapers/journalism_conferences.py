#!/usr/bin/env python3
"""
Scraper for the journalism.wtf 2026 Conference Calendar (Airtable shared view).
https://www.journalism.wtf/journalism-conferences-2026/

The Airtable embed at this page exposes a shared view API. We:
1. Fetch the embed HTML to extract a fresh access-policy token and request ID.
2. Call the Airtable readSharedViewData API with those credentials.
3. Parse the JSON response into event dicts.

Usage:
    python scrapers/journalism_conferences.py --output cities/publisher-resources/journalism_conferences.ics
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import json
import re
from datetime import datetime
from typing import Any, Optional
from urllib.parse import unquote

import requests

from lib.base import BaseScraper

EMBED_URL = (
    "https://airtable.com/embed/appdQ4Dw4XiTJosQ3/shrf3WOwq5zRMEuIZ"
    "?layout=card&viewControls=on"
)

AIRTABLE_BASE = "https://airtable.com"

BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class JournalismConferencesScraper(BaseScraper):
    """Scraper for journalism conferences from Airtable shared view."""

    name = "Journalism Conferences"
    domain = "journalism.wtf"
    timezone = "America/New_York"

    def fetch_events(self) -> list[dict[str, Any]]:
        """Fetch conferences from the Airtable shared view API."""
        session = requests.Session()
        session.headers['User-Agent'] = BROWSER_UA

        # Step 1: Load the embed page to get cookies and the prefetch URL
        self.logger.info("Fetching Airtable embed page for access token")
        resp = session.get(EMBED_URL, timeout=30)
        resp.raise_for_status()

        api_path = self._extract_api_path(resp.text)
        if not api_path:
            self.logger.error("Could not extract API path from embed page")
            return []

        headers = self._extract_headers(resp.text)

        # Step 2: Call the data API
        self.logger.info("Fetching shared view data from Airtable API")
        data_resp = session.get(
            f"{AIRTABLE_BASE}{api_path}",
            headers=headers,
            timeout=60,
        )
        data_resp.raise_for_status()
        payload = data_resp.json()

        if payload.get('msg') != 'SUCCESS':
            self.logger.error(f"Airtable API returned: {payload.get('msg')}")
            return []

        # Step 3: Parse the response
        table = payload['data']['table']
        return self._parse_rows(table)

    def _extract_api_path(self, html: str) -> Optional[str]:
        """Extract the readSharedViewData URL from the embed page JS."""
        # The prefetch script contains a fetch() call with the full API path
        match = re.search(
            r'fetch\("(\\u002F[^"]*readSharedViewData[^"]*)"',
            html,
        )
        if not match:
            return None

        raw = match.group(1)
        # Decode JS unicode escapes (\u002F -> /)
        path = raw.encode().decode('unicode_escape')
        return path

    def _extract_headers(self, html: str) -> dict:
        """Extract the request headers from the prefetch script."""
        match = re.search(r'var headers\s*=\s*(\{[^}]+\})', html)
        base_headers = {
            'Accept': 'application/json',
            'Referer': EMBED_URL,
            'x-time-zone': 'America/New_York',
        }
        if match:
            try:
                h = json.loads(match.group(1))
                base_headers.update(h)
            except json.JSONDecodeError:
                pass
        # Don't request msgpack — we want JSON
        base_headers.pop('x-airtable-accept-msgpack', None)
        return base_headers

    def _parse_rows(self, table: dict) -> list[dict[str, Any]]:
        """Parse Airtable table data into event dicts."""
        columns = {c['id']: c for c in table.get('columns', [])}

        # Build lookup maps for select/multiSelect fields
        select_maps = {}
        for col in table.get('columns', []):
            choices = (col.get('typeOptions') or {}).get('choices')
            if choices and col['type'] in ('select', 'multiSelect'):
                select_maps[col['id']] = {
                    cid: c['name'] for cid, c in choices.items()
                }

        events = []
        for row in table.get('rows', []):
            cells = row.get('cellValuesByColumnId', {})
            record = self._resolve_cells(cells, columns, select_maps)
            event = self._record_to_event(record)
            if event:
                events.append(event)

        return events

    def _resolve_cells(
        self,
        cells: dict,
        columns: dict,
        select_maps: dict,
    ) -> dict[str, Any]:
        """Resolve raw cell values to human-readable values."""
        record = {}
        for col_id, val in cells.items():
            col = columns.get(col_id)
            if not col:
                continue
            name = col['name']
            col_type = col['type']

            if col_type == 'select' and col_id in select_maps:
                record[name] = select_maps[col_id].get(val, val)
            elif col_type == 'multiSelect' and col_id in select_maps:
                record[name] = [
                    select_maps[col_id].get(v, v) for v in (val or [])
                ]
            elif col_type == 'foreignKey' and isinstance(val, list):
                record[name] = ', '.join(
                    v.get('foreignRowDisplayName', '') for v in val
                )
            elif col_type == 'date' and val:
                record[name] = val[:10]  # "2026-03-05T00:00:00.000Z" -> "2026-03-05"
            else:
                record[name] = val

        return record

    def _record_to_event(self, r: dict) -> Optional[dict[str, Any]]:
        """Convert a resolved Airtable record to a scraper event dict."""
        title = r.get('Instance')
        start_str = r.get('Start Date')
        if not title or not start_str:
            return None

        try:
            dtstart = datetime.strptime(start_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            self.logger.debug(f"Skipping {title}: bad start date {start_str}")
            return None

        dtend = None
        end_str = r.get('End Date')
        if end_str:
            try:
                dtend = datetime.strptime(end_str, '%Y-%m-%d')
            except (ValueError, TypeError):
                pass

        # Build location from City, State, Country
        loc_parts = [
            p for p in [r.get('City'), r.get('State'), r.get('Country')]
            if p
        ]
        location = ', '.join(loc_parts)

        url = r.get('Conference Website', '')

        # Build description from host, attendance type, scope, format
        desc_parts = []
        host = r.get('Host')
        if host:
            desc_parts.append(f"Host: {host}")
        attendance = r.get('Attendance Type')
        if attendance:
            desc_parts.append(f"Attendance: {attendance}")
        scope = r.get('Scope')
        if scope:
            desc_parts.append(f"Scope: {scope}")
        fmt = r.get('Format')
        if fmt:
            if isinstance(fmt, list):
                fmt = ', '.join(fmt)
            desc_parts.append(f"Format: {fmt}")
        notes = r.get('Schedule Notes')
        if notes:
            desc_parts.append(notes)
        description = '\n'.join(desc_parts)

        self.logger.info(f"Found: {title} on {start_str}")

        return {
            'title': title,
            'dtstart': dtstart,
            'dtend': dtend or dtstart,
            'url': url,
            'location': location,
            'description': description,
        }


if __name__ == '__main__':
    JournalismConferencesScraper.main()
