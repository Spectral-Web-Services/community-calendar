# Boston Sources Checklist

Focus: Theater (initial phase)

## Currently Implemented (10 sources)

### Theater — ICS Feeds
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| ArtsEmerson | WordPress Tribe ICS | 1+ | Emerson College's performing arts org |

### Theater — Custom Scrapers
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| BU School of Theatre | bu_cfa.py (topic 8637) | 23 | WordPress AJAX calendar, shows + student productions |

### Theater — OvationTix Venues
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| Central Square Theater | ovationtix.py (org 2462) | 46 | 2 productions, individual performances scraped |
| Actors' Shakespeare Project | ovationtix.py (org 921) | 22 | OvationTix org 921 |
| Wheelock Family Theatre | ovationtix.py (org 177) | 15 | Mix of productions and children's classes |

### Theater — Songkick Venues
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| Citizens Opera House | Songkick scraper | 3 | Broadway touring house (was Citizens Bank Opera House) |
| Emerson Colonial Theatre | Songkick scraper | 8 | Broadway touring house, ATG Tickets |
| Huntington Theatre | Songkick scraper | 3 | Major regional theater |
| Lyric Stage Company | Songkick scraper | 1 | 244-seat intimate theater |

## Discovered - Needs Investigation
| Source | URL | Notes |
|--------|-----|-------|
| American Repertory Theater (A.R.T.) | americanrepertorytheater.org | WordPress, JSON in /calendar page, self-hosted ticketing |
| Company One Theatre | companyone.org | WordPress/Divi, performs at BCA |
| Boston Center for the Arts | bostonarts.org | WordPress, Salesforce ticketing |
| Tufts TDPS | tdps.tufts.edu | Trumba calendar integration |
| Wellesley Repertory Theatre | wellesleyrepertorytheatre.org | Squarespace, SimpleTix |
| Front Porch Arts Collective | frontporcharts.org | Weebly, GiveButter ticketing |

## Non-Starters
| Source | Reason |
|--------|--------|
| SpeakEasy Stage Company | WordPress Tribe installed; ICS (`?ical=1`) returns HTML not ICS; webcal:// URL returns empty ICS (0 events via curl and Google Calendar import) |
| Central Square Theater EventON | EventON 5.0.2 AJAX requires session-bound nonce; can't scrape via requests. Using OvationTix instead |
| Boston University CFA (generic) | Use bu_cfa.py with --topic filter instead; generic page mixes all arts |
| Emerson College events | Empty events page; use ArtsEmerson instead |
| Cambridge Multicultural Arts Center | Site down (ECONNREFUSED) |
| Open Theater Project | Site down (ECONNREFUSED) |
| Calderwood Pavilion | Not separate entity; events listed by resident companies |

## To Investigate (future phases)
- [ ] Ticketmaster venue IDs for Citizens Opera House, Emerson Colonial (for richer data)
- [ ] A.R.T. calendar page JSON scraper
- [ ] Huntington calendar Vue API
- [ ] Music venues, comedy clubs, community events, meetups, libraries
