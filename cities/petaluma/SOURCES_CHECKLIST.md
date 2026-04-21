# Petaluma Calendar Source Checklist

## Currently Implemented (all in CI)

| Source | Type | Events | Status |
|--------|------|--------|--------|
| Petaluma Downtown Association | Tockify ICS | 71 | ✅ In CI |
| Aqus Community | MembershipWorks ICS | 87 | ✅ In CI |
| Petaluma Regional Library | Scraper | 155 | ✅ In CI |
| Petaluma Chamber of Commerce | GrowthZone Scraper | 80 | ✅ In CI |
| Mystic Theatre | Scraper | 21 | ✅ In CI |
| ~~Eventbrite Petaluma~~ | ~~Scraper~~ | — | Retired 2026-02-15: scraper broken |
| Petaluma High School Athletics | MaxPreps Scraper | 9 | ✅ In CI |
| Casa Grande High School Athletics | MaxPreps Scraper | 8 | ✅ In CI |
| SRJC Petaluma Campus | LiveWhale ICS | ~10 | ✅ In CI |
| HenHouse Brewing Petaluma | Scraper | 2-3 | ✅ In CI |
| Phoenix Theater | Eventbrite Scraper | 9 | ✅ In CI (restored 2026-04-20) |
| Mercury Theater | Squarespace JSON Scraper | 12 | ✅ In CI |
| Adobe Road Winery | JSON-LD Scraper | 8 | ✅ In CI |
| The Big Easy | WordPress iCal | ~30 | ✅ In CI |
| Polly Klaas Community Theater | WordPress iCal | ~8 | ✅ In CI |
| Brooks Note Winery | Google Calendar ICS | ~142 | ✅ In CI |
| Petaluma Arts Center | Squarespace Scraper | ~10 | ✅ In CI |
| Brewsters Beer Garden | Squarespace Scraper | ~18 | ✅ In CI |
| Cool Petaluma | Squarespace Scraper | ~6 | ✅ In CI |
| McNear's Saloon | WordPress iCal | ~2 | ✅ In CI |
| Griffo Distillery | Tockify ICS | ~20 | ✅ In CI |
| Petaluma Elks Lodge | Google Calendar ICS | ~568 | ✅ In CI |
| Petaluma Garden Club | Google Calendar ICS | ~131 | ✅ In CI |
| Petaluma Bounty | WordPress iCal | ~19 | ✅ In CI |
| Petaluma River Park | Squarespace Scraper | ~8 | ✅ In CI |
| Petaluma Historical Library & Museum | WordPress iCal | ~2 | ✅ In CI |
| Blue Zones Project Petaluma | Eventbrite Scraper | ~4 | ✅ In CI |
| Meetup: Mindful Petaluma | ICS | 10 | ✅ In CI |
| Meetup: Candlelight Yoga | ICS | 10 | ✅ In CI |
| Meetup: Rebel Craft Collective | ICS | 6 | ✅ In CI |
| Meetup: Figure Drawing | ICS | 1 | ✅ In CI |
| Meetup: Book & Brew Club | ICS | 1 | ✅ In CI |
| Meetup: Active 20-30 | ICS | 2 | ✅ In CI |
| Meetup: Sonoma County Outdoors | ICS | ~10 | ✅ In CI |
| Meetup: Meditate with a Monk | ICS | ~10 | ✅ In CI |
| Lagunitas Brewing Petaluma | Scraper | 10 | ✅ In CI (added 2026-04-20) |
| The Floathouse Petaluma | Squarespace Scraper | ~78 | ✅ In CI (added 2026-04-20) |
| Petaluma Speedway | WordPress iCal | ~27 | ✅ In CI (added 2026-04-20) |
| Hall of the Above | Squarespace Scraper | ~16 | ✅ In CI (added 2026-04-20) |
| Usher Gallery | Scraper | ~2 | ✅ In CI (added 2026-04-20) |
| Montagne Russe Winery | Vin65 Scraper | ~9 | ✅ In CI (added 2026-04-20) |
| Copperfield's Books Petaluma | Drupal Scraper | ~15 | ✅ In CI (added 2026-04-20) |
| UU Petaluma | Google Calendar ICS | many | ✅ In CI (added 2026-04-20) |
| The Block Petaluma | Elfsight Calendar Scraper | ~51 | ✅ In CI (added 2026-04-20) |
| Village Network of Petaluma | HelpfulVillage Scraper | ~47 | ✅ In CI (added 2026-04-20) |

