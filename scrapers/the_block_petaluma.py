#!/usr/bin/env python3
"""
Scraper for The Block Petaluma events.
https://www.theblockpetaluma.com/newyears

Site renders events via the Elfsight Event Calendar widget loaded inside
a filesusr.com HTML embed. We hit the Elfsight API directly with the
widget ID extracted from the embed's URL fragments, e.g.
  ...#calendar-5a98f0f4-e510-4ea3-bcba-794725c130dc-event-...
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from lib.elfsight import ElfsightCalendarScraper


class TheBlockPetalumaScraper(ElfsightCalendarScraper):
    name = "The Block Petaluma"
    domain = "theblockpetaluma.com"
    widget_id = "5a98f0f4-e510-4ea3-bcba-794725c130dc"
    source_page = "https://www.theblockpetaluma.com/newyears"


if __name__ == '__main__':
    TheBlockPetalumaScraper.main()
