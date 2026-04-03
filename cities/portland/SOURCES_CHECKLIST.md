# Portland Sources Checklist

## Currently Implemented (95 sources)

### Aggregators / Community Calendars
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| KPTV Community Calendar | Tockify ICS | 160 | FOX 12 Oregon community events calendar |
| Travel Portland | WP REST API scraper | ~750 (16k instances) | Tourism board aggregator; recurring events expanded to instances |

### Venues & Institutions
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| The Old Church Concert Hall | Tockify ICS | 59 | Historic Portland concert hall |
| Portland Art Museum | WordPress Tribe ICS | 30 | Art exhibitions, performances |
| Literary Arts | WordPress Tribe ICS | 30 | Readings, writing workshops |
| Portland Japanese Garden | WordPress WP Events Manager | 161 (2026) | Gardens, cultural events |
| Calagator | Custom ICS | 35 | Portland tech community calendar |
| Portland Farmers Market | WordPress Tribe ICS | 3 | 5 market locations, images |
| Hollywood Farmers Market | Squarespace scraper | varies | Music, special events, market events (3 collections) |
| Vancouver Farmers Market | WordPress Tribe ICS | varies | Downtown & East Vancouver markets |
| Oregon City Farmers Market | WordPress Tribe ICS | varies | Winter/summer market at Clackamas CC |
| PDX Jazz | Squarespace scraper | varies | Jazz festival and season concerts |
| Portland Fruit Tree Project | Squarespace scraper | varies | Volunteer harvests, gardening workshops |
| Explore Washington Park | WordPress Tribe ICS | ~31 | Park-wide events; some overlap with Hoyt/Japanese Garden |
| JAMO (Japanese American Museum of Oregon) | WordPress Tribe ICS | varies | Cultural workshops, exhibits, history events |
| Pioneer Courthouse Square | WordPress Tribe ICS | 30 | Free concerts, festivals; images |
| Portland Saturday Market | Squarespace scraper | 31 | Seasonal market events |
| Portland Saturday Market Stage | Squarespace scraper | 18 | Live music performances |
| Crystal Ballroom | WordPress Tribe ICS | 31 | McMenamins venue; images |
| Lan Su Chinese Garden | WordPress Tribe ICS | 30 | Tea tastings, cultural events; images |
| Hoyt Arboretum | WordPress Events Manager | 50 | Nature walks, forest bathing; images |
| Ananda Portland | WordPress Events Manager | 50 | Meditation, yoga, kirtan |
| PDX Parent | WordPress Tribe ICS | 30 | Family events calendar |
| Portland Public Schools | Google Calendar | 12 | School district calendar |
| EMSWCD | WordPress Tribe ICS | 4 | Workshops, meetings (soil & water conservation) |
| Portland Parks Foundation | Squarespace scraper | 3 | Park celebrations, volunteer events |
| Rockwood Market Hall | Squarespace scraper | varies | Community markets, live music, Gresham area |
| Kickstand Comedy | Squarespace scraper | varies | Improv, standup, sketch comedy (SE Hawthorne) |
| Visit Vancouver WA | Simpleview scraper | 30 | Tourism events, festivals, music (Vancouver WA) |
| OSU Extension Master Gardeners | osu_extension.py scraper | 11 | Gardening workshops, Metro area MG program |

### Nature & Outdoors
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| Bird Alliance of Oregon | WordPress Tribe ICS | 30 | Birding, nature walks; images |
| Friends of Tryon Creek | Squarespace scraper | 21 | Trail volunteering, nature storytimes |
| Crystal Springs Rhododendron Garden | Squarespace scraper | 3 | Forest therapy, birding walks |
| Friends of Trees (Green Space) | Google Calendar ICS | 75 | Free tree-planting volunteer events |
| Friends of Trees (Neighborhood) | Google Calendar ICS | 60 | Free neighborhood tree-planting events |
| Oregon Zoo | oregon_zoo.py scraper | 1-3 | Family events, seasonal; images |

### Libraries
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| WCCLS Libraries | BiblioCommons scraper | 1,970 | 13+ branches, storytimes, classes, book clubs |
| Multnomah County Library | multcolib.py scraper | 1,795 | Drupal Views AJAX, all branches; images |

