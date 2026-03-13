# Publisher Resources — Sources Checklist

Aggregates workshops, training, and events for local news organizations and journalists.
No geolocation filtering applied.

## Currently Implemented

### ICS Feeds
- [ ] INN (Institute for Nonprofit News) — `https://inn.org/events/list/?ical=1` (WordPress Tribe Events)
- [ ] SPJ (Society of Professional Journalists) — `webcal://calendar.spjnetwork.org/calendar.php`
- [ ] Poynter Institute — `https://www.poynter.org/events/?ical=1` (WordPress Tribe Events)
- [ ] NAHJ (National Assoc. of Hispanic Journalists) — `https://nahj.org/events/?ical=1` (WordPress Tribe Events)
- [ ] NLGJA (Assoc. of LGBTQ+ Journalists) — `https://www.nlgja.org/events/?ical=1` (WordPress Tribe Events)
- [ ] AHCJ (Assoc. of Health Care Journalists) — `https://healthjournalism.org/events/?ical=1` (WordPress Tribe Events)
- [ ] SABEW (Soc. for Advancing Business Editing & Writing) — `https://sabew.org/?post_type=tribe_events&ical=1&eventDisplay=list` (WordPress Tribe Events)
- [ ] Hacks/Hackers — `https://api2.luma.com/ics/get?entity=calendar&id=cal-09kcgQfLYGyy2JP` (Luma calendar ICS)

### Google Calendar
- [ ] Tiny News Members Only — `https://calendar.google.com/calendar/ical/c_3ef2026db19c41c73cb8ed72bbde7f163008de761ce942a9ad334f5b8993e652%40group.calendar.google.com/public/basic.ics`
- [ ] Journalism Internship & Fellowship Deadlines — `https://calendar.google.com/calendar/ical/er06vtjd12h86b4rej5bts6p6c%40group.calendar.google.com/public/basic.ics`

### Scrapers
- [ ] SEJ (Society of Environmental Journalists) — `sej_calendar.py` (RSS calendar at `sej.org/rss_calendar`)
- [ ] IRE/NICAR Conference Schedules — `ire_schedule.py` (S3 JSON, updated per conference cycle)
- [ ] SJN (Solutions Journalism Network) — `sjn_events.py` (Drupal HTML scraper at `solutionsjournalism.org/events`)
- [ ] PEN America — `pen_america.py` (WordPress REST API at `pen.org/wp-json/wp/v2/event`) + `eventbrite.py` (organizer `31882531335`)
- [ ] NABJ (National Assoc. of Black Journalists) — `nabj_events.py` (Wild Apricot RSS at `nabj.org/resource/rss/events.rss`)
- [ ] American Press Institute — `eventbrite.py` (Eventbrite organizer `59619554833`; 0 upcoming as of 2026-03)

- [ ] Center for Cooperative Media — `eventbrite.py` (Eventbrite organizer `5988913981`)

## Investigated — Possible with Scraper
- **RJI (Reynolds Journalism Institute)** — ICS feed at `calendar.missouri.edu/live/ical/events/group/Reynolds%20Journalism%20Institute/` works but very low volume (2 events), Columbia MO only
- [ ] LION Publishers — `lion_publishers.py` (HTML scraper, WordPress free-form events page)
- [ ] Editor & Publisher — `editor_publisher.py` (HTML scraper, industry conference calendar)
- [ ] Center for Cooperative Media — `eventbrite.py` (Eventbrite organizer scraper)
- [ ] Associated Press — `eventbrite.py` (Eventbrite organizer scraper)
- [ ] ONA (Online News Association) — `ona_events.py` (HTML scraper, Novi AMS events page)

### Scrapable (no feeds, but server-rendered HTML)
- [ ] Knight Center for Journalism — `https://journalismcourses.org/course-library/` (WordPress/Elementor, paginated course cards with dates, instructors, pricing)

## Investigated — Not Viable

- **LION Publishers** — Now implemented as scraper (see above)
- **American Journalism Project** — No public events; invitation-only (AJPalooza)
- **Virginia Local News Project** — No events calendar; runs ongoing programs only
- **GIJN** — Site returns 403 to all automated requests; no public feeds
- **East-West Center** — Cloudflare 403 on all automated access
- **The Open Notebook** — Trainings are custom-booked/on-demand, no scheduled events
- **Trusting News** — Events announced via blog posts with Zoom links, no structured data
- **ONA** — No ICS/RSS feeds; Novi AMS platform — but events page is scrapable (see above)
- **Knight Foundation** — Events infrastructure under development, not live
- **RTDNA** — No public feeds; Novi AMS platform, /events/feed returns 500
- **National Press Club** — Custom calendar grid, no feeds
- **EWA** — No feeds; custom WordPress events with AJAX
- **NABJ** — ~~Site returns 403 to automated access~~ Moved to Scrapers (RSS feed at CDN bypasses Cloudflare)
- **AAJA** — No event-specific feeds; RSS has news only
- **Inside the Newsroom (Substack)** — Blog post listing deadlines in prose; no structured data or feeds
- **Hearst Awards** — TLS certificate error (ERR_TLS_CERT_ALTNAME_INVALID); site inaccessible
- **Editor & Publisher** — Now implemented as scraper (see above)
- **SPJ Freelance Calendar** — Same feed as SPJ already implemented (`webcal://calendar.spjnetwork.org/calendar.php`)
- **Trauma Journalism** — WordPress custom calendar, no ICS/RSS export; stale events only
- **IRE** — WordPress (Beaver Builder) but no ICS export; `?ical=1` returns HTML; RSS is blog posts only; events load via JavaScript (not scrapable without headless browser)
- **CPJ** — WordPress, no events ICS feed; events page is server-rendered but stale (last event 2018)
- **IWMF** — Returns 403 to automated access
- **Knight Center (journalismcourses.org)** — No calendar feeds; WordPress/WooCommerce — but course library is scrapable (see above)
- **Pulitzer Center** — Returns 403 to automated access
- **TCIJ (Centre for Investigative Journalism)** — Returns 403 to automated access

## To Investigate

- Hacks/Hackers events
- SRCCON / OpenNews
- Lenfest Institute
- Report for America
- Solutions Journalism Network
