-- View for public embed queries: excludes events from hidden sources entirely.
-- Curators see private source events via FeedView which queries the events
-- table directly when authenticated.
CREATE OR REPLACE VIEW embed_events AS
SELECT e.*
FROM events e
WHERE NOT EXISTS (
  SELECT 1 FROM source_config sc
  WHERE sc.city = e.city
    AND sc.source_name = e.source
    AND sc.hidden_from_main = true
);
