# JWeekly (Jewish Northern California) Sources Checklist

This calendar aggregates events from Jewish organizations across the San Francisco Bay Area / Northern California, sourced from the [J. Weekly Jewish Resource Guide](https://jweekly.com/jewishresourceguide/).

## Currently Implemented

### ICS Feeds (The Events Calendar / WordPress)
| Source | Feed URL | Events | Notes |
|--------|----------|--------|-------|
| J. Weekly (jweekly.com) | `https://jweekly.com/events/?ical=1` | 18 | Community events aggregator, clean descriptions |
| JCCSF (Jewish Community Center of SF) | `https://www.jccsf.org/events/?ical=1` | 17 | Empty descriptions - may need scraper for enrichment |
| Peninsula JCC | `https://www.pjcc.org/events/?ical=1` | 30 | Good descriptions |
| Osher Marin JCC | `https://www.marinjcc.org/events/?ical=1` | 12 | Good descriptions |
| JCC East Bay | `https://www.jcceastbay.org/events/?ical=1` | 30 | Good descriptions (Mah Jongg, Yiddish, etc.) |
| Jewish Federation Bay Area | `https://www.jewishfed.org/events/?ical=1` | 25 | Community-wide events, good descriptions |
| Urban Adamah | `https://www.urbanadamah.org/events/?ical=1` | 30 | Farm + Jewish programming; descriptions contain page HTML - needs cleanup |
| Kehilla Community Synagogue | `https://www.kehillasynagogue.org/events/?ical=1` | 26 | Good descriptions (meditation, learning, services) |
| The Magnes Collection (UC Berkeley) | `https://magnes.berkeley.edu/events/?ical=1` | 8 | Jewish art & life museum, good descriptions |

### Google Calendar Feeds
| Source | Feed URL | Events | Notes |
|--------|----------|--------|-------|
| Congregation Beth Sholom SF | `https://calendar.google.com/calendar/ical/bethsholomsf%40gmail.com/public/basic.ics` | 7172 | Very large - includes recurring services, will need review |

### Meetup Groups
| Source | Feed URL | Events | Notes |
|--------|----------|--------|-------|
| Bay Area Peninsula Jewish Young Adults | `https://www.meetup.com/bayareajews/events/ical/` | 2 | 20s-30s social events |
| Bay Area Jewish Singles Havurah | `https://www.meetup.com/Bay-Area-Jewish-Singles-Havurah/events/ical/` | 3 | 40s-60s hiking, dinners, cultural |
| Mountain Jew | `https://www.meetup.com/mountain-jew/events/ical/` | 5 | Young professionals, hikes, Shabbat |

### Eventbrite Organizers (via scraper)
| Source | Eventbrite Organizer URL | Notes |
|--------|--------------------------|-------|
| JCCSF | eventbrite.com/o/115705078411 | 19 upcoming events |
| Congregation Emanu-El SF | eventbrite.com/o/congregation-emanu-el-san-francisco-74110536583 | Multiple pages |
| Chabad SF - SOMA Shul | eventbrite.com/o/chabad-sf-soma-shul-3729957203 | 2 upcoming events |
| JCC East Bay | eventbrite.com/o/jcc-east-bay-9035654915 | 3 upcoming events |
| Jewish Baby Network - East Bay | eventbrite.com/o/jewish-baby-network-jbn-east-bay-56946956693 | Family (0-36 months) |
| Jewish Baby Network - Peninsula | eventbrite.com/o/jewish-baby-network-jbn-peninsula-60080821253 | 3 upcoming events |

## Discovered - Needs Investigation

| Source | URL | Platform | Notes |
|--------|-----|----------|-------|
| Oshman Family JCC (Palo Alto) | paloaltojcc.org | WordPress + Ticket Tailor | No ICS feed at standard paths; uses Elementor |
| Jewish Silicon Valley | jvalley.org | WordPress + The Events Calendar | Behind Cloudflare, ICS feed times out |
| Congregation Emanu-El SF | emanuelsf.org | WordPress + Salesforce/FullCalendar.js | Custom CRM integration; also on Eventbrite |
| JCC Sonoma County | jccsoco.org | Wix | Wix site - no feed expected |
| Addison-Penzak JCC (Los Gatos) | apjcc.org | WordPress + Elementor | No calendar plugin detected |
| Wilderness Torah | wildernesstorah.org | WordPress (Avada theme) | 404 on /events, /calendar paths |
| New Lehrhaus | newlehrhaus.org | Custom CMS ("Agile") | Programs at /learn-with-us, no ICS |
| GatherBay | gatherbay.org | Unknown | SSL certificate expired; major Bay Area Jewish event aggregator |
| SF Black & Jewish Unity Coalition | sfunitygroup.org | Squarespace | Has ?format=ical but returned 0 events |
| Jewish Film Institute | jfi.org | Ingeniux CMS + custom | Custom calendar, no ICS; ticketing at boxoffice.jfi.org |
| JFCS (Jewish Family & Children's Services) | jfcs.org | WordPress + Eventbrite mix | Hybrid approach, no unified feed |
| JFCS Holocaust Center | holocaustcenter.jfcs.org | Unknown | /community-events/upcoming-events/ - not a WordPress ICS |
| Berkeley Hillel | berkeleyhillel.org | WordPress + The Events Calendar | /calendar/ page exists but ICS feed returns empty |
| Stanford Hillel | stanfordhillel.org | Own website | /event-list; also on events.stanford.edu |

## Discovered - Eventbrite Organizers (need scraper)
(all moved to Currently Implemented)

## Discovered - Non-Starters

| Source | Reason |
|--------|--------|
| Congregation Sherith Israel | ShulCloud platform, 406 errors on fetch |
| Congregation Netivot Shalom | ShulCloud platform - no public ICS |
| Chabad of SF (main site) | 403 Forbidden |
| Congregation Etz Chayim | 406 error on fetch |
| Tribester Jewish Experiences | National aggregator, only 1 Bay Area event |
| SF Bay Area Jewish Hikers (Meetup) | ICS feed returns 0 events |
| Friday Night Hub (Meetup) | ICS feed returns 0 events |
| Bay Area Israelis Meetup | ICS feed returns 0 events |
| Jewish Geeks - Bay Area (Meetup) | ICS feed returns 0 events |
| SF Bay Area Hebrew Speakers (Meetup) | ICS feed returns 0 events |

## To Investigate

### More Congregations
- [ ] Congregation Beth Israel (Berkeley)
- [ ] Temple Sinai (Oakland)
- [ ] Congregation Sha'ar Zahav (SF - LGBTQ)
- [ ] Congregation Beth Am (Los Altos Hills)
- [ ] Temple Beth Abraham (Oakland)
- [ ] Peninsula Temple Beth El (San Mateo)

### Other Organizations from Resource Guide
- [ ] Moishe House / Mem Global (redirects to memglobal.org, 404)
- [ ] OneTable (Shabbat dinners for young adults)
- [ ] Israel Center of SF / Israeli Consulate events
- [ ] Jewish Vocational Service (JVS)
- [ ] Israeli Folk Dancing groups (Cafe Simcha, etc.)
- [ ] Yiddish cultural organizations
- [ ] BBYO Central Region West (teen programs)
- [ ] Jewish High Tech Community (jhtc.org)
- [ ] Chabad of the Bay Area (jbayarea.org) - Jewish calendar page

### Resource Guide Categories Not Yet Searched
- [ ] Agencies & Organizations > Federations
- [ ] Agencies & Organizations > Public Affairs
- [ ] Arts & Judaica > Genealogy & History
- [ ] Arts & Judaica > Sports
- [ ] Kids & Teens > Family Resources
- [ ] Kids & Teens > Day Camps / Overnight Camps
- [ ] Religious Life > Interfaith Programs
- [ ] Social Services > LGBTQ Support
