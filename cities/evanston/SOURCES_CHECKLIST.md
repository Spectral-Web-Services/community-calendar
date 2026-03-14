# Evanston, IL — Sources Checklist

8-mile radius from Evanston, covering Skokie, Wilmette, Winnetka, Kenilworth, Glencoe, Glenview, Morton Grove, Niles, Northfield, Lincolnwood.

## Currently Implemented

### ICS Feeds
| Source | Feed URL | Notes |
|--------|----------|-------|
| North Shore Center for the Performing Arts | `https://www.northshorecenter.org/events/?ical=1` | WordPress + The Events Calendar; 28 events |
| Evanston History Center | `https://evanstonhistorycenter.org/calendar-of-events/?ical=1` | WordPress + The Events Calendar |
| Beth Emet Synagogue | `https://bethemet.org/calendar/?ical=1` | WordPress + The Events Calendar |
| Village of Skokie Community Calendar | `https://www.skokie.org/common/modules/iCalendar/iCalendar.aspx?catID=22&feed=calendar` | CivicPlus; 25 events |
| City of Evanston (Events) | `scrapers/revize.py` (Events category) | Revize CMS JSON API; ~51 events |
| City of Evanston (Meetings) | `scrapers/revize.py` (Meetings category) | Revize CMS JSON API; ~103 events |
| City of Evanston (City Council) | `scrapers/revize.py` (City Council category) | Revize CMS JSON API; ~11 events |
| Chicago Botanic Garden | `scrapers/chicagobotanic.py` | Drupal calendar scraper; ~157 events with images |
| Enjoy Evanston | `tockify.com/api/feeds/ics/enjoyevanston` | Tockify ICS; ~68 events with images (X-TKF-FEATURED-IMAGE) |
| CitySpark Evanston | `scrapers/cityspark/evanston.py` | CitySpark API direct; 5-mile radius; links to cityspark.com |
| Northlight Theatre | `https://www.northlight.org/events/?ical=1` | WordPress + The Events Calendar; ~30 events; Skokie |
| Evanston Made | `https://evanstonmade.org/community-calendar/?ical=1` | WordPress + The Events Calendar; ~30 events; community arts |
| Eisenhower Public Library | `eisenhower.librarycalendar.com/events/feed/ical` | Communico ICS; ~402 events; Norwood Park |
| Visit Chicago North Shore | `scrapers/visitchicagonorthshore.py` | Sitemap + JSON-LD; ~110 events with images; North Shore CVB |
| Evanston American Legion | `scrapers/evanston_legion.py` | Google Calendar ICS, filtered; ~35 events; concerts, community |

### Libraries
| Source | Feed URL | Notes |
|--------|----------|-------|
| Skokie Public Library | `https://www.skokielibrary.info/events/feed/ical` | Drupal + Sabre VObject; 141 events |
| Morton Grove Public Library | `https://www.mgpl.org/events/feed/ical` | Sabre VObject |
| Lincolnwood Public Library | `https://www.lincolnwoodlibrary.org/events/feed/ical` | Sabre VObject |
| Winnetka-Northfield Public Library | `https://www.wnpld.org/events/feed/ical` | Drupal + Sabre VObject |

### Education
| Source | Feed URL | Notes |
|--------|----------|-------|
| Oakton Community College | `https://events.oakton.edu/calendar/1.ics` | Localist; ~200 calendar resources |
| Northwestern University (Arts) | `scrapers/planitpurple.py` (category 2) | PlanIt Purple XML feed; ~20 arts/humanities events |
| District 65 | `scrapers/finalsite.py` | Finalsite CMS; ~18 events (K-8 school calendar) |
| ETHS District 202 | `scrapers/finalsite.py` | Finalsite CMS; ~18 events (high school calendar) |

### Northwestern Athletics (SideArm Sports API)
| Source | Feed URL | Notes |
|--------|----------|-------|
| Football | `nusports.com/api/v2/Calendar/subscribe?type=ics&sportId=2&scheduleId=1742` | 13 events |
| Men's Basketball | `nusports.com/api/v2/Calendar/subscribe?type=ics&sportId=4&scheduleId=1737` | 31 events |
| Women's Basketball | `nusports.com/api/v2/Calendar/subscribe?type=ics&sportId=10&scheduleId=1732` | 31 events |
| Baseball | `nusports.com/api/v2/Calendar/subscribe?type=ics&sportId=1&scheduleId=1739` | 52 events |
| Softball | `nusports.com/api/v2/Calendar/subscribe?type=ics&sportId=11&scheduleId=1741` | |
| Women's Lacrosse | `nusports.com/api/v2/Calendar/subscribe?type=ics&sportId=14&scheduleId=1740` | |
| Men's Soccer | `nusports.com/api/v2/Calendar/subscribe?type=ics&sportId=6&scheduleId=1724` | |
| Women's Soccer | `nusports.com/api/v2/Calendar/subscribe?type=ics&sportId=15&scheduleId=1725` | |
| Volleyball | `nusports.com/api/v2/Calendar/subscribe?type=ics&sportId=18&scheduleId=1722` | |
| Field Hockey | `nusports.com/api/v2/Calendar/subscribe?type=ics&sportId=28&scheduleId=1726` | |
| Wrestling | `nusports.com/api/v2/Calendar/subscribe?type=ics&sportId=30&scheduleId=1738` | |
| Women's Swimming & Diving | `nusports.com/api/v2/Calendar/subscribe?type=ics&sportId=16&scheduleId=1728` | 15 events |

