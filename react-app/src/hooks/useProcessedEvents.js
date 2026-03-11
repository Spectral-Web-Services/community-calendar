import { useMemo } from 'react';
import {
  applyEnrichments,
  dedupeEvents,
  expandEnrichments,
  filterHiddenSources,
  getCumulativeEvents,
  getMasonryColumns,
} from '../lib/helpers.js';
import { getDateRange } from './useEvents.js';

export function useProcessedEvents(events, enrichments, filterTerm, displayCount, categoryFilter, columnCount, featuredIds) {
  const { from, to } = useMemo(() => getDateRange(), []);

  const processedEvents = useMemo(() => {
    if (!events) return [];
    const enriched = applyEnrichments(events, enrichments);
    const expanded = expandEnrichments(enrichments, from, to);
    const combined = [...enriched, ...expanded];
    const deduped = dedupeEvents(combined);
    return filterHiddenSources(deduped, []);
  }, [events, enrichments, from, to]);

  const { events: cardEvents, hasMore } = useMemo(() => {
    return getCumulativeEvents(processedEvents, filterTerm, displayCount, categoryFilter, featuredIds);
  }, [processedEvents, filterTerm, displayCount, categoryFilter, featuredIds]);

  const masonryColumns = useMemo(() => {
    return getMasonryColumns(cardEvents, columnCount);
  }, [cardEvents, columnCount]);

  return { processedEvents, cardEvents, hasMore, masonryColumns };
}
