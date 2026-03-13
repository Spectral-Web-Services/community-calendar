"""NABJ (National Assoc. of Black Journalists) events scraper.

Parses the Wild Apricot RSS feed at nabj.org/resource/rss/events.rss.
The feed redirects to a CDN URL that bypasses Cloudflare protection.
The pubDate field contains the actual event start date.
"""

from typing import Any, Optional

from lib.rss import RssScraper


class NABJEventsScraper(RssScraper):
    name = "NABJ"
    domain = "nabj.org"
    rss_url = "https://www.nabj.org/resource/rss/events.rss"
    timezone = "America/New_York"

    def parse_entry(self, entry: dict) -> Optional[dict[str, Any]]:
        title = entry.get("title", "").strip()
        if not title:
            return None

        dtstart = self.parse_rss_date(entry)
        if not dtstart:
            self.logger.warning(f"No date found for: {title}")
            return None

        url = entry.get("link", "")
        description = entry.get("summary", "").strip()

        return {
            "title": title,
            "dtstart": dtstart,
            "dtend": None,
            "url": url,
            "description": description,
        }


if __name__ == "__main__":
    NABJEventsScraper.main()
