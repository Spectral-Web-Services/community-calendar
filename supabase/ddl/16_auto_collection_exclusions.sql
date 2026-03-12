-- Auto-collection exclusions: events excluded from auto-collections by source_uid
CREATE TABLE IF NOT EXISTS auto_collection_exclusions (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  collection_id uuid REFERENCES collections(id) ON DELETE CASCADE NOT NULL,
  source_uid text NOT NULL,
  excluded_at timestamptz DEFAULT now(),
  UNIQUE(collection_id, source_uid)
);

CREATE INDEX IF NOT EXISTS idx_auto_collection_exclusions_collection_id
  ON auto_collection_exclusions(collection_id);

-- RLS: public SELECT, owner-only INSERT/DELETE (via join to collections.user_id)
ALTER TABLE auto_collection_exclusions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "auto_collection_exclusions_select_public"
  ON auto_collection_exclusions FOR SELECT
  USING (true);

CREATE POLICY "auto_collection_exclusions_insert_curator"
  ON auto_collection_exclusions FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM collections
      WHERE id = collection_id AND user_id = auth.uid()
    )
    AND public.is_curator_for_city((SELECT city FROM collections WHERE id = collection_id))
  );

CREATE POLICY "auto_collection_exclusions_delete_curator"
  ON auto_collection_exclusions FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM collections
      WHERE id = collection_id AND user_id = auth.uid()
    )
    AND public.is_curator_for_city((SELECT city FROM collections WHERE id = collection_id))
  );
