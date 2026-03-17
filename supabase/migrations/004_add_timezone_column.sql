-- Migration 004: Add timezone column and fix stored timestamps
--
-- Purpose:
--   1. Add a `timezone` column (IANA identifier, e.g. 'America/New_York') to
--      events, pending_events, and event_enrichments.
--   2. Backfill the column from a city → timezone mapping for all existing rows.
--   3. Fix the "fake UTC" problem: event times were stored as local times but
--      tagged as UTC. This migration re-interprets those timestamps correctly so
--      that all stored timestamps represent true UTC.
--
-- Note: publisher-resources events span multiple timezones and are excluded from
-- the time-fix step; they will be corrected on next ingestion.
--
-- Apply manually via: psql $DATABASE_URL -f 004_add_timezone_column.sql
-- This file is NOT applied automatically by the migration runner.

-- Add timezone column to events, pending_events, and event_enrichments
-- Stores IANA timezone identifier (e.g. 'America/New_York')

ALTER TABLE events ADD COLUMN IF NOT EXISTS timezone text;
ALTER TABLE pending_events ADD COLUMN IF NOT EXISTS timezone text;
ALTER TABLE event_enrichments ADD COLUMN IF NOT EXISTS timezone text;

-- Backfill existing events from city mapping
UPDATE events SET timezone = CASE city
  WHEN 'petaluma' THEN 'America/Los_Angeles'
  WHEN 'portland' THEN 'America/Los_Angeles'
  WHEN 'bloomington' THEN 'America/Indiana/Indianapolis'
  WHEN 'boston' THEN 'America/New_York'
  WHEN 'evanston' THEN 'America/Chicago'
  WHEN 'roanoke' THEN 'America/New_York'
  WHEN 'matsu' THEN 'America/Anchorage'
  WHEN 'jweekly' THEN 'America/Los_Angeles'
  WHEN 'publisher-resources' THEN 'America/New_York'
  ELSE 'America/Los_Angeles'
END
WHERE timezone IS NULL;

-- Backfill pending_events the same way
UPDATE pending_events SET timezone = CASE city
  WHEN 'petaluma' THEN 'America/Los_Angeles'
  WHEN 'portland' THEN 'America/Los_Angeles'
  WHEN 'bloomington' THEN 'America/Indiana/Indianapolis'
  WHEN 'boston' THEN 'America/New_York'
  WHEN 'evanston' THEN 'America/Chicago'
  WHEN 'roanoke' THEN 'America/New_York'
  WHEN 'matsu' THEN 'America/Anchorage'
  WHEN 'jweekly' THEN 'America/Los_Angeles'
  WHEN 'publisher-resources' THEN 'America/New_York'
  ELSE 'America/Los_Angeles'
END
WHERE timezone IS NULL;

-- Backfill event_enrichments
UPDATE event_enrichments SET timezone = CASE city
  WHEN 'petaluma' THEN 'America/Los_Angeles'
  WHEN 'portland' THEN 'America/Los_Angeles'
  WHEN 'bloomington' THEN 'America/Indiana/Indianapolis'
  WHEN 'boston' THEN 'America/New_York'
  WHEN 'evanston' THEN 'America/Chicago'
  WHEN 'roanoke' THEN 'America/New_York'
  WHEN 'matsu' THEN 'America/Anchorage'
  WHEN 'jweekly' THEN 'America/Los_Angeles'
  WHEN 'publisher-resources' THEN 'America/New_York'
  ELSE 'America/Los_Angeles'
END
WHERE timezone IS NULL;

-- Fix stored times: currently local times pretending to be UTC.
-- (start_time AT TIME ZONE 'UTC') strips UTC marker to get naive timestamp,
-- then AT TIME ZONE timezone re-interprets as local time → correct UTC.
-- Skip publisher-resources (multi-timezone, will be fixed on next ingestion).
UPDATE events
SET start_time = (start_time AT TIME ZONE 'UTC') AT TIME ZONE timezone
WHERE timezone IS NOT NULL AND city != 'publisher-resources';

UPDATE events
SET end_time = (end_time AT TIME ZONE 'UTC') AT TIME ZONE timezone
WHERE timezone IS NOT NULL AND end_time IS NOT NULL AND city != 'publisher-resources';

UPDATE pending_events
SET start_time = (start_time AT TIME ZONE 'UTC') AT TIME ZONE timezone
WHERE timezone IS NOT NULL;

UPDATE pending_events
SET end_time = (end_time AT TIME ZONE 'UTC') AT TIME ZONE timezone
WHERE timezone IS NOT NULL AND end_time IS NOT NULL;

UPDATE event_enrichments
SET start_time = (start_time AT TIME ZONE 'UTC') AT TIME ZONE timezone
WHERE timezone IS NOT NULL AND start_time IS NOT NULL;

UPDATE event_enrichments
SET end_time = (end_time AT TIME ZONE 'UTC') AT TIME ZONE timezone
WHERE timezone IS NOT NULL AND end_time IS NOT NULL;

-- =============================================================================
-- REVERSE MIGRATION (run manually to undo — destructive, use with caution)
-- =============================================================================
--
-- Step 1: Undo the timestamp fix — convert corrected UTC back to "fake UTC"
--         (local time stored with UTC marker).
--
-- UPDATE events
-- SET start_time = (start_time AT TIME ZONE timezone) AT TIME ZONE 'UTC'
-- WHERE timezone IS NOT NULL AND city != 'publisher-resources';
--
-- UPDATE events
-- SET end_time = (end_time AT TIME ZONE timezone) AT TIME ZONE 'UTC'
-- WHERE timezone IS NOT NULL AND end_time IS NOT NULL AND city != 'publisher-resources';
--
-- UPDATE pending_events
-- SET start_time = (start_time AT TIME ZONE timezone) AT TIME ZONE 'UTC'
-- WHERE timezone IS NOT NULL;
--
-- UPDATE pending_events
-- SET end_time = (end_time AT TIME ZONE timezone) AT TIME ZONE 'UTC'
-- WHERE timezone IS NOT NULL AND end_time IS NOT NULL;
--
-- UPDATE event_enrichments
-- SET start_time = (start_time AT TIME ZONE timezone) AT TIME ZONE 'UTC'
-- WHERE timezone IS NOT NULL AND start_time IS NOT NULL;
--
-- UPDATE event_enrichments
-- SET end_time = (end_time AT TIME ZONE timezone) AT TIME ZONE 'UTC'
-- WHERE timezone IS NOT NULL AND end_time IS NOT NULL;
--
-- Step 2: Drop the timezone column from all three tables.
--
-- ALTER TABLE events DROP COLUMN IF EXISTS timezone;
-- ALTER TABLE pending_events DROP COLUMN IF EXISTS timezone;
-- ALTER TABLE event_enrichments DROP COLUMN IF EXISTS timezone;
-- =============================================================================
