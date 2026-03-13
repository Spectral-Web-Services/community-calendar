"""IRE/NICAR conference schedule scraper.

Fetches public JSON schedule data from IRE's S3 bucket and converts
sessions to ICS events. Handles both IRE and NICAR schema variants.
"""

import argparse
import logging
import re
from datetime import datetime
from html import unescape
from typing import Any, Optional
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

from lib.base import BaseScraper

S3_BASE = "https://ire-nicar-conference-schedules.s3.us-east-2.amazonaws.com"


class IREScheduleScraper(BaseScraper):
    name = "IRE Conference"
    domain = "ire.org"
    timezone = "America/New_York"

    def __init__(self, conference: str = "ire-2025"):
        super().__init__()
        self.conference = conference
        self.json_url = f"{S3_BASE}/{conference}/{conference}-schedule.json"
        # Derive friendly name from conference slug
        parts = conference.split("-")
        self.name = f"{parts[0].upper()} {parts[1]}" if len(parts) >= 2 else conference

    def fetch_events(self) -> list[dict[str, Any]]:
        self.logger.info(f"Fetching schedule: {self.json_url}")
        resp = requests.get(self.json_url, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Handle both flat list (IRE 2025) and wrapper object (NICAR 2026+)
        if isinstance(data, list):
            sessions = data
        elif isinstance(data, dict):
            sessions = data.get("sessions", [])
            # Use timezone from metadata if available
            tz_name = data.get("timezone")
            if tz_name:
                self.timezone = tz_name
        else:
            sessions = []

        self.logger.info(f"Found {len(sessions)} sessions")

        events = []
        for session in sessions:
            event = self._parse_session(session)
            if event:
                events.append(event)
        return events

    def _parse_session(self, session: dict) -> Optional[dict[str, Any]]:
        title = session.get("session_title", "").strip()
        if not title or session.get("canceled"):
            return None

        # Parse start/end times (ISO 8601 UTC, with or without milliseconds)
        dtstart = self._parse_iso(session.get("start_time"))
        dtend = self._parse_iso(session.get("end_time"))
        if not dtstart:
            return None

        # Room: object (IRE 2025) or string (NICAR 2026)
        room = session.get("room", "")
        if isinstance(room, dict):
            room = room.get("room_name", "")

        # Session type prefix
        session_type = session.get("session_type", "")
        if session_type:
            title = f"[{session_type}] {title}"

        # Description: may be plain text or HTML
        description = session.get("description", "")
        if "<" in description:
            description = BeautifulSoup(description, "html.parser").get_text(
                separator="\n", strip=True
            )

        # Speakers: full objects (IRE 2025) or hash IDs (NICAR 2026)
        speakers = session.get("speakers", [])
        speaker_names = []
        for s in speakers:
            if isinstance(s, dict):
                name = f"{s.get('first', '')} {s.get('last', '')}".strip()
                if s.get("affiliation"):
                    name += f" ({s['affiliation']})"
                if name:
                    speaker_names.append(name)
        if speaker_names:
            description = f"Speakers: {', '.join(speaker_names)}\n\n{description}".strip()

        # Tracks
        tracks = session.get("tracks") or session.get("track", "")
        if isinstance(tracks, list):
            tracks = ", ".join(tracks)

        skill = session.get("skill_level", "")
        meta_parts = [p for p in [tracks, f"Skill: {skill}" if skill else ""] if p]
        if meta_parts:
            description = f"{description}\n\n{' | '.join(meta_parts)}".strip()

        conf_slug = self.conference
        session_id = session.get("session_id", "")
        url = f"https://schedules.ire.org/{conf_slug}#session-{session_id}" if session_id else ""

        return {
            "title": title,
            "dtstart": dtstart,
            "dtend": dtend,
            "location": room,
            "description": description,
            "url": url,
            "uid": f"{conf_slug}-{session_id}@{self.domain}" if session_id else None,
        }

    def _parse_iso(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        # Strip milliseconds for consistent parsing
        value = re.sub(r"\.\d+Z$", "Z", value)
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt.astimezone(ZoneInfo(self.timezone))
        except (ValueError, TypeError):
            return None

    @classmethod
    def parse_args(cls, description=None):
        parser = argparse.ArgumentParser(
            description="Scrape IRE/NICAR conference schedule from S3 JSON"
        )
        parser.add_argument("--output", "-o", type=str, help="Output filename")
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")
        parser.add_argument(
            "--conference",
            type=str,
            default="ire-2025",
            help="Conference slug (e.g., ire-2025, nicar-2026)",
        )
        return parser.parse_args()

    @classmethod
    def main(cls):
        cls.setup_logging()
        args = cls.parse_args()
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        scraper = cls(conference=args.conference)
        scraper.run(args.output)


if __name__ == "__main__":
    IREScheduleScraper.main()
