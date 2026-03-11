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

### Meetup Groups
| Source | Feed URL | Notes |
|--------|----------|-------|
| Alliance Française du North Shore | `https://www.meetup.com/afnorthshore/events/ical/` | Cultural events |
| Evanston Board Games Meetup | `https://www.meetup.com/evanston-beer-and-board-games-meetup/events/ical/` | 3 events, meets at Sketchbook Brewing |
| Evanston Writers Workshop | `https://www.meetup.com/evanstonwriters/events/ical/` | 9 events, poetry/fiction/screenwriting |
| Black Girls Read Book Club | `https://www.meetup.com/black-girls-read-book-club/events/ical/` | 2 events, meets in Evanston |
| Chicago Drum Circle | `https://www.meetup.com/chicagodrumcircle/events/ical/` | 10 events, meets at Double Clutch Brewing |
| Evanston Trivia Nerds | `https://www.meetup.com/evanston-trivia-nerds-meetup/events/ical/` | 1 event, meets at Stacked and Folded |

## Discovered - Non-Starters

| Source | Reason |
|--------|--------|
| City of Evanston (cityofevanston.org) | Revize CMS, no standard feeds |
| Evanston Public Library | BiblioCommons platform, no ICS/RSS feed |
| Northwestern PlanIt Purple | No feed export, browse-only calendar |
| Northwestern Bienen School of Music | No feed export visible |
| Block Museum (Northwestern) | Calendar page 404 |
| Illinois Holocaust Museum (Skokie) | WordPress but no ICS feed at ?ical=1 |
| Chicago Botanic Garden (Glencoe) | Drupal, no feeds exposed |
| Evanston Art Center | Drupal, no feeds |
| Glenview Park District | Individual ICS download only, no feed |
| Skokie Park District | Custom system, no feeds |
| SPACE Evanston | Squarespace + Ticketmaster, no feeds |
| Temperance Beer | 401 Unauthorized |
| Sketchbook Brewing | No events page found |
| McGaw YMCA | No feed visible |
| Downtown Evanston | Custom site, no feeds |
| Evanston RoundTable | Embedded calendar, no ICS at ?ical=1 |
| Wilmette Village | Redirects, 404 |
| Evanston Art Center Eventbrite | Organizer page 404 |
| Wilmette Public Library | Communico platform with ICS/RSS disabled |
| Writers Theatre | Custom CMS + proprietary ticketing |
| Music Theater Works | Custom site, no feeds |
| Glenview Public Library | BiblioCommons, no ICS feed |
| Niles-Maine District Library | Communico with RSS/ICS disabled |
| Evanston Folk Festival | Single annual event, no calendar feed |
| Glencoe Public Library | 404 |
| Double Clutch Brewing | Wix, no events page |

## To Investigate

- [ ] City of Evanston Revize calendar scraper (cityofevanston.org/calendar.php)
- [ ] Northwestern athletics (nuwildcats.com was ECONNREFUSED)
- [ ] More Eventbrite organizers in Evanston
- [ ] Evanston Farmers Market
- [ ] Celtic Knot Public House events
- [ ] Skokie Village other calendar categories (Health/Human Services, Public Meetings, Sustainability, Storefront)
