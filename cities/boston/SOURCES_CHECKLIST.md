# Boston Sources Checklist

Focus: Theater (initial phase)

## Currently Implemented (12 sources)

### Theater — ICS Feeds
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| ArtsEmerson | WordPress Tribe ICS | 1+ | Emerson College's performing arts org |
| Tufts TDPS | Trumba ICS | 9 | Theater, dance, and performance studies at Tufts |

### Theater — Custom Scrapers
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| American Repertory Theater | art_calendar.py (embedded JSON) | 38 | Embedded FullCalendar JSON in /calendar/ page |
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
| Company One Theatre | companyone.org | WordPress/Divi, client-rendered, no calendar structure |
| Front Porch Arts Collective | frontporcharts.org | Weebly, GiveButter ticketing, only 2 upcoming performances |

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
| Boston Center for the Arts | Residencies and exhibitions, not theater productions |
| Wellesley Repertory Theatre | Squarespace without events collection; SimpleTix; only 1 production at a time |

## To Investigate (future phases)
- [ ] Company One Theatre — needs custom WordPress/Divi scraper
- [ ] Front Porch Arts Collective — Weebly/GiveButter, low volume
- [ ] Ticketmaster venue IDs for Citizens Opera House, Emerson Colonial (for richer data)
- [ ] Huntington calendar Vue API
- [ ] Music venues, comedy clubs, community events, meetups, libraries
