-- Allow curators to see their own hidden sources on the main feed.
-- The view already uses security_invoker = true, so auth.uid() reflects the
-- calling user.  We add a check: hidden sources are excluded UNLESS the
-- current user matches the source_config.curator_id.

CREATE OR REPLACE VIEW public_events
  WITH (security_invoker = true)
AS
SELECT e.*,
  EXISTS (
    SELECT 1 FROM source_config sc
    WHERE sc.city = e.city
      AND sc.source_name = e.source
      AND sc.hidden_from_main = true
  ) AS is_private
FROM events e
WHERE NOT EXISTS (
  SELECT 1 FROM source_config sc
  WHERE sc.city = e.city
    AND sc.source_name = e.source
    AND sc.hidden_from_main = true
    AND (sc.curator_id IS DISTINCT FROM auth.uid())
);
