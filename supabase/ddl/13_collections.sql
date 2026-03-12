-- Collections: named groups of events curated by a user
CREATE TABLE IF NOT EXISTS collections (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  city text NOT NULL,
  name text NOT NULL,
  card_style text DEFAULT 'accent',
  description text,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_collections_user_id ON collections(user_id);

-- RLS: public SELECT, owner-only INSERT/UPDATE/DELETE
ALTER TABLE collections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "collections_select_public"
  ON collections FOR SELECT
  USING (true);

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
