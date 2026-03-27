-- Source suggestions table - anonymous community submissions for new calendar sources

CREATE TABLE IF NOT EXISTS source_suggestions (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  city text NOT NULL,
  name text NOT NULL,
  url text,
  feed_type text,
  notes text,
  submitter_email text,
  status text NOT NULL DEFAULT 'submitted',
  reviewed_by uuid,
  reviewed_at timestamptz,
  created_at timestamptz DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE source_suggestions ENABLE ROW LEVEL SECURITY;

-- Anyone can insert suggestions (anonymous, no auth required)
CREATE POLICY "Anyone can insert suggestions"
  ON source_suggestions FOR INSERT
  WITH CHECK (true);

-- Anyone can read suggestions
CREATE POLICY "Anyone can read suggestions"
  ON source_suggestions FOR SELECT
  USING (true);

-- Curators can update suggestions for their city
CREATE POLICY "Curators can update suggestions"
  ON source_suggestions FOR UPDATE
  USING (public.is_curator_for_city(city))
  WITH CHECK (public.is_curator_for_city(city));