### Eventbrite Organizers (free events)
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| Trailkeepers of Oregon | Eventbrite scraper | 11 | Free trail volunteer events; images |
| Northwest Trail Alliance | Eventbrite scraper | 11 | Free mountain bike trail building; images |
| Portland Nursery | Eventbrite scraper | 4 | Free gardening classes; images |
| Habitat for Humanity Portland | Eventbrite scraper | 3 | Free homeownership education; images |
| WonderLove PDX | Eventbrite scraper | 2 | Culture/food/entertainment hub; markets, festivals |

### Ticketmaster Venues (3)
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| Moda Center | Ticketmaster scraper | varies | Trail Blazers, concerts, family shows; images |
| Veterans Memorial Coliseum | Ticketmaster scraper | varies | Winterhawks, concerts, trade shows; images |
| Theater of the Clouds | Ticketmaster scraper | varies | Comedy, mid-size concerts; images |

### Songkick Music Venues (8)
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| Revolution Hall | Songkick scraper | 5 | Major concert venue |
| Mississippi Studios | Songkick scraper | 5 | Indie music |
| Wonder Ballroom | Songkick scraper | 5 | Concerts |
| Aladdin Theater | Songkick scraper | 4 | Historic music venue |
| Hawthorne Theatre | Songkick scraper | 5 | Rock/indie |
| Arlene Schnitzer Concert Hall | Songkick scraper | 5 | Portland'5 venue |
| Alberta Rose Theatre | Songkick scraper | 4 | Music, comedy, spoken word |
| Keller Auditorium | Songkick scraper | 2 | Portland'5 venue |

### Universities
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| University of Portland | Localist ICS | 351 | Full campus calendar |
| Reed College | Localist ICS | 370 | Lectures, performances, community events |
| Lewis & Clark College | LiveWhale ICS | 296 | Symposiums, concerts, lectures |
| Portland Community College | LiveWhale ICS | 326 | Multi-campus events |
| OHSU Library Workshops | LibCal ICS | 30 | Library workshops |

### Athletics
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| PSU Vikings | SIDEARM ICS | varies | All PSU athletics |
| UP Pilots | SIDEARM ICS | varies | All UP athletics |
| Portland Timbers | Google Calendar | varies | MLS soccer schedule |
| Portland Thorns FC | Google Calendar | varies | NWSL soccer schedule |

### Government
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| Oregon Metro | Legistar scraper | varies | Metro Council meetings |
| Portland Community Events | portland_gov.py (type 329) | 59 | City community events; images, locations |
| Portland Volunteer Events | portland_gov.py (type 364) | 92 | City volunteer events; images, locations |
| Portland Classes & Activities | portland_gov.py (type 583) | 33 | City classes and activities; images |
| Portland Public Meetings | portland_gov.py (type 333) | 85 | Public meetings; locations |
| Portland Council Meetings | portland_gov.py (type 651) | 49 | City council meetings |

### Meetup Groups - Tech (5)
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| Portland Code & Coffee | Meetup ICS | 10 | Biweekly dev meetups |
| CODE PDX | Meetup ICS | 1 | Civic tech / Code for America |
| PADNUG | Meetup ICS | 10 | .NET developer user group |
| PDXCPP | Meetup ICS | 10 | C++ user group |
| The Tech Academy | Meetup ICS | 2 | Coding workshops |

### Meetup Groups - Hiking/Outdoor (5)
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| Portland Outdoors (20s-30s) | Meetup ICS | 10 | Hikes, varying difficulty |
| Portland Hiking Meetup | Meetup ICS | 10 | Oregon & SW Washington trails |
| Women's Wednesday Wanderers | Meetup ICS | 2 | Women's monthly hikes |
| Portland 20s-30s Coffee, Bars, Hiking | Meetup ICS | 8 | Social + outdoor |
| Portland City Trail Walking | Meetup ICS | 10 | Trail & neighborhood walks |

