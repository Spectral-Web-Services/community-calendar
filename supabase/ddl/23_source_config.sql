-- Source configuration table: marks certain sources as hidden from the main calendar view.
-- Hidden sources are still ingested normally and appear in auto-collection embeds.

CREATE TABLE IF NOT EXISTS source_config (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  city text NOT NULL,
  source_name text NOT NULL,
  curator_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  hidden_from_main boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  UNIQUE(city, source_name)
);

-- RLS: publicly readable; only the owning curator can insert/update/delete their rows.
ALTER TABLE source_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "source_config_select" ON source_config
  FOR SELECT USING (true);

CREATE POLICY "source_config_insert" ON source_config
  FOR INSERT WITH CHECK (auth.uid() = curator_id);

CREATE POLICY "source_config_update" ON source_config
  FOR UPDATE USING (auth.uid() = curator_id);

CREATE POLICY "source_config_delete" ON source_config
  FOR DELETE USING (auth.uid() = curator_id);

-- View that automatically excludes hidden sources from the main calendar.
-- Auto-collections query the `events` table directly, so they bypass this filter.
CREATE OR REPLACE VIEW public_events AS
SELECT e.*
FROM events e
WHERE NOT EXISTS (
  SELECT 1 FROM source_config sc
  WHERE sc.city = e.city
    AND sc.source_name = e.source
    AND sc.hidden_from_main = true
);
