"""Solutions Journalism Network events scraper.

Scrapes events from solutionsjournalism.org/events (Drupal site).
Fetches the listing page, extracts event links, then scrapes each
event detail page for dates, location, and description.
"""

import re
from datetime import datetime, timedelta
from typing import Any, Optional
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

from lib.base import BaseScraper


class SJNEventsScraper(BaseScraper):
    name = "Solutions Journalism Network"
    domain = "solutionsjournalism.org"
    timezone = "America/New_York"
    base_url = "https://www.solutionsjournalism.org"
    events_url = "https://www.solutionsjournalism.org/events"

    def fetch_events(self) -> list[dict[str, Any]]:
        self.logger.info(f"Fetching events listing: {self.events_url}")
        resp = requests.get(self.events_url, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        events = []

        # Find all event links on the listing page
        seen_urls = set()
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if not href.startswith("/events/") or href == "/events/":
                continue
            # Skip anchor-only or filter links
            if "?" in href or "#" in href:
                continue
            full_url = self.base_url + href
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            event = self._scrape_event_page(full_url)
            if event:
                events.append(event)

        self.logger.info(f"Found {len(events)} events")
        return events

    def _scrape_event_page(self, url: str) -> Optional[dict[str, Any]]:
        """Scrape a single event detail page."""
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            self.logger.warning(f"Failed to fetch {url}: {e}")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        tz = ZoneInfo(self.timezone)

        # Title: look for h1 or the page title
        title_el = soup.find("h1")
        if not title_el:
            self.logger.warning(f"No title found at {url}")
            return None
        title = title_el.get_text(strip=True)

        # Extract date text - look for common patterns in the page body
        dtstart = None
        dtend = None
        date_text = self._find_date_text(soup)
        if date_text:
            dtstart, dtend = self._parse_date_range(date_text, tz)

        if not dtstart:
            self.logger.warning(f"No date found for: {title} at {url}")
            return None

        # Location
        location = self._find_field_text(soup, ["location", "venue", "where"])

        # Description
        description = self._extract_description(soup)

        # Registration/external link
        reg_link = self._find_registration_link(soup)
        event_url = reg_link or url

        return {
            "title": title,
            "dtstart": dtstart,
            "dtend": dtend,
            "url": event_url,
            "location": location,
            "description": description,
        }

    def _find_date_text(self, soup: BeautifulSoup) -> Optional[str]:
        """Find date text on the event page."""
        # SJN uses <div class="field field--date-start ...">DateApril 7, 2026</div>
        date_field = soup.find(class_=re.compile(r"field--date-start"))
        if date_field:
            text = date_field.get_text(strip=True)
            # Strip "Date" label prefix
            text = re.sub(r"^Date\s*", "", text, flags=re.I).strip()
            if text:
                return text

        # Fallback: look for heading "Date" followed by text
        for heading in soup.find_all(["h3", "h4", "strong", "label"]):
            if heading.get_text(strip=True).lower() in ("date", "dates", "when"):
                nxt = heading.next_sibling
                while nxt:
                    if hasattr(nxt, "get_text"):
                        text = nxt.get_text(strip=True)
                    else:
                        text = str(nxt).strip()
                    if text and re.search(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b", text):
                        return text
                    nxt = nxt.next_sibling

        # Try <time> elements
        time_el = soup.find("time")
        if time_el:
            dt_attr = time_el.get("datetime")
            if dt_attr:
                return dt_attr
            return time_el.get_text(strip=True)

        return None

    def _parse_date_range(self, text: str, tz: ZoneInfo) -> tuple[Optional[datetime], Optional[datetime]]:
        """Parse date range like 'March 13, 2026 to March 15, 2026' or 'April 7, 2026'."""
        # Handle ISO datetime attribute
        if re.match(r"\d{4}-\d{2}-\d{2}", text):
            try:
                dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
                return dt.astimezone(tz), None
            except ValueError:
                try:
                    dt = datetime.strptime(text[:10], "%Y-%m-%d")
                    return dt.replace(tzinfo=tz), None
                except ValueError:
                    pass

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Range: "March 13, 2026 to March 15, 2026"
        range_match = re.search(
            r"(\w+ \d{1,2},?\s*\d{4})\s*(?:to|–|-|—|through)\s*(\w+ \d{1,2},?\s*\d{4})",
            text, re.I
        )
        if range_match:
            dtstart = self._parse_single_date(range_match.group(1), tz)
            dtend = self._parse_single_date(range_match.group(2), tz)
            return dtstart, dtend

        # Single date: "April 7, 2026"
        single_match = re.search(r"(\w+ \d{1,2},?\s*\d{4})", text)
        if single_match:
            dtstart = self._parse_single_date(single_match.group(1), tz)
            return dtstart, None

        return None, None

    def _parse_single_date(self, text: str, tz: ZoneInfo) -> Optional[datetime]:
        """Parse a single date string."""
        text = text.strip().replace(",", ", ").replace("  ", " ").strip(", ")
        for fmt in ("%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y"):
            try:
                dt = datetime.strptime(text, fmt)
                return dt.replace(hour=0, minute=0, tzinfo=tz)
            except ValueError:
                continue
        self.logger.warning(f"Could not parse date: {text}")
        return None

    def _find_field_text(self, soup: BeautifulSoup, keywords: list[str]) -> Optional[str]:
        """Find text in fields matching keywords."""
        for kw in keywords:
            # SJN uses <div class="field field--location ...">LocationOnline (Zoom)</div>
            field = soup.find(class_=re.compile(rf"field--{kw}"))
            if field:
                text = field.get_text(strip=True)
                # Strip label prefix (e.g., "Location")
                text = re.sub(rf"^{kw}\s*", "", text, flags=re.I).strip()
                if text:
                    return text

            # Drupal field classes
            for el in soup.find_all(class_=re.compile(rf"field--name-field-{kw}|field-name-field-{kw}", re.I)):
                text = el.get_text(strip=True)
                if text:
                    return text
        return None

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract event description from the page body."""
        # Look for Drupal body field
        body = soup.find(class_=re.compile(r"field--name-body|field-name-body", re.I))
        if body:
            return body.get_text(separator="\n", strip=True)[:2000]

        # Fall back to main content paragraphs
        main = soup.find("main") or soup.find("article")
        if main:
            paragraphs = main.find_all("p")
            text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            return text[:2000]

        return ""

    def _find_registration_link(self, soup: BeautifulSoup) -> Optional[str]:
        """Find external registration or 'learn more' link."""
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True).lower()
            href = link["href"]
            if any(kw in text for kw in ["register", "learn more", "sign up", "apply", "rsvp"]):
                if href.startswith("http") and self.domain not in href:
                    return href
        return None


if __name__ == "__main__":
    SJNEventsScraper.main()