### Meetup Groups - Running/Fitness (5)
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| Northwest Trail Runners | Meetup ICS | 3 | Forest Park trail runs |
| Portland Trail Runners | Meetup ICS | 4 | Saturday morning trail runs |
| Portland Running Co. | Meetup ICS | 10 | Multiple weekly group runs |
| SlowPo Runners | Meetup ICS | 10 | Slower-pace inclusive runs |
| Portland Fun Run | Meetup ICS | 10 | Casual fun-focused runs |

### Meetup Groups - Social/Games/Books (4)
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| PDX Board Games & RPGs | Meetup ICS | 10 | Thursday game nights |
| PDX Silent Book Club | Meetup ICS | 1 | Silent reading meetups |
| Silent Book Club Portland | Meetup ICS | 1 | Silent reading meetups |
| It's More Than Just Reading Books | Meetup ICS | 2 | Book + adventure group |

### Meetup Groups - Arts/Creative (4)
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| Portland Coffee & Sketch Club | Meetup ICS | 10 | Sketching meetups, all levels |
| Portland Art Guild | Meetup ICS | 3 | Low-cost art classes |
| Portland Arts & Craft | Meetup ICS | 10 | Fused glass, hands-on crafts |
| Pop Up Paint and Sip | Meetup ICS | 6 | Paint party events |

### Meetup Groups - Community/Wellness/Family (4)
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| Portland Free & Community | Meetup ICS | 10 | Free community events, wellness |
| Decompress + Connect Meditation | Meetup ICS | 10 | Free meditation sessions |
| Portland Active Dads | Meetup ICS | 1 | Dads + kids outdoor activities |
| Contra Dancing | Meetup ICS | 2 | Saturday contra dances |

## Discovered - Needs Scraper
| Source | URL | Notes |
|--------|-----|-------|
| Portland State University | pdx.edu/calendar/month | Drupal, per-event "Add to Calendar" only |
| OMSI | omsi.edu/whats-on/ | WordPress, REST API blocked by security plugin |
| Oregon Symphony | orsymphony.org/calendar/ | No feeds found |
| Powell's Books | powells.com/events | Blocks automated access (403) |
| Portland Center Stage | pcs.org/events | Custom CMS, no feeds |
| Helium Comedy Club | portland.heliumcomedy.com | SeatEngine ticketing, JSON-LD available |
| Hollywood Theatre | hollywoodtheatre.org | Cloudflare-blocked |
| Q Center | pdxqcenter.org/calendar | Wix, no feeds |
| The People's Courts | thepeoplescourts.com/tpc-calendar | WordPress + Elfsight widget, no ICS |

| Beaverton Gov Events | beavertonoregon.gov/482/Events | CivicPlus, no iCalendar module |
| Rockwood Common | tools.rockwoodcommon.org/events | Lend Engine, JSON endpoint only |

## Non-Starters
| Source | Reason |
|--------|--------|
| Portland city government (Legistar) | Not on Legistar; now scraped via portland_gov.py |
| Portland Parks & Recreation | portland.gov/parks/events | Covered by portland_gov.py type filters |
| City of Portland Arts | portland.gov/arts/arts-events | Covered by portland_gov.py community events |
| Concordia University Portland | Closed permanently in 2020 |
| Portland Children's Museum | Closed permanently in 2021 |
| Doug Fir Lounge | Relocating, no events currently |
| Williams-Sonoma Brewery Blocks | 403 blocked, proprietary platform, no feeds |
| Portland Plazas Events | Manual info page updated monthly, not a real event calendar |

## To Investigate

### High-Value (from Stumptown Savings newsletter, March 2026)
- [x] PDX Jazz (pdxjazz.org) — Squarespace events collection added
- [x] Explore Washington Park (explorewashingtonpark.org) — WordPress Tribe ICS added (~31 events, some overlap with Hoyt/Japanese Garden)
- [x] Portland Fruit Tree Project (portlandfruit.org) — Squarespace events collection added
- [x] JAMO (jamo.org) — WordPress Tribe ICS added
- [x] OSU Extension (extension.oregonstate.edu) — Custom scraper added, filtered to MG-Metro (11 events)
- [x] WonderLove PDX (wonderlovepdx.com) — Added via Eventbrite organizer scraper
- [ ] People's Food Co-op (peoples.coop) — Squarespace, community room closed, no events listed
- [ ] Rockwood Common (tools.rockwoodcommon.org) — Lend Engine tool library, no calendar feeds
- [ ] PDX Night Market (pdxnm.com) — Wix, no feeds
- [ ] Portland Dining Month (pdxdiningmonth.com) — seasonal restaurant event
- [ ] PNW CSA Coalition (pnwcsa.org) — CSA share fair
- [ ] First Friday PDX (firstfridaypdx.org) — site down (ECONNREFUSED)

