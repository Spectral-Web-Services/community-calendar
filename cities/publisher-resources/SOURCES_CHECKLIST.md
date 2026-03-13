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

### Google Calendar
- [ ] Tiny News Members Only — `https://calendar.google.com/calendar/ical/c_3ef2026db19c41c73cb8ed72bbde7f163008de761ce942a9ad334f5b8993e652%40group.calendar.google.com/public/basic.ics`
- [ ] Journalism Internship & Fellowship Deadlines — `https://calendar.google.com/calendar/ical/er06vtjd12h86b4rej5bts6p6c%40group.calendar.google.com/public/basic.ics`

### Scrapers
- [ ] SEJ (Society of Environmental Journalists) — `sej_calendar.py` (RSS calendar at `sej.org/rss_calendar`)
- [ ] IRE/NICAR Conference Schedules — `ire_schedule.py` (S3 JSON, updated per conference cycle)

## Investigated — Not Viable

- **LION Publishers** — No calendar feeds; WordPress events page at `https://lionpublishers.com/events/` could be scraped
- **American Journalism Project** — No public events; invitation-only (AJPalooza)
- **Virginia Local News Project** — No events calendar; runs ongoing programs only
- **GIJN** — Site returns 403 to all automated requests; no public feeds
- **East-West Center** — Cloudflare 403 on all automated access
- **The Open Notebook** — Trainings are custom-booked/on-demand, no scheduled events
- **Trusting News** — Events announced via blog posts with Zoom links, no structured data
- **ONA** — No public feeds; Novi AMS platform, EventScribe for conferences
- **Knight Foundation** — Events infrastructure under development, not live
- **RTDNA** — No public feeds; Novi AMS platform, /events/feed returns 500
- **National Press Club** — Custom calendar grid, no feeds
- **EWA** — No feeds; custom WordPress events with AJAX
- **NABJ** — Site returns 403 to automated access
- **AAJA** — No event-specific feeds; RSS has news only
- **Inside the Newsroom (Substack)** — Blog post listing deadlines in prose; no structured data or feeds
- **Hearst Awards** — TLS certificate error (ERR_TLS_CERT_ALTNAME_INVALID); site inaccessible
- **Editor & Publisher** — Custom CMS (Creative Circle Media), no ICS/RSS feeds; curated directory only
- **SPJ Freelance Calendar** — Same feed as SPJ already implemented (`webcal://calendar.spjnetwork.org/calendar.php`)
- **Trauma Journalism** — WordPress custom calendar, no ICS/RSS export; stale events only
- **IRE** — WordPress (Beaver Builder) but no ICS export; `?ical=1` returns HTML; RSS is blog posts only
- **CPJ** — WordPress, no events ICS feed; general RSS at `/about/feeds/` is not event-specific
- **IWMF** — Returns 403 to automated access
- **Knight Center (journalismcourses.org)** — WordPress/WooCommerce, no calendar feeds; course dates only in page templates
- **Pulitzer Center** — Returns 403 to automated access
- **TCIJ (Centre for Investigative Journalism)** — Returns 403 to automated access

## To Investigate

- LION Publishers events page scraper
- Hacks/Hackers events
- SRCCON / OpenNews
- Lenfest Institute
- News Revenue Hub
- Report for America
- Center for Cooperative Media
- Solutions Journalism Network