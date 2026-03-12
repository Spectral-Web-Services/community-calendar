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
