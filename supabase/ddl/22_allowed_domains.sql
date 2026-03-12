-- Add domain allowlist for embed protection.
-- Empty array = no restriction (backward compatible).
-- Non-empty array = only those domains may embed the collection.
ALTER TABLE collections ADD COLUMN IF NOT EXISTS allowed_domains text[] DEFAULT '{}';
