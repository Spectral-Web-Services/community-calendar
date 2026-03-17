-- Pending events table - community-submitted events awaiting curator approval

CREATE TABLE IF NOT EXISTS pending_events (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  title text NOT NULL,
  start_time timestamptz NOT NULL,
  end_time timestamptz,
  location text,
  description text,
  url text,
  city text,
  submitted_by uuid REFERENCES auth.users(id),  -- nullable: anonymous submissions allowed
  submitted_at timestamptz DEFAULT now(),
  submission_type text,        -- 'image', 'text', 'manual'
  status text DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
  reviewed_by uuid,
  reviewed_at timestamptz,
  original_text text           -- pasted text or transcript
);

-- Enable Row Level Security
ALTER TABLE pending_events ENABLE ROW LEVEL SECURITY;

-- Anyone can submit events (anonymous, no auth required)
CREATE POLICY "Anyone can insert pending events"
  ON pending_events FOR INSERT
  WITH CHECK (true);

-- Curators can read all pending events; authenticated users can read their own
CREATE POLICY "Curators can read all pending events"
  ON pending_events FOR SELECT
  USING (public.is_curator() OR (auth.uid() IS NOT NULL AND auth.uid() = submitted_by));

-- Curators can update pending events (approve/reject) for their city
CREATE POLICY "Curators can update pending events"
  ON pending_events FOR UPDATE
  USING (public.is_curator_for_city(city));

-- Curators can delete pending events for their city
CREATE POLICY "Curators can delete pending events"
  ON pending_events FOR DELETE
  USING (public.is_curator_for_city(city));
