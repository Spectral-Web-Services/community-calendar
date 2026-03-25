/**
 * Timezone-aware display utilities.
 *
 * After the timezone migration, event times are stored as real UTC in timestamptz
 * columns, with a `timezone` text field containing the IANA timezone.
 */

/**
 * Format a time string in a specific timezone.
 * Returns empty string for midnight (all-day events).
 */
export function formatTimeInZone(isoString, timezone) {
  if (!isoString) return '';
  const d = new Date(isoString);
  const parts = new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone: timezone,
  }).formatToParts(d);

  const hour = parts.find(p => p.type === 'hour')?.value;
  const minute = parts.find(p => p.type === 'minute')?.value;
  const dayPeriod = parts.find(p => p.type === 'dayPeriod')?.value;

  if (hour === '12' && minute === '00' && dayPeriod?.toUpperCase() === 'AM') return '';
  return `${hour}:${minute} ${dayPeriod?.toUpperCase() || ''}`.trim();
}

/**
 * Format date parts (month, day, weekday) in a specific timezone.
 */
export function formatDateInZone(isoString, timezone) {
  if (!isoString) return { month: '', day: '', weekday: '' };
  const d = new Date(isoString);
  return {
    month: d.toLocaleDateString('en-US', { month: 'short', timeZone: timezone }).toUpperCase(),
    day: d.toLocaleDateString('en-US', { day: 'numeric', timeZone: timezone }),
    weekday: d.toLocaleDateString('en-US', { weekday: 'short', timeZone: timezone }),
  };
}

/**
 * Format day of week in a specific timezone.
 */
export function formatDayOfWeekInZone(isoString, timezone) {
  if (!isoString) return '';
  return new Date(isoString).toLocaleDateString('en-US', { weekday: 'short', timeZone: timezone });
}

/**
 * Format month + day in a specific timezone.
 */
export function formatMonthDayInZone(isoString, timezone) {
  if (!isoString) return '';
  return new Date(isoString).toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: timezone });
}

/**
 * Determine the display timezone for an event.
 * - City views: use the event's stored timezone (or the city's timezone)
 * - publisher-resources: use the viewer's browser timezone
 */
export function getDisplayTimezone(event, citySlug) {
  if (citySlug === 'publisher-resources') {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  }
  return event?.timezone || 'America/Los_Angeles';
}

/**
 * Convert a naive datetime string (from datetime-local or date input) to an
 * ISO 8601 string with the correct UTC offset for the given IANA timezone.
 *
 * E.g. toTimestampTz("2026-03-25T13:00", "America/Los_Angeles") → "2026-03-25T13:00:00-07:00"
 *      toTimestampTz("2026-03-25", "America/Los_Angeles")        → "2026-03-25T00:00:00-07:00"
 *
 * This ensures PostgreSQL timestamptz columns store the correct instant.
 */
export function toTimestampTz(dateTimeLocal, tz) {
  if (!dateTimeLocal) return null;
  // Normalize: date-only → add midnight, datetime-local → add seconds
  const normalized = dateTimeLocal.length === 10
    ? dateTimeLocal + 'T00:00:00'
    : dateTimeLocal + ':00';

  // Create a Date near the target time (treating input as UTC to get close)
  const approx = new Date(normalized + 'Z');

  // Determine the UTC offset of the target timezone at this approximate instant
  const utcStr = approx.toLocaleString('en-US', { timeZone: 'UTC' });
  const tzStr = approx.toLocaleString('en-US', { timeZone: tz });
  const offsetMs = new Date(tzStr).getTime() - new Date(utcStr).getTime();
  const totalMin = offsetMs / 60000;

  const sign = totalMin >= 0 ? '+' : '-';
  const absMin = Math.abs(totalMin);
  const h = String(Math.floor(absMin / 60)).padStart(2, '0');
  const m = String(absMin % 60).padStart(2, '0');

  return normalized + sign + h + ':' + m;
}

/**
 * Get a short timezone abbreviation for display (e.g., "PDT", "EST").
 */
export function getTimezoneAbbr(isoString, timezone) {
  if (!isoString || !timezone) return '';
  const d = new Date(isoString);
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZoneName: 'short',
    timeZone: timezone,
  }).formatToParts(d);
  return parts.find(p => p.type === 'timeZoneName')?.value || '';
}
