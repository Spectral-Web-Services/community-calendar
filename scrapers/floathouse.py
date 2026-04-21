#!/usr/bin/env python3
"""
Scraper for The Floathouse Petaluma events.
https://www.thefloathousepetaluma.org/events

Squarespace events collection. Uses ?format=json which exposes an
'upcoming' array of event objects.
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from lib.squarespace import SquarespaceScraper


class FloathouseScraper(SquarespaceScraper):
    name = "The Floathouse Petaluma"
    domain = "thefloathousepetaluma.org"
    collection_url = "https://www.thefloathousepetaluma.org/events"
    default_location = "The Floathouse Petaluma, 95 Lakeville St, Petaluma, CA 94952"


if __name__ == '__main__':
    FloathouseScraper.main()
