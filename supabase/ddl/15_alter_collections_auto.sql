-- Add auto-collection support: type and rules columns
ALTER TABLE collections ADD COLUMN IF NOT EXISTS type text NOT NULL DEFAULT 'manual';
ALTER TABLE collections ADD COLUMN IF NOT EXISTS rules jsonb;
