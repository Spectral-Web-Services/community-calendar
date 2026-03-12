import { useState, useEffect, createContext, useContext } from 'react';
import { supabase, SUPABASE_URL, SUPABASE_KEY } from '../lib/supabase.js';
import { useAuth } from './useAuth.jsx';

const CuratorContext = createContext({ isCurator: false });

export function CuratorProvider({ children }) {
  const { user, session } = useAuth();
  const [isCurator, setIsCurator] = useState(false);

  useEffect(() => {
    if (!user || !session) {
      setIsCurator(false);
      return;
    }

    const headers = {
      apikey: SUPABASE_KEY,
      Authorization: 'Bearer ' + session.access_token,
    };

    // Check all three curator tables + admin tables in parallel.
    // RLS ensures each query returns at most the user's own row.
    async function check() {
      try {
        const urls = [
          `${SUPABASE_URL}/rest/v1/curator_users?select=user_id&user_id=eq.${user.id}&limit=1`,
          `${SUPABASE_URL}/rest/v1/curator_github_users?select=github_user&limit=1`,
          `${SUPABASE_URL}/rest/v1/curator_google_users?select=google_email&limit=1`,
          `${SUPABASE_URL}/rest/v1/admin_users?select=user_id&user_id=eq.${user.id}&limit=1`,
          `${SUPABASE_URL}/rest/v1/admin_github_users?select=github_user&limit=1`,
          `${SUPABASE_URL}/rest/v1/admin_google_users?select=google_email&limit=1`,
        ];

        const results = await Promise.all(
          urls.map(url => fetch(url, { headers }).then(r => r.json()).catch(() => []))
        );

        setIsCurator(results.some(r => Array.isArray(r) && r.length > 0));
      } catch (e) {
        setIsCurator(false);
      }
    }

    check();
  }, [user, session]);

  return (
    <CuratorContext.Provider value={{ isCurator }}>
      {children}
    </CuratorContext.Provider>
  );
}

export function useCurator() {
  return useContext(CuratorContext);
}
