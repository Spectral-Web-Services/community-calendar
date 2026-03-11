import { useState, useEffect } from 'react';
import { SUPABASE_URL, SUPABASE_KEY } from '../lib/supabase.js';
import { applyEnrichments } from '../lib/helpers.js';

/** Fetch a single public collection + its events (no auth required). */
export function useCollection(feedId) {
  const [collection, setCollection] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!feedId) { setLoading(false); return; }

    const headers = { apikey: SUPABASE_KEY };

    async function load() {
      try {
        // Fetch collection metadata
        const colRes = await fetch(
          `${SUPABASE_URL}/rest/v1/collections?id=eq.${feedId}&select=*`,
          { headers }
        );
        const colData = await colRes.json();
        const col = Array.isArray(colData) ? colData[0] : null;
        setCollection(col || null);
        if (!col) { setEvents([]); setLoading(false); return; }

        let rawEvents;

        if (col.type === 'auto') {
          // Auto-collection: query events directly using rules
          const rules = col.rules || {};
          const now = new Date().toISOString();
          let url = `${SUPABASE_URL}/rest/v1/events?city=eq.${encodeURIComponent(col.city)}&start_time=gte.${now}&order=start_time.asc&select=*`;
          if (rules.sources?.length) {
            url += `&source=in.(${rules.sources.map(s => encodeURIComponent(s)).join(',')})`;
          }
          if (rules.categories?.length) {
            url += `&category=in.(${rules.categories.map(c => encodeURIComponent(c)).join(',')})`;
          }

          const [evRes, exRes, manualRes] = await Promise.all([
            fetch(url, { headers }),
            fetch(`${SUPABASE_URL}/rest/v1/auto_collection_exclusions?collection_id=eq.${feedId}&select=source_uid`, { headers }),
            fetch(`${SUPABASE_URL}/rest/v1/collection_events?collection_id=eq.${feedId}&select=event_id,events(*)`, { headers }),
          ]);
          const evData = await evRes.json();
          const exclusions = await exRes.json();
          const manualAdds = await manualRes.json();
          const excludedUids = new Set((Array.isArray(exclusions) ? exclusions : []).map(e => e.source_uid));

          const ruleMatched = (Array.isArray(evData) ? evData : []).filter(ev => !excludedUids.has(ev.source_uid));
          // Merge manually-added events not already matched by rules
          const matchedIds = new Set(ruleMatched.map(ev => ev.id));
          const manualEvents = (Array.isArray(manualAdds) ? manualAdds : [])
            .filter(ce => ce.events && !matchedIds.has(ce.event_id))
            .map(ce => ce.events);
          rawEvents = [...ruleMatched, ...manualEvents];
        } else {
          // Manual collection: query collection_events joined with events
          const evRes = await fetch(
            `${SUPABASE_URL}/rest/v1/collection_events?collection_id=eq.${feedId}&select=sort_order,event_id,events(*)&order=sort_order`,
            { headers }
          );
          const evData = await evRes.json();
          rawEvents = (Array.isArray(evData) ? evData : [])
            .filter(ce => ce.events)
            .map(ce => ({ ...ce.events, _sort_order: ce.sort_order }));
        }

        // Fetch curator's enrichments and apply them
        const enrRes = await fetch(
          `${SUPABASE_URL}/rest/v1/event_enrichments?curator_id=eq.${col.user_id}&select=*`,
          { headers }
        );
        const enrichments = await enrRes.json();
        const enrichArr = Array.isArray(enrichments) ? enrichments : [];
        const enriched = applyEnrichments(rawEvents, enrichArr);

        // Sort featured events to the front
        const featuredSet = new Set(enrichArr.filter(e => e.featured && e.event_id).map(e => e.event_id));
        if (featuredSet.size > 0) {
          const featured = enriched.filter(e => featuredSet.has(e.id));
          const rest = enriched.filter(e => !featuredSet.has(e.id));
          setEvents([...featured, ...rest]);
        } else {
          setEvents(enriched);
        }
      } catch {
        setCollection(null);
        setEvents([]);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [feedId]);

  return { collection, events, loading };
}
