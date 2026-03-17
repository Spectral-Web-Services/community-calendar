-- Nightly cleanup of past events
-- Events older than 7 days are safe to remove; the frontend already filters
-- to start_time >= 1 hr ago, so these rows are invisible to users.
-- All FK references use ON DELETE CASCADE, so child rows are cleaned up automatically.

CREATE OR REPLACE FUNCTION public.cleanup_old_events()
RETURNS bigint
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  deleted_count bigint;
BEGIN
  DELETE FROM events
  WHERE start_time < now() - interval '7 days';

  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$;
