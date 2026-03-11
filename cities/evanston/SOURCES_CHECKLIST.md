# Evanston, IL — Sources Checklist

8-mile radius from Evanston, covering Skokie, Wilmette, Winnetka, Kenilworth, Glencoe, Glenview, Morton Grove, Niles, Northfield, Lincolnwood.

## Currently Implemented

### ICS Feeds
| Source | Feed URL | Notes |
|--------|----------|-------|
| North Shore Center for the Performing Arts | `https://www.northshorecenter.org/events/?ical=1` | WordPress + The Events Calendar; 28 events |
| Evanston History Center | `https://evanstonhistorycenter.org/calendar-of-events/?ical=1` | WordPress + The Events Calendar |
| Skokie Public Library | `https://www.skokielibrary.info/events/feed/ical` | Drupal + Sabre VObject; library events |
| Morton Grove Public Library | `https://www.mgpl.org/events/feed/ical` | Sabre VObject; library events |
| Oakton Community College | `https://events.oakton.edu/calendar/1.ics` | Localist; ~200 calendar resources |

### Meetup Groups
| Source | Feed URL | Notes |
|--------|----------|-------|
| Alliance Française du North Shore | `https://www.meetup.com/afnorthshore/events/ical/` | Cultural events |
| Evanston Board Games Meetup | `https://www.meetup.com/evanston-beer-and-board-games-meetup/events/ical/` | 3 events, meets at Sketchbook Brewing |
| Evanston Writers Workshop | `https://www.meetup.com/evanstonwriters/events/ical/` | 9 events, poetry/fiction/screenwriting |
| Black Girls Read Book Club | `https://www.meetup.com/black-girls-read-book-club/events/ical/` | 2 events, meets in Evanston |

## Discovered - Non-Starters

| Source | Reason |
|--------|--------|
| City of Evanston | cityofevanston.org events pages return 404 |
| Evanston Public Library | BiblioCommons platform, no ICS/RSS feed |
| Northwestern PlanIt Purple | No feed export, browse-only calendar |
| Northwestern Bienen School of Music | No feed export visible |
| Block Museum (Northwestern) | Calendar page 404 |
| Illinois Holocaust Museum (Skokie) | WordPress but no ICS feed at ?ical=1 |
| Chicago Botanic Garden (Glencoe) | Drupal, no feeds exposed |
| Evanston Art Center | Drupal, no feeds |
| Glenview Park District | Individual ICS download only, no feed |
| Skokie Park District | Custom system, no feeds |
| SPACE Evanston | Ticketmaster, no feeds |
| Temperance Beer | 401 Unauthorized |
| Sketchbook Brewing | No events page found |
| McGaw YMCA | No feed visible |
| Downtown Evanston | Custom site, no feeds |
| Evanston RoundTable | Embedded calendar with ad-blocker issues |
| Wilmette Village | Redirects, 404 |
| Evanston Art Center Eventbrite | Organizer page 404 |
| Wilmette Public Library | Communico platform with ICS/RSS disabled |
| Writers Theatre | Custom CMS + proprietary ticketing (my.writerstheatre.org) |
| Music Theater Works | Custom site, no feeds or calendar |

## To Investigate

- [ ] Evanston Public Library via BiblioCommons API or RSS
- [ ] Glenview Public Library
- [ ] Lincolnwood Public Library
- [ ] Evanston Folk Festival
- [ ] Northwestern athletics (nuwildcats.com was ECONNREFUSED)
- [ ] Beth Emet Synagogue
- [ ] More Meetup groups in the area
- [ ] More Eventbrite organizers in Evanston
- [ ] Evanston Farmers Market
- [ ] Celtic Knot Public House events
- [ ] Niles Public Library
- [ ] Northfield Township events
