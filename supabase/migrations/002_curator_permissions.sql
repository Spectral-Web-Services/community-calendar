-- Migration: Curator permissions
-- Curators must be pre-approved. Regular logged-in users can still
-- pick/bookmark events, but curator actions (enrichments, category
-- overrides, featuring, collections) require curator allowlist membership.
-- Admins are implicitly curators.

-- ============================================================
-- 1. Create curator allowlist tables (mirrors admin pattern)
-- ============================================================

CREATE TABLE IF NOT EXISTS curator_users (
  user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE curator_users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own curator status"
  ON curator_users FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage curator users"
  ON curator_users FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- ---

CREATE TABLE IF NOT EXISTS curator_github_users (
  github_user text PRIMARY KEY,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE curator_github_users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own github curator status"
  ON curator_github_users FOR SELECT
  TO authenticated
  USING (github_user = coalesce(public.get_my_github_username(), ''));

CREATE POLICY "Service role can manage github curator users"
  ON curator_github_users FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- ---

CREATE TABLE IF NOT EXISTS curator_google_users (
  google_email text PRIMARY KEY,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE curator_google_users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own google curator status"
  ON curator_google_users FOR SELECT
  TO authenticated
  USING (google_email = coalesce(public.get_my_google_email(), ''));

CREATE POLICY "Service role can manage google curator users"
  ON curator_google_users FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- ============================================================
-- 2. Create is_curator() helper function
-- ============================================================

CREATE OR REPLACE FUNCTION public.is_curator()
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
STABLE
SET search_path = ''
AS $$
  SELECT EXISTS (SELECT 1 FROM public.curator_users WHERE user_id = auth.uid())
      OR EXISTS (SELECT 1 FROM public.curator_github_users
                 WHERE github_user = public.get_my_github_username())
      OR EXISTS (SELECT 1 FROM public.curator_google_users
                 WHERE google_email = public.get_my_google_email())
      -- Admins are implicitly curators
      OR EXISTS (SELECT 1 FROM public.admin_users WHERE user_id = auth.uid())
      OR EXISTS (SELECT 1 FROM public.admin_github_users
                 WHERE github_user = public.get_my_github_username())
      OR EXISTS (SELECT 1 FROM public.admin_google_users
                 WHERE google_email = public.get_my_google_email());
$$;

-- ============================================================
-- 3. Update RLS policies to require curator status
-- ============================================================

-- event_enrichments: drop old policies, create curator-gated ones
DROP POLICY IF EXISTS "Users can insert own enrichments" ON event_enrichments;
DROP POLICY IF EXISTS "Users can update own enrichments" ON event_enrichments;
DROP POLICY IF EXISTS "Users can delete own enrichments" ON event_enrichments;

CREATE POLICY "Curators can insert own enrichments"
  ON event_enrichments FOR INSERT
  WITH CHECK (auth.uid() = curator_id AND public.is_curator());

CREATE POLICY "Curators can update own enrichments"
  ON event_enrichments FOR UPDATE
  USING (auth.uid() = curator_id AND public.is_curator());

CREATE POLICY "Curators can delete own enrichments"
  ON event_enrichments FOR DELETE
  USING (auth.uid() = curator_id AND public.is_curator());

-- category_overrides: drop old policies, create curator-gated ones
DROP POLICY IF EXISTS "Auth users can insert overrides" ON category_overrides;
DROP POLICY IF EXISTS "Auth users can update own overrides" ON category_overrides;

CREATE POLICY "Curators can insert overrides"
  ON category_overrides FOR INSERT
  WITH CHECK (auth.uid() = curator_id AND public.is_curator());

CREATE POLICY "Curators can update own overrides"
  ON category_overrides FOR UPDATE
  USING (auth.uid() = curator_id AND public.is_curator());

-- collections: drop old policies, create curator-gated ones
DROP POLICY IF EXISTS "collections_insert_owner" ON collections;
DROP POLICY IF EXISTS "collections_update_owner" ON collections;
DROP POLICY IF EXISTS "collections_delete_owner" ON collections;

CREATE POLICY "collections_insert_curator"
  ON collections FOR INSERT
  WITH CHECK (auth.uid() = user_id AND public.is_curator());

CREATE POLICY "collections_update_curator"
  ON collections FOR UPDATE
  USING (auth.uid() = user_id AND public.is_curator())
  WITH CHECK (auth.uid() = user_id AND public.is_curator());

CREATE POLICY "collections_delete_curator"
  ON collections FOR DELETE
  USING (auth.uid() = user_id AND public.is_curator());

-- collection_events: drop old policies, create curator-gated ones
DROP POLICY IF EXISTS "collection_events_insert_owner" ON collection_events;
DROP POLICY IF EXISTS "collection_events_delete_owner" ON collection_events;

CREATE POLICY "collection_events_insert_curator"
  ON collection_events FOR INSERT
  WITH CHECK (
    public.is_curator() AND EXISTS (
      SELECT 1 FROM collections
      WHERE id = collection_id AND user_id = auth.uid()
    )
  );

CREATE POLICY "collection_events_delete_curator"
  ON collection_events FOR DELETE
  USING (
    public.is_curator() AND EXISTS (
      SELECT 1 FROM collections
      WHERE id = collection_id AND user_id = auth.uid()
    )
  );

-- auto_collection_exclusions: drop old policies, create curator-gated ones
DROP POLICY IF EXISTS "auto_collection_exclusions_insert_owner" ON auto_collection_exclusions;
DROP POLICY IF EXISTS "auto_collection_exclusions_delete_owner" ON auto_collection_exclusions;

CREATE POLICY "auto_collection_exclusions_insert_curator"
  ON auto_collection_exclusions FOR INSERT
  WITH CHECK (
    public.is_curator() AND EXISTS (
      SELECT 1 FROM collections
      WHERE id = collection_id AND user_id = auth.uid()
    )
  );

CREATE POLICY "auto_collection_exclusions_delete_curator"
  ON auto_collection_exclusions FOR DELETE
  USING (
    public.is_curator() AND EXISTS (
      SELECT 1 FROM collections
      WHERE id = collection_id AND user_id = auth.uid()
    )
  );
