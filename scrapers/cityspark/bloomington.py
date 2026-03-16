#!/usr/bin/env python3
"""Scraper for Bloomington events via CitySpark API."""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])  # Add scrapers/ to path

from lib.cityspark import CitySparkScraper


class BloomingtonCitySparkScraper(CitySparkScraper):
    """Scraper for Bloomington, IN events via CitySpark."""

    name = "CitySpark Bloomington"
    domain = "cityspark.com"
    timezone = "America/Indiana/Indianapolis"
    api_slug = "CitySpark"
    ppid = 5
    lat = 39.1653
    lng = -86.5264
    distance = 15
    calendar_url = "https://cityspark.com/calendar/"


if __name__ == '__main__':
    BloomingtonCitySparkScraper.main()