### Meetup Groups
| Source | Feed URL | Notes |
|--------|----------|-------|
| Alliance Française du North Shore | `https://www.meetup.com/afnorthshore/events/ical/` | Cultural events |
| Evanston Board Games Meetup | `https://www.meetup.com/evanston-beer-and-board-games-meetup/events/ical/` | 3 events, meets at Sketchbook Brewing |
| Evanston Writers Workshop | `https://www.meetup.com/evanstonwriters/events/ical/` | 9 events, poetry/fiction/screenwriting |
| Black Girls Read Book Club | `https://www.meetup.com/black-girls-read-book-club/events/ical/` | 2 events, meets in Evanston |
| Chicago Drum Circle | `https://www.meetup.com/chicagodrumcircle/events/ical/` | 10 events, meets at Double Clutch Brewing |
| Evanston Trivia Nerds | `https://www.meetup.com/evanston-trivia-nerds-meetup/events/ical/` | 1 event, meets at Stacked and Folded |

### Eventbrite Organizers (via scraper)
| Source | Eventbrite Organizer URL | Notes |
|--------|--------------------------|-------|
| Bookends & Beginnings | `eventbrite.com/o/bookends-beginnings-30806170182` | ~5 upcoming events; bookstore, author talks |
| The Wine Goddess | `eventbrite.com/o/the-wine-goddess-3108057164` | ~7 events; cooking, wine tastings |
| Hive Center for the Book Arts | `eventbrite.com/o/hive-center-for-the-book-arts-70775141113` | ~4 events; literary, workshops |
| YWCA Evanston/North Shore | `eventbrite.com/o/ywca-evanstonnorth-shore-32016273019` | ~5 events; community, workforce |
| Block Museum of Art | `eventbrite.com/o/the-block-museum-of-art-northwestern-university-9891072212` | ~2 events; film, art |
| Goldfish Swim School Evanston | `eventbrite.com/o/goldfish-swim-school-evanston-17557648193` | ~9 events; family |
| Open Studio Project | `eventbrite.com/o/open-studio-project-72607065443` | ~2 events; community art |
| Prairie Moon | `eventbrite.com/o/prairie-moon-51597641783` | ~1 event; jazz, music |
| Downtown Evanston | `eventbrite.com/o/downtown-evanston-6767069203` | Art receptions, community events |
| The Backyard Barbecue Store | `eventbrite.com/o/dan-marguerite-16757593742` | ~9 events; BBQ classes |
| Booked | `eventbrite.com/o/booked-76549470443` | ~2 upcoming, 25 total; indie bookstore, author events |
| Creative Coworking | `eventbrite.com/o/creative-coworking-23232786009` | ~6 upcoming, 416 total; gallery nights, concerts, dinners; 922 Davis St + Colvin House |
| The Main-Dempster Mile | `eventbrite.com/o/the-main-dempster-mile-13695320840` | ~1 upcoming, 43 total; community crawls, wine walks |
| Northshore Concert Band | `eventbrite.com/o/41593942663` | ~2 upcoming; concerts at Pick-Staiger Hall |
| Stewpendous Productions | `eventbrite.com/o/120935657951` | ~7 upcoming; trivia nights, music bingo at Double Clutch + others |
| Rhythm Revolution | `eventbrite.com/o/33380339107` | ~1 upcoming; drum circles at Double Clutch Brewing |
| Mezcla Media Collective | `eventbrite.com/o/mezcla-media-collective-54754536433` | ~1 upcoming, 41 total; experimental video/art at Evanston Art Center |
| Homeschool + Hue | `eventbrite.com/o/121090594971` | Family meetups for children of color; Zora's Place |
| BLAST Northwestern | `eventbrite.com/o/121097824224` | Dance performances at Ryan Auditorium |

### Ticketmaster (via Discovery API)
| Source | Query | Notes |
|--------|-------|-------|
| Ticketmaster/Evanston | `--promoter-id 6085` | Local promoter (Folk Fest, Winnetka Music Fest); ~3 events |
| Ticketmaster/Evanston Venues | `--venue-id KovZpakJQe --venue-id KovZ917At8O` | SPACE + Cahn Auditorium; ~99 events with images |

## Discovered - Non-Starters

| Source | Reason |
|--------|--------|
| Evanston Public Library | BiblioCommons platform, no ICS/RSS feed |
| Northwestern Bienen School of Music | No feed export visible |

| Illinois Holocaust Museum (Skokie) | WordPress but no ICS feed at ?ical=1 |
| Evanston Art Center | Drupal, no feeds |
| Glenview Park District | Individual ICS download only, no feed |
| Skokie Park District | Custom ASP.NET/Angular system (Americaneagle.com), no feeds or API |

| Temperance Beer | 401 Unauthorized |
| Sketchbook Brewing | No events page found |
| McGaw YMCA | No feed visible |

| Evanston RoundTable | CitySpark widget; same data now sourced directly from CitySpark API |
| Wilmette Village | Redirects, 404 |
| Evanston Art Center Eventbrite | Organizer page 404 |
| Wilmette Public Library | Communico platform with ICS/RSS disabled |
| Writers Theatre | Custom CMS + proprietary ticketing |
| Music Theater Works | Custom site, no feeds |
| Glenview Public Library | BiblioCommons, no ICS feed |
| Niles-Maine District Library | Communico with RSS/ICS disabled |

| Glencoe Public Library | 404 |
| Double Clutch Brewing | Wix, no events page |
| Downtown Evanston (downtownevanston.org) | Vibemap React widget embed, no feeds/API; events covered by Eventbrite |
| North Shore Senior Center | WordPress + Astra/Elementor, no calendar plugin visible |
| Zanies Comedy Club | WordPress/Elementor, no feeds; site data misconfigured (shows Nashville) |
| Pastimes Comics & Games | Site unreachable |

## To Investigate

- [ ] Evanston Farmers Market
- [ ] Celtic Knot Public House events
- [ ] Skokie Village other calendar categories (Health/Human Services, Public Meetings, Sustainability, Storefront)
