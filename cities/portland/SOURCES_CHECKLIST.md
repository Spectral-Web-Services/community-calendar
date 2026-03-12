# Portland Sources Checklist

## Currently Implemented (39 sources)

### Aggregators / Community Calendars
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| KPTV Community Calendar | Tockify ICS | 160 | FOX 12 Oregon community events calendar |

### Venues & Institutions
| Source | Type | Events | Notes |
|--------|------|--------|-------|
| The Old Church Concert Hall | Tockify ICS | 59 | Historic Portland concert hall |
| Portland Art Museum | WordPress Tribe ICS | 30 | Art exhibitions, performances |
| Literary Arts | WordPress Tribe ICS | 30 | Readings, writing workshops |
| Portland Japanese Garden | WordPress WP Events Manager | 161 (2026) | Gardens, cultural events |
| Calagator | Custom ICS | 35 | Portland tech community calendar |

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

## Discovered - Needs Scraper
| Source | URL | Notes |
|--------|-----|-------|
| Portland State University | pdx.edu/calendar/month | Drupal, per-event "Add to Calendar" only |
| Multnomah County Library | events.multcolib.org/events | Communico platform, has ICAL option but dynamic URLs |
| City of Portland | portland.gov/arts/arts-events | Drupal, no feeds. Arts via Cruncho embed |
| Oregon Zoo | oregonzoo.org/events | No feeds found |
| OMSI | omsi.edu/whats-on/ | WordPress, no feeds found |
| Oregon Symphony | orsymphony.org/calendar/ | No feeds found |

## Non-Starters
| Source | Reason |
|--------|--------|
| Portland city government (Legistar) | Not on Legistar; uses own system at portland.gov |
| Concordia University Portland | Closed permanently in 2020 |

## To Investigate
- [ ] Arlene Schnitzer Concert Hall
- [ ] Revolution Hall
- [ ] Doug Fir Lounge
- [ ] Crystal Ballroom
- [ ] Powell's Books
- [ ] Portland Center Stage
- [ ] Portland Saturday Market
- [ ] Pioneer Courthouse Square events
- [ ] Portland Farmers Market
- [ ] Eventbrite Portland (scraper exists in repo)
- [ ] Ticketmaster Portland venues (scraper exists in repo)
- [ ] Songkick Portland venues
- [ ] PDX Pipeline (blog RSS, not structured events)
- [ ] EverOut Portland
- [ ] DoPDX
