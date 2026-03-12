-- Helper function: returns true if the current user is a curator or admin

CREATE OR REPLACE FUNCTION public.is_curator()
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
STABLE
SET search_path = ''
AS $$
  SELECT EXISTS (SELECT 1 FROM public.curator_users WHERE user_id = auth.uid())
      OR EXISTS (SELECT 1 FROM public.curator_github_users
                 WHERE github_user = public.get_my_github_username())
      OR EXISTS (SELECT 1 FROM public.curator_google_users
                 WHERE google_email = public.get_my_google_email())
      -- Admins are implicitly curators
      OR EXISTS (SELECT 1 FROM public.admin_users WHERE user_id = auth.uid())
      OR EXISTS (SELECT 1 FROM public.admin_github_users
                 WHERE github_user = public.get_my_github_username())
      OR EXISTS (SELECT 1 FROM public.admin_google_users
                 WHERE google_email = public.get_my_google_email());
$$;

-- Helper function: returns true if the current user can curate the given city.
-- Admins are implicitly global. Curators with empty/null cities array are global.

CREATE OR REPLACE FUNCTION public.is_curator_for_city(check_city text)
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
STABLE
SET search_path = ''
AS $$
  SELECT CASE WHEN
    EXISTS (SELECT 1 FROM public.admin_users WHERE user_id = auth.uid())
    OR EXISTS (SELECT 1 FROM public.admin_github_users
               WHERE github_user = public.get_my_github_username())
    OR EXISTS (SELECT 1 FROM public.admin_google_users
               WHERE google_email = public.get_my_google_email())
  THEN true
  ELSE
    EXISTS (SELECT 1 FROM public.curator_users
            WHERE user_id = auth.uid()
              AND (cities = '{}' OR cities IS NULL OR check_city = ANY(cities)))
    OR EXISTS (SELECT 1 FROM public.curator_github_users
               WHERE github_user = public.get_my_github_username()
                 AND (cities = '{}' OR cities IS NULL OR check_city = ANY(cities)))
    OR EXISTS (SELECT 1 FROM public.curator_google_users
               WHERE google_email = public.get_my_google_email()
                 AND (cities = '{}' OR cities IS NULL OR check_city = ANY(cities)))
  END;
$$;
