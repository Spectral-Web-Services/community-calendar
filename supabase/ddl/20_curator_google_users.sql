-- Curator Google users table - allows preapproval before first sign-in

CREATE TABLE IF NOT EXISTS curator_google_users (
  google_email text PRIMARY KEY,
  cities text[] DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE curator_google_users ENABLE ROW LEVEL SECURITY;

-- Authenticated users can only read their own Google email row
CREATE POLICY "Users can view own google curator status"
  ON curator_google_users FOR SELECT
  TO authenticated
  USING (google_email = coalesce(public.get_my_google_email(), ''));

-- Service role manages curator grants/revokes
CREATE POLICY "Service role can manage google curator users"
  ON curator_google_users FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
