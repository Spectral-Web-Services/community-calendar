import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://mrarvzihuwgfjvricdte.supabase.co';
const SUPABASE_KEY = 'sb_publishable_7e4Pgqdr22FuLsMVhRYwiA_RVxG5Dw1';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yYXJ2emlodXdnZmp2cmljZHRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4OTI4OTIsImV4cCI6MjA4ODQ2ODg5Mn0._WmlT1YF1_sxAcl3UfpeWvBhg4TJ1couL40sYTYBhkw';

// Use the anon JWT key for createClient — the publishable key is not a JWT
// and gets rejected by the edge function gateway.
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
export { SUPABASE_URL, SUPABASE_KEY, SUPABASE_ANON_KEY };
