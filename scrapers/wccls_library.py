#!/usr/bin/env python3
"""WCCLS (Washington County Cooperative Library Services) scraper using generic Bibliocommons base."""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from lib.bibliocommons import BibliocommonsEventsScraper


class WCCLSLibraryScraper(BibliocommonsEventsScraper):
    name = "WCCLS Libraries"
    domain = "wccls.bibliocommons.com"
    timezone = "America/Los_Angeles"
    library_slug = "wccls"

    page_limit = 100
    max_pages = 80


if __name__ == "__main__":
    WCCLSLibraryScraper.main()
