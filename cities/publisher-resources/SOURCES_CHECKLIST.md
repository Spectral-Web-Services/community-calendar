# Publisher Resources — Sources Checklist

Aggregates workshops, training, and events for local news organizations and journalists.
No geolocation filtering applied.

## Currently Implemented

### ICS Feeds
- [x] INN (Institute for Nonprofit News) — `https://inn.org/events/list/?ical=1` (WordPress Tribe Events)
- [x] SPJ (Society of Professional Journalists) — `webcal://calendar.spjnetwork.org/calendar.php`
- [x] Poynter Institute — `https://www.poynter.org/events/?ical=1` (WordPress Tribe Events)
- [x] NAHJ (National Assoc. of Hispanic Journalists) — `https://nahj.org/events/?ical=1` (WordPress Tribe Events)
- [x] NLGJA (Assoc. of LGBTQ+ Journalists) — `https://www.nlgja.org/events/?ical=1` (WordPress Tribe Events)
- [x] AHCJ (Assoc. of Health Care Journalists) — `https://healthjournalism.org/events/?ical=1` (WordPress Tribe Events)
- [x] SABEW (Soc. for Advancing Business Editing & Writing) — `https://sabew.org/?post_type=tribe_events&ical=1&eventDisplay=list` (WordPress Tribe Events)
- [x] Hacks/Hackers — `https://api2.luma.com/ics/get?entity=calendar&id=cal-09kcgQfLYGyy2JP` (Luma calendar ICS)
- [x] RJI (Reynolds Journalism Institute) — `https://calendar.missouri.edu/live/ical/events/group/Reynolds%20Journalism%20Institute/` (University of Missouri LiveWhale calendar; low volume)

### Google Calendar
- [x] Tiny News Members Only — `https://calendar.google.com/calendar/ical/c_3ef2026db19c41c73cb8ed72bbde7f163008de761ce942a9ad334f5b8993e652%40group.calendar.google.com/public/basic.ics`
- [x] Journalism Internship & Fellowship Deadlines — `https://calendar.google.com/calendar/ical/er06vtjd12h86b4rej5bts6p6c%40group.calendar.google.com/public/basic.ics`
- [x] NewsGuild-CWA Events — `https://calendar.google.com/calendar/ical/c_ids4f68nckkrpd5fne36sgooeo%40group.calendar.google.com/public/basic.ics`

### Scrapers
- [x] SEJ (Society of Environmental Journalists) — `sej_calendar.py` (RSS calendar at `sej.org/rss_calendar`)
- [x] IRE/NICAR Conference Schedules — `ire_schedule.py` (S3 JSON, updated per conference cycle)
- [x] SJN (Solutions Journalism Network) — `sjn_events.py` (Drupal HTML scraper at `solutionsjournalism.org/events`)
- [x] PEN America — `pen_america.py` (WordPress REST API at `pen.org/wp-json/wp/v2/event`) + `eventbrite.py` (organizer `31882531335`)
- [x] NABJ (National Assoc. of Black Journalists) — `nabj_events.py` (Wild Apricot RSS at `nabj.org/resource/rss/events.rss`)
- [x] American Press Institute — `eventbrite.py` (Eventbrite organizer `59619554833`; 0 upcoming as of 2026-03)
- [x] Center for Cooperative Media — `eventbrite.py` (Eventbrite organizer `5988913981`)
- [x] SciLine (AAAS) — `eventbrite.py` (Eventbrite organizer `120815379857`; 0 upcoming as of 2026-03)
- [x] Sunlight Research — `sunlight_research.py` (Wix listing page scraper at `sunlightresearch.net/research-training`)
- [x] Poynter Institute Training — `poynter_shop.py` (WooCommerce shop page at `poynter.org/shop/`)
- [x] Lenfest Institute — `lenfest_events.py` (WordPress HTML scraper at `lenfestinstitute.org/get-involved/events/`)
- [x] LION Publishers — `lion_publishers.py` (HTML scraper, WordPress free-form events page)
- [x] Editor & Publisher — `editor_publisher.py` (HTML scraper, industry conference calendar)
- [x] Associated Press — `eventbrite.py` (Eventbrite organizer `72823983313`)
- [x] News Product Alliance — `eventbrite.py` (Eventbrite organizer `31338856063`)
- [x] ONA (Online News Association) — `ona_events.py` (HTML scraper, Novi AMS events page)
- [x] Knight Center for Journalism — `knight_center.py` (WordPress/Elementor course library at `journalismcourses.org/course-library/`)

## Investigated — Not Viable

- **American Journalism Project** — No public events; invitation-only (AJPalooza)
- **Virginia Local News Project** — No events calendar; runs ongoing programs only
- **GIJN** — Site returns 403 to all automated requests; no public feeds
- **East-West Center** — Cloudflare 403 on all automated access
- **The Open Notebook** — Trainings are custom-booked/on-demand, no scheduled events
- **Trusting News** — Events announced via blog posts with Zoom links, no structured data
- **Knight Foundation** — Events infrastructure under development, not live
- **RTDNA** — No public feeds; Novi AMS platform, /events/feed returns 500
- **National Press Club** — Custom calendar grid, no feeds
- **EWA** — No feeds; custom WordPress events with AJAX
- **AAJA** — No event-specific feeds; RSS has news only
- **Inside the Newsroom (Substack)** — Blog post listing deadlines in prose; no structured data or feeds
- **Hearst Awards** — TLS certificate error (ERR_TLS_CERT_ALTNAME_INVALID); site inaccessible
- **SPJ Freelance Calendar** — Same feed as SPJ already implemented (`webcal://calendar.spjnetwork.org/calendar.php`)
- **Trauma Journalism** — WordPress custom calendar, no ICS/RSS export; stale events only
- **CPJ** — WordPress, no events ICS feed; events page is server-rendered but stale (last event 2018)
- **IWMF** — Returns 403 to automated access
- **Pulitzer Center** — Returns 403 to automated access
- **TCIJ (Centre for Investigative Journalism)** — Returns 403 to automated access
- **SRCCON / OpenNews** — One event per year, no structured format
- **Report for America** — No events found
