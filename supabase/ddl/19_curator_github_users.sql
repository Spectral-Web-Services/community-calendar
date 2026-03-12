-- Curator GitHub users table - allows preapproval before first sign-in

CREATE TABLE IF NOT EXISTS curator_github_users (
  github_user text PRIMARY KEY,
  cities text[] DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE curator_github_users ENABLE ROW LEVEL SECURITY;

-- Authenticated users can only read their own GitHub username row
CREATE POLICY "Users can view own github curator status"
  ON curator_github_users FOR SELECT
  TO authenticated
  USING (github_user = coalesce(public.get_my_github_username(), ''));

-- Service role manages curator grants/revokes
CREATE POLICY "Service role can manage github curator users"
  ON curator_github_users FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
