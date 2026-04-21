#!/usr/bin/env python3
"""
Scraper for Village Network of Petaluma events.
https://www.villagenetworkofpetaluma.org/events/index_list

The list view is Cloudflare-protected with default UAs, but two
underlying endpoints are open:
  - /events.json?start=YYYY-MM-DD&end=YYYY-MM-DD — bulk index
    returning {title, start, url, color} per event
  - /events/{id}.ics — full per-event ICS with SUMMARY, LOCATION,
    DTSTART/DTEND (DESCRIPTION is empty)

We pull the index, then fetch each event's ICS in parallel and re-emit
the events as our own VEVENTs.
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import requests
from icalendar import Calendar

from lib.base import BaseScraper
from lib.utils import DEFAULT_HEADERS


class VillageNetworkScraper(BaseScraper):
    name = "Village Network of Petaluma"
    domain = "villagenetworkofpetaluma.org"
    timezone = "America/Los_Angeles"

    BASE_URL = "https://www.villagenetworkofpetaluma.org"
    INDEX_URL = f"{BASE_URL}/events.json"
    EVENTS_PAGE = f"{BASE_URL}/events/index_list"

    def fetch_events(self) -> list[dict[str, Any]]:
        tz = ZoneInfo(self.timezone)
        start = datetime.now(tz).date()
        end = start + timedelta(days=self.months_ahead * 31 + 14)
        params = {'start': start.isoformat(), 'end': end.isoformat()}
        self.logger.info(f"Fetching index {self.INDEX_URL} for {start} → {end}")

        index_resp = requests.get(self.INDEX_URL, params=params, headers=DEFAULT_HEADERS, timeout=30)
        index_resp.raise_for_status()
        index = index_resp.json()
        self.logger.info(f"Found {len(index)} events in index")

        # Extract event IDs from /events/{id} URLs
        ids: list[str] = []
        for item in index:
            url = item.get('url', '')
            m = re.match(r'^/events/(\d+)', url)
            if m:
                ids.append(m.group(1))

        events = []
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(self._fetch_one, eid, tz): eid for eid in ids}
            for fut in as_completed(futures):
                try:
                    event = fut.result()
                    if event:
                        events.append(event)
                except Exception as e:
                    self.logger.warning(f"Failed to fetch event {futures[fut]}: {e}")

        return events

    def _fetch_one(self, event_id: str, tz: ZoneInfo) -> dict[str, Any] | None:
        url = f"{self.BASE_URL}/events/{event_id}.ics"
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=20)
        if resp.status_code != 200:
            return None

        cal = Calendar.from_ical(resp.text)
        for component in cal.walk('VEVENT'):
            summary = str(component.get('summary', ''))
            # Strip the "Village event: " prefix the platform adds
            title = re.sub(r'^Village event:\s*', '', summary).strip()
            if not title:
                continue

            dtstart = component.get('dtstart').dt if component.get('dtstart') else None
            dtend = component.get('dtend').dt if component.get('dtend') else None
            if dtstart and not hasattr(dtstart, 'tzinfo'):
                dtstart = datetime.combine(dtstart, datetime.min.time()).replace(tzinfo=tz)
            elif dtstart and dtstart.tzinfo is None:
                dtstart = dtstart.replace(tzinfo=tz)
            if dtend and not hasattr(dtend, 'tzinfo'):
                dtend = datetime.combine(dtend, datetime.min.time()).replace(tzinfo=tz)
            elif dtend and dtend.tzinfo is None:
                dtend = dtend.replace(tzinfo=tz)

            location = str(component.get('location', '')) or ''
            # Use the public-domain event page URL, not the helpfulvillage subdomain.
            event_url = f"{self.BASE_URL}/events/{event_id}"

            return {
                'title': title,
                'dtstart': dtstart,
                'dtend': dtend,
                'url': event_url,
                'location': location,
                'description': '',
            }
        return None


if __name__ == '__main__':
    VillageNetworkScraper.main()