### Aggregators
These curate or republish events from primary venues (which we already scrape directly). They're listed in `AGGREGATORS` in `scripts/combine_ics.py` so primary sources win during cross-source dedup.

| Source | Type | Events | Notes |
|--------|------|--------|-------|
| Visit Petaluma | tribe-events Scraper | ~41 | Tourism board's `find-events/` listing; iCal export and Tribe REST API are disabled, so we scrape the rendered listing pages. Heavy overlap with Mystic / Phoenix / Russe / etc. — added 2026-04-20 |

---

## To Investigate

### Not yet investigated
- Sonoma County Regional Parks (parks.sonomacounty.ca.gov/play/calendar/hiking) - no ICS, would need scraper; Tolay Lake hikes may be within radius
- Petaluma Cycling Club / Petaluma Wheelmen (petalumawheelmen.org) — Wild Apricot platform, no native ICS. Homepage links only 2 master event pages (e.g., /event-6641694 "Show and Go from River Front Cafe – Every Tuesday & Thursday 9 AM"); each is a parent event with many child sessions exposed only via `#sessionId` fragments. Would need to crawl `/event-N` pages and expand sessions manually. 2026-04-20
- Empire Runners Club (Wild Apricot - no native ICS)
- Sonoma-Marin Fairgrounds (sonoma-marinfair.org/calendar) - WordPress Events Calendar, ICS empty, check closer to fair season
- Petaluma Wetlands Alliance (petalumawetlands.org/calendar/) - WordPress/Divi, JS-rendered calendar, couldn't see events

---

## Non-Starters

| Source | Reason |
|--------|--------|
| City of Petaluma website | Cloudflare protection |
| Various Marin-based Meetup groups | Too far from Petaluma (removed 2026-03-13) |
| Mindful-Monday Meetup | Virtual conference calls, not local |
| Petaluma Wildlife Museum | School tours/private events, not public |
| Youth sports leagues | Member-only platforms, no public calendar exports (see below) |
| WonderStump! | Squarespace but no events collection; Ticket Tailor behind Cloudflare |
| 350 Petaluma | Squarespace events but dead since Oct 2023 |
| Petaluma People Services | Squarespace but hand-curated page, not events collection |
| Rotary Club of Petaluma | ClubRunner site deactivated |
| Cinnabar Theater | Shows at SSU Warren Theater in Rohnert Park, outside 8mi radius |
| Healthy Petaluma | Squarespace, board meetings only |
| 14 regional Meetup groups | Removed 2026-03-13: events outside 8mi radius or 0 events |

### Youth Sports Research (2026-02-14)

Extensively investigated: Petaluma National/American Little League (BlueSombrero), Leghorns Baseball, AYSO Region 26 (wrong city), Petaluma Youth Soccer (domain dead), Girls Softball (site down), Swim Team (not active), Parks & Rec (Cloudflare), RecDesk (not found). Platforms checked: GameChanger, TeamSnap, SportsEngine, LeagueApps, GotSport, TourneyMachine, ActiveNet, RecDesk. None viable. High school athletics via MaxPreps already covers public-facing school sports.

## More todo 4-20-2026

### Marginal value, defer
- Petaluma Film Alliance (petalumafilmalliance.org/2026-spring-schedule/) — static spring schedule page, ~12 films parseable from H2 headings (`Month Day: TITLE`). Date-only, no times in headings — would need to fetch each film's individual page or assume a default showtime. 2026-04-20
- Magic Shop Studios (magicshopstudios.com/open-studio-gallery-shows/) — only quarterly open studios + occasional gallery shows, very low event volume. 2026-04-20

### Deferred
(none currently)

### Already covered above
- Cinnabar Theater — see Non-Starters (shows at SSU Warren Theater, outside 8mi radius)
- Petaluma Museum — already in CI as "Petaluma Historical Library & Museum"
