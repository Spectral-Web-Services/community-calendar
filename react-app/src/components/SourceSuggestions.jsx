import React, { useState, useEffect, useMemo } from 'react';
import { Loader2, ExternalLink, Mail } from 'lucide-react';
import { useAuth } from '../hooks/useAuth.jsx';
import { SUPABASE_URL, SUPABASE_KEY } from '../lib/supabase.js';

const STATUS_OPTIONS = [
  { value: 'submitted', label: 'Submitted', color: 'bg-gray-100 text-gray-600' },
  { value: 'will do', label: 'Will do', color: 'bg-blue-50 text-blue-700' },
  { value: 'done', label: 'Done', color: 'bg-green-50 text-green-700' },
  { value: 'rejected', label: 'Rejected', color: 'bg-red-50 text-red-700' },
  { value: "can't do", label: "Can't do", color: 'bg-amber-50 text-amber-700' },
];

const FEED_LABELS = { ics: 'ICS', rss: 'RSS', webpage: 'Webpage', unknown: 'Unknown' };

export default function SourceSuggestions({ city }) {
  const { user, session } = useAuth();
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);

  const headers = useMemo(() => ({
    apikey: SUPABASE_KEY,
    Authorization: 'Bearer ' + session?.access_token,
  }), [session]);

  useEffect(() => {
    if (!session) return;
    setLoading(true);
    const params = new URLSearchParams({ order: 'created_at.desc' });
    if (city) params.set('city', `eq.${city}`);

    fetch(`${SUPABASE_URL}/rest/v1/source_suggestions?${params}`, { headers })
      .then(r => r.json())
      .then(data => setSuggestions(Array.isArray(data) ? data : []))
      .catch(() => setSuggestions([]))
      .finally(() => setLoading(false));
  }, [session, city]);

  async function handleStatusChange(suggestion, newStatus) {
    setUpdatingId(suggestion.id);
    try {
      const res = await fetch(`${SUPABASE_URL}/rest/v1/source_suggestions?id=eq.${suggestion.id}`, {
        method: 'PATCH',
        headers: { ...headers, 'Content-Type': 'application/json', Prefer: 'return=minimal' },
        body: JSON.stringify({
          status: newStatus,
          reviewed_by: user?.id || null,
          reviewed_at: new Date().toISOString(),
        }),
      });
      if (!res.ok) throw new Error('Update failed');
      setSuggestions(prev => prev.map(s =>
        s.id === suggestion.id ? { ...s, status: newStatus, reviewed_by: user?.id, reviewed_at: new Date().toISOString() } : s
      ));
    } catch (err) {
      console.error(err);
    } finally {
      setUpdatingId(null);
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600"></div>
      </div>
    );
  }

  if (suggestions.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400 text-sm">
        No source suggestions
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-gray-500 mb-2">
        {suggestions.length} source suggestion{suggestions.length !== 1 ? 's' : ''}
      </p>
      {suggestions.map(s => {
        const statusInfo = STATUS_OPTIONS.find(o => o.value === s.status) || STATUS_OPTIONS[0];
        const isBusy = updatingId === s.id;

        return (
          <div key={s.id} className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  {s.feed_type && (
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-gray-100 text-gray-500">
                      {FEED_LABELS[s.feed_type] || s.feed_type}
                    </span>
                  )}
                  <span className="text-xs text-gray-400">
                    {new Date(s.created_at).toLocaleDateString()}
                  </span>
                </div>

                <p className="font-semibold text-gray-900 text-sm">{s.name}</p>

                {s.url && (
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 mt-0.5"
                  >
                    {s.url.length > 60 ? s.url.substring(0, 60) + '...' : s.url}
                    <ExternalLink size={10} />
                  </a>
                )}

                {s.notes && (
                  <p className="text-xs text-gray-400 mt-1">{s.notes}</p>
                )}

                {s.submitter_email && (
                  <p className="inline-flex items-center gap-1 text-xs text-gray-400 mt-1">
                    <Mail size={10} />
                    {s.submitter_email}
                  </p>
                )}
              </div>

              <div className="flex items-center gap-2 flex-shrink-0">
                {isBusy && <Loader2 size={14} className="animate-spin text-gray-400" />}
                <select
                  value={s.status}
                  onChange={e => handleStatusChange(s, e.target.value)}
                  disabled={isBusy}
                  className={`rounded-lg px-2 py-1 text-xs font-medium border-0 cursor-pointer focus:ring-0 focus:outline-none disabled:opacity-40 ${statusInfo.color}`}
                >
                  {STATUS_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
