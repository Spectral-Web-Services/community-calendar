#!/usr/bin/env python3
"""
Scraper for Hall of the Above events (Petaluma).
https://www.halloftheabove.com/events

Squarespace events collection lives at /event-database; the public
/events page is a summary grid that links into it. The JSON API at
/event-database?format=json returns the 'upcoming' array.
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from lib.squarespace import SquarespaceScraper


class HallOfTheAboveScraper(SquarespaceScraper):
    name = "Hall of the Above"
    domain = "halloftheabove.com"
    collection_url = "https://www.halloftheabove.com/event-database"
    default_location = "Hall of the Above, 401 N McDowell Blvd, Petaluma, CA 94954"


if __name__ == '__main__':
    HallOfTheAboveScraper.main()
