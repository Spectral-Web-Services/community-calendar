-- Migration: Scope curators to specific cities
-- A curator with cities = '{portland,boston}' can only curate events in those cities.
-- Empty/null array = global curator (all cities). Admins remain implicitly global.

-- ============================================================
-- 1. Add cities column to curator tables
-- ============================================================

ALTER TABLE curator_users ADD COLUMN IF NOT EXISTS cities text[] DEFAULT '{}';
ALTER TABLE curator_github_users ADD COLUMN IF NOT EXISTS cities text[] DEFAULT '{}';
ALTER TABLE curator_google_users ADD COLUMN IF NOT EXISTS cities text[] DEFAULT '{}';

-- ============================================================
-- 2. Create is_curator_for_city() helper function
-- ============================================================

CREATE OR REPLACE FUNCTION public.is_curator_for_city(check_city text)
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
STABLE
SET search_path = ''
AS $$
  SELECT CASE WHEN
    EXISTS (SELECT 1 FROM public.admin_users WHERE user_id = auth.uid())
    OR EXISTS (SELECT 1 FROM public.admin_github_users
               WHERE github_user = public.get_my_github_username())
    OR EXISTS (SELECT 1 FROM public.admin_google_users
               WHERE google_email = public.get_my_google_email())
  THEN true
  ELSE
    EXISTS (SELECT 1 FROM public.curator_users
            WHERE user_id = auth.uid()
              AND (cities = '{}' OR cities IS NULL OR check_city = ANY(cities)))
    OR EXISTS (SELECT 1 FROM public.curator_github_users
               WHERE github_user = public.get_my_github_username()
                 AND (cities = '{}' OR cities IS NULL OR check_city = ANY(cities)))
    OR EXISTS (SELECT 1 FROM public.curator_google_users
               WHERE google_email = public.get_my_google_email()
                 AND (cities = '{}' OR cities IS NULL OR check_city = ANY(cities)))
  END;
$$;

-- ============================================================
-- 3. Update RLS policies to use is_curator_for_city()
-- ============================================================

-- event_enrichments: has city column
DROP POLICY IF EXISTS "Curators can insert own enrichments" ON event_enrichments;
DROP POLICY IF EXISTS "Curators can update own enrichments" ON event_enrichments;
DROP POLICY IF EXISTS "Curators can delete own enrichments" ON event_enrichments;

CREATE POLICY "Curators can insert own enrichments"
  ON event_enrichments FOR INSERT
  WITH CHECK (auth.uid() = curator_id AND public.is_curator_for_city(city));

CREATE POLICY "Curators can update own enrichments"
  ON event_enrichments FOR UPDATE
  USING (auth.uid() = curator_id AND public.is_curator_for_city(city));

CREATE POLICY "Curators can delete own enrichments"
  ON event_enrichments FOR DELETE
  USING (auth.uid() = curator_id AND public.is_curator_for_city(city));

-- category_overrides: no city column, join via event_id
DROP POLICY IF EXISTS "Curators can insert overrides" ON category_overrides;
DROP POLICY IF EXISTS "Curators can update own overrides" ON category_overrides;

CREATE POLICY "Curators can insert overrides"
  ON category_overrides FOR INSERT
  WITH CHECK (auth.uid() = curator_id AND public.is_curator_for_city((SELECT city FROM public.events WHERE id = event_id)));

CREATE POLICY "Curators can update own overrides"
  ON category_overrides FOR UPDATE
  USING (auth.uid() = curator_id AND public.is_curator_for_city((SELECT city FROM public.events WHERE id = event_id)));

-- collections: has city column
DROP POLICY IF EXISTS "collections_insert_curator" ON collections;
DROP POLICY IF EXISTS "collections_update_curator" ON collections;
DROP POLICY IF EXISTS "collections_delete_curator" ON collections;

CREATE POLICY "collections_insert_curator"
  ON collections FOR INSERT
  WITH CHECK (auth.uid() = user_id AND public.is_curator_for_city(city));

CREATE POLICY "collections_update_curator"
  ON collections FOR UPDATE
  USING (auth.uid() = user_id AND public.is_curator_for_city(city))
  WITH CHECK (auth.uid() = user_id AND public.is_curator_for_city(city));

CREATE POLICY "collections_delete_curator"
  ON collections FOR DELETE
  USING (auth.uid() = user_id AND public.is_curator_for_city(city));

-- collection_events: inherits city from collection
DROP POLICY IF EXISTS "collection_events_insert_curator" ON collection_events;
DROP POLICY IF EXISTS "collection_events_delete_curator" ON collection_events;

CREATE POLICY "collection_events_insert_curator"
  ON collection_events FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.collections
      WHERE id = collection_id AND user_id = auth.uid()
    )
    AND public.is_curator_for_city((SELECT city FROM public.collections WHERE id = collection_id))
  );

CREATE POLICY "collection_events_delete_curator"
  ON collection_events FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.collections
      WHERE id = collection_id AND user_id = auth.uid()
    )
    AND public.is_curator_for_city((SELECT city FROM public.collections WHERE id = collection_id))
  );

-- auto_collection_exclusions: inherits city from collection
DROP POLICY IF EXISTS "auto_collection_exclusions_insert_curator" ON auto_collection_exclusions;
DROP POLICY IF EXISTS "auto_collection_exclusions_delete_curator" ON auto_collection_exclusions;

CREATE POLICY "auto_collection_exclusions_insert_curator"
  ON auto_collection_exclusions FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.collections
      WHERE id = collection_id AND user_id = auth.uid()
    )
    AND public.is_curator_for_city((SELECT city FROM public.collections WHERE id = collection_id))
  );

CREATE POLICY "auto_collection_exclusions_delete_curator"
  ON auto_collection_exclusions FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.collections
      WHERE id = collection_id AND user_id = auth.uid()
    )
    AND public.is_curator_for_city((SELECT city FROM public.collections WHERE id = collection_id))
  );
