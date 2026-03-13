"""PEN America events scraper.

Fetches events from pen.org via the WordPress REST API.
Events use ACF (Advanced Custom Fields) for date/time data.
"""

from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

import requests

from lib.base import BaseScraper

# US timezone abbreviation mapping
TZ_MAP = {
    "ET": "America/New_York",
    "CT": "America/Chicago",
    "MT": "America/Denver",
    "PT": "America/Los_Angeles",
}


class PENAmericaScraper(BaseScraper):
    name = "PEN America"
    domain = "pen.org"
    timezone = "America/New_York"
    api_url = "https://pen.org/wp-json/wp/v2/event"
    location_url = "https://pen.org/wp-json/wp/v2/event-location"

    def __init__(self):
        super().__init__()
        self._locations: dict[int, str] = {}

    def _load_locations(self):
        """Load location taxonomy terms."""
        if self._locations:
            return
        try:
            resp = requests.get(self.location_url, params={"per_page": 100}, timeout=30)
            resp.raise_for_status()
            for term in resp.json():
                self._locations[term["id"]] = term["name"]
        except requests.RequestException as e:
            self.logger.warning(f"Failed to load locations: {e}")

    def fetch_events(self) -> list[dict[str, Any]]:
        self._load_locations()
        self.logger.info(f"Fetching events from {self.api_url}")

        events = []
        page = 1
        while True:
            resp = requests.get(
                self.api_url,
                params={"per_page": 100, "page": page, "orderby": "date", "order": "desc"},
                timeout=30,
            )
            if resp.status_code == 400:
                break  # No more pages
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break

            for item in data:
                event = self._parse_event(item)
                if event:
                    events.append(event)

            # Check if there are more pages
            total_pages = int(resp.headers.get("X-WP-TotalPages", 1))
            if page >= total_pages:
                break
            page += 1

        self.logger.info(f"Found {len(events)} events")
        return events

    def _parse_event(self, item: dict) -> Optional[dict[str, Any]]:
        """Parse a single WP REST API event item."""
        acf = item.get("acf", {})

        # Skip hidden events
        meta = acf.get("event_meta", {}).get("value", {})
        if meta.get("hidden_event", {}).get("value"):
            return None

        title = item.get("title", {}).get("rendered", "").strip()
        if not title:
            return None

        # Parse dates from ACF
        event_date = acf.get("event_date", {}).get("value", {})
        start_str = event_date.get("start_time", {}).get("value", "")
        end_str = event_date.get("end_time", {}).get("value", "")

        if not start_str:
            self.logger.warning(f"No start date for: {title}")
            return None

        # Determine timezone
        tz_abbr = acf.get("time_zone", {})
        if isinstance(tz_abbr, dict):
            tz_abbr = tz_abbr.get("value", "ET")
        tz_name = TZ_MAP.get(tz_abbr or "ET", self.timezone)
        tz = ZoneInfo(tz_name)

        dtstart = self._parse_datetime(start_str, tz)
        dtend = self._parse_datetime(end_str, tz) if end_str else None

        if not dtstart:
            self.logger.warning(f"Could not parse date for: {title}")
            return None

        # Location
        loc_ids = item.get("event-location", [])
        location = ", ".join(
            self._locations.get(lid, "") for lid in loc_ids if self._locations.get(lid)
        ) or None

        # URL
        url = item.get("link", "")

        # Description from content
        description = ""
        content = item.get("content", {}).get("rendered", "")
        if content:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, "html.parser")
            description = soup.get_text(separator="\n", strip=True)[:2000]

        # Cost info
        options = acf.get("event_options", {}).get("value", {})
        cost = options.get("cost", {}).get("value", "")
        if cost and cost != "Free":
            description = f"Cost: {cost}\n{description}".strip()

        return {
            "title": title,
            "dtstart": dtstart,
            "dtend": dtend,
            "url": url,
            "location": location,
            "description": description,
        }

    def _parse_datetime(self, text: str, tz: ZoneInfo) -> Optional[datetime]:
        """Parse datetime string like '2026-03-19 18:00:00'."""
        if not text or not text.strip():
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(text.strip(), fmt).replace(tzinfo=tz)
            except ValueError:
                continue
        self.logger.warning(f"Could not parse datetime: {text}")
        return None


if __name__ == "__main__":
    PENAmericaScraper.main()
