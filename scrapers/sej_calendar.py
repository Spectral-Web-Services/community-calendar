"""SEJ (Society of Environmental Journalists) calendar RSS scraper.

Parses event dates from HTML inside RSS <description> fields,
since <pubDate> is the CMS publish date, not the event date.
"""

import re
from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

from lib.rss import RssScraper


class SEJCalendarScraper(RssScraper):
    name = "Society of Environmental Journalists"
    domain = "sej.org"
    rss_url = "https://www.sej.org/rss_calendar"
    timezone = "America/New_York"

    def parse_entry(self, entry: dict) -> Optional[dict[str, Any]]:
        title = entry.get("title", "").strip()
        if not title:
            return None

        # Remove "DEADLINE: " prefix for cleaner titles but keep info in description
        clean_title = re.sub(r"^DEADLINE:\s*", "", title)

        url = entry.get("link", "")
        description_html = entry.get("summary", "")

        soup = BeautifulSoup(description_html, "html.parser")

        # Extract event dates from HTML spans
        dtstart = None
        dtend = None
        tz = ZoneInfo(self.timezone)

        # Single-day event
        single = soup.find("span", class_="date-display-single")
        if single:
            dtstart = self._parse_date_text(single.get_text(strip=True), tz)

        # Multi-day range
        range_start = soup.find("span", class_="date-display-start")
        range_end = soup.find("span", class_="date-display-end")
        if range_start:
            dtstart = self._parse_date_text(range_start.get_text(strip=True), tz)
        if range_end:
            dtend = self._parse_date_text(range_end.get_text(strip=True), tz)

        if not dtstart:
            self.logger.warning(f"No date found for: {title}")
            return None

        # Extract plain text description (body paragraphs)
        body_div = soup.find("div", class_="field-name-body")
        desc_text = ""
        if body_div:
            desc_text = body_div.get_text(separator="\n", strip=True)

        # Extract categories
        categories = []
        for vocab in ["vocabulary-4", "vocabulary-5", "vocabulary-7"]:
            field = soup.find("div", class_=f"field-name-taxonomy-{vocab}")
            if field:
                for link in field.find_all("a"):
                    categories.append(link.get_text(strip=True))

        if categories:
            desc_text = f"{desc_text}\n\nCategories: {', '.join(categories)}".strip()

        return {
            "title": clean_title,
            "dtstart": dtstart,
            "dtend": dtend,
            "url": url,
            "description": desc_text,
        }

    def _parse_date_text(self, text: str, tz: ZoneInfo) -> Optional[datetime]:
        """Parse date strings like 'Sunday, March 15, 2026' or 'March 15, 2026'."""
        # Strip day-of-week prefix
        text = re.sub(r"^\w+day,\s*", "", text.strip())
        for fmt in ("%B %d, %Y", "%b %d, %Y", "%B %d %Y"):
            try:
                dt = datetime.strptime(text, fmt)
                return dt.replace(hour=0, minute=0, tzinfo=tz)
            except ValueError:
                continue
        self.logger.warning(f"Could not parse date: {text}")
        return None


if __name__ == "__main__":
    SEJCalendarScraper.main()