### Farmers Markets (from Stumptown Savings newsletter)
- [x] Hollywood Farmers Market (hollywoodfarmersmarket.org) — Squarespace, 3 event collections added
- [x] Vancouver Farmers Market (vancouverfarmersmarket.org) — WordPress Tribe ICS added
- [x] Oregon City Farmers Market (orcityfarmersmarket.com) — WordPress Tribe ICS added
- [ ] Beaverton Farmers Market (beavertonfarmersmarket.com) — Wix, no feeds
- [ ] Hillsdale Farmers Market (hillsdalefarmersmarket.com) — Squarespace, no events collection
- [ ] Montavilla Farmers Market (montavillamarket.org) — Squarespace, static schedule only
- [ ] Sunnyside Farmers Market (sunnysidefarmersmarkets.com) — 403 blocked
- [ ] Woodlawn Farmers Market (woodlawnfarmersmarket.org) — Squarespace, no events collection

### Previously Identified
- [ ] Portland'5 Centers full calendar (Drupal scraper for non-music events)
- [ ] PDX Pipeline (blog RSS, not structured events)
- [ ] EverOut Portland (everout.com) — 10 links in newsletter, aggregator
- [ ] DoPDX
- [ ] Portland Shambhala Center (Cloudflare-blocked, likely has ICS)
- [ ] Hands On Greater Portland (volunteer platform)

### New Requests (March 2026) — Resolved
| Source | URL | Resolution |
|--------|-----|------------|
| EMSWCD | emswcd.org/events | **Added** — WordPress Tribe ICS feed (4 events, workshops & meetings) |
| Portland Parks Foundation | portlandpf.org/upcoming-events | **Added** — Squarespace scraper (3 events, park celebrations) |
| Rockwood Market Hall | rockwoodmarkethall.com/events | **Added** — Squarespace scraper (markets, live music, community events) |
| Kickstand Comedy | kickstandcomedy.org/shows | **Added** — Squarespace scraper (improv, standup, sketch) |
| Explore Washington Park | explorewashingtonpark.org/events/list/?ical=1 | **Duplicate** — already in feed (line 108) |
| PDX Jazz | pdxjazz.org/events | **Duplicate** — already in feed (Squarespace scraper, line 79) |
| ResourcefulPDX | portland.gov/bps/sustainability/resourcefulpdx/events | **Already covered** — captured by portland_gov.py type 329 |
| Portland Center Stage | pcs.org/events | Custom CMS, no feeds; partially covered via Travel Portland (~27 events) |
| OSU Extension Metro | extension.oregonstate.edu/program/all/mg/events | **Added** — custom scraper, filtered to Metro group (11 events) |
| The People's Courts | thepeoplescourts.com/tpc-calendar | WordPress + Elfsight widget, no ICS; needs custom scraper |
| Beaverton Gov Events | beavertonoregon.gov/482/Events | CivicPlus, no iCalendar module exposed; needs custom scraper |
| Visit Vancouver WA | visitvancouverwa.com/events | **Added** — Simpleview scraper (30 events, JSON-LD from detail pages) |
| Portland Plazas | portland.gov/transportation/planning/plazas/events | **Non-starter** — manual info page, updated monthly, not a calendar |
| Williams-Sonoma Brewery Blocks | williams-sonoma.com/stores/us-or-portland-brewery-blocks/ | **Non-starter** — 403 blocked, proprietary platform, no feeds |
| Rockwood Common | tools.rockwoodcommon.org/events | Lend Engine platform, JSON endpoint only, no ICS; needs custom scraper |