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
    return getCumulativeEvents(processedEvents, filterTerm, displayCount, categoryFilter);
  }, [processedEvents, filterTerm, displayCount, categoryFilter]);

  const { featuredEvents, regularEvents } = useMemo(() => {
    if (!featuredIds || featuredIds.size === 0) return { featuredEvents: [], regularEvents: cardEvents };
    return {
      featuredEvents: cardEvents.filter(e => featuredIds.has(e.id)),
      regularEvents: cardEvents.filter(e => !featuredIds.has(e.id)),
    };
  }, [cardEvents, featuredIds]);

  const featuredColumns = useMemo(() => {
    return getMasonryColumns(featuredEvents, columnCount);
  }, [featuredEvents, columnCount]);

  const masonryColumns = useMemo(() => {
    return getMasonryColumns(regularEvents, columnCount);
  }, [regularEvents, columnCount]);

  return { processedEvents, cardEvents, hasMore, featuredColumns, masonryColumns };
}
