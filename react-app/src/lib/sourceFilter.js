/**
 * Build Supabase/PostgREST query params for source inclusion.
 *
 * Uses `like` so that multi-source values ("A, B") match when any
 * individual source is included.
 *
 * @param {string[]} sources - sources to include (empty = all)
 * @returns {string} query string fragment to append (starts with '&')
 */
export function buildSourceFilter(sources) {
  if (!sources?.length) return '';
  const parts = sources.map(s => `source.like.*${s}*`).join(',');
  return `&or=(${parts})`;
}
