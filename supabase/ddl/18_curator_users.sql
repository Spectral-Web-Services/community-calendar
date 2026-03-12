-- Curator users table - server-authorized access for curator UI/actions

CREATE TABLE IF NOT EXISTS curator_users (
  user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  cities text[] DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE curator_users ENABLE ROW LEVEL SECURITY;

-- Users can only view their own curator row (presence means curator)
CREATE POLICY "Users can view own curator status"
  ON curator_users FOR SELECT
  USING (auth.uid() = user_id);

-- Service role manages curator grants/revokes
CREATE POLICY "Service role can manage curator users"
  ON curator_users FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
