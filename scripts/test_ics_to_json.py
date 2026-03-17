"""Tests for ics_to_json timezone handling."""
import json
import tempfile
from pathlib import Path
from ics_to_json import parse_ics_datetime, ics_to_json, load_city_timezone
from zoneinfo import ZoneInfo


def test_parse_utc_time_returns_offset():
    """UTC times (Z suffix) should be returned with correct offset for the city."""
    tz = ZoneInfo('America/New_York')
    iso, tz_name = parse_ics_datetime('20260115T190000Z', local_tz=tz)
    assert iso == '2026-01-15T14:00:00-05:00'
    assert tz_name == 'America/New_York'


def test_parse_naive_time_gets_city_offset():
    """Naive times (no Z, no TZID) are assumed to be in the city's timezone."""
    tz = ZoneInfo('America/Los_Angeles')
    iso, tz_name = parse_ics_datetime('20260317T190000', local_tz=tz)
    assert iso == '2026-03-17T19:00:00-07:00'
    assert tz_name == 'America/Los_Angeles'


def test_parse_tzid_parameter_honored():
    """DTSTART;TZID=America/Chicago:20260317T190000 should use the TZID, not the city tz."""
    tz = ZoneInfo('America/Los_Angeles')
    iso, tz_name = parse_ics_datetime('DTSTART;TZID=America/Chicago:20260317T190000', local_tz=tz)
    assert iso == '2026-03-17T19:00:00-05:00'
    assert tz_name == 'America/Chicago'


def test_parse_allday_event():
    """All-day events should return date with midnight and offset."""
    tz = ZoneInfo('America/New_York')
    iso, tz_name = parse_ics_datetime('20260315', local_tz=tz)
    assert iso == '2026-03-15T00:00:00-04:00'
    assert tz_name == 'America/New_York'


def test_parse_dst_spring_forward_gap():
    """Times in the DST spring-forward gap should be adjusted, not error."""
    tz = ZoneInfo('America/Los_Angeles')
    iso, tz_name = parse_ics_datetime('20260308T023000', local_tz=tz)
    assert iso is not None
    assert tz_name == 'America/Los_Angeles'


def test_parse_dst_fall_back_ambiguous():
    """Ambiguous times during fall-back should resolve (fold=0 = first occurrence)."""
    tz = ZoneInfo('America/Los_Angeles')
    iso, tz_name = parse_ics_datetime('20261101T013000', local_tz=tz)
    assert iso is not None
    assert tz_name == 'America/Los_Angeles'


def test_timezone_field_in_output():
    """ics_to_json should emit a 'timezone' field for each event."""
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Test Event
DTSTART:20260601T190000
UID:test-tz-1@example.com
X-SOURCE:test
END:VEVENT
END:VCALENDAR"""

    with tempfile.NamedTemporaryFile(suffix='.ics', mode='w', delete=False) as f:
        f.write(ics_content)
        f.flush()
        events = ics_to_json(f.name, future_only=False, city='portland')

    assert len(events) == 1
    assert events[0]['timezone'] == 'America/Los_Angeles'
    assert '-07:00' in events[0]['start_time'] or '-08:00' in events[0]['start_time']


def test_tzid_overrides_city_timezone():
    """When DTSTART has TZID parameter, that timezone should be used, not city's."""
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Remote Workshop
DTSTART;TZID=America/New_York:20260601T140000
UID:test-tz-2@example.com
X-SOURCE:test
END:VEVENT
END:VCALENDAR"""

    with tempfile.NamedTemporaryFile(suffix='.ics', mode='w', delete=False) as f:
        f.write(ics_content)
        f.flush()
        events = ics_to_json(f.name, future_only=False, city='portland')

    assert len(events) == 1
    assert events[0]['timezone'] == 'America/New_York'
    assert '-04:00' in events[0]['start_time']
