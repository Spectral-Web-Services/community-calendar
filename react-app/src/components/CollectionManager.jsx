import React, { useState, useEffect } from 'react';
import { Plus, Trash2, ChevronDown, ChevronRight, Link2, X, Zap } from 'lucide-react';
import { useCollections } from '../hooks/useCollections.js';
import { usePicks } from '../hooks/usePicks.jsx';
import { SUPABASE_URL, SUPABASE_KEY } from '../lib/supabase.js';
import { categoryList } from '../lib/categories.js';
import { formatDayOfWeek, formatMonthDay } from '../lib/helpers.js';

/** Summary text for auto-collection rules */
function ruleSummary(rules) {
  if (!rules) return '';
  const parts = [];
  if (rules.sources?.length) parts.push(rules.sources.join(', '));
  if (rules.categories?.length) parts.push(rules.categories.join(', '));
  return parts.join(' · ');
}

export default function CollectionManager({ expanded, onExpandedChange }) {
  const {
    collections, createCollection, deleteCollection,
    getCollectionEvents, removeEventFromCollection,
  } = useCollections();
  const { city } = usePicks();

  const [newName, setNewName] = useState('');
  const [newType, setNewType] = useState('manual');
  const [selectedSources, setSelectedSources] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [availableSources, setAvailableSources] = useState([]);
  const [creating, setCreating] = useState(false);
  const setExpanded = onExpandedChange;
  const [expandedEvents, setExpandedEvents] = useState([]);
  const [copied, setCopied] = useState(null);

  // Fetch distinct sources when type is 'auto'
  useEffect(() => {
    if (newType !== 'auto' || !city) { setAvailableSources([]); return; }
    fetch(
      `${SUPABASE_URL}/rest/v1/rpc/`,
      { headers: { apikey: SUPABASE_KEY } }
    ).catch(() => {});
    // Use a simple query with select and distinct isn't directly supported by PostgREST,
    // so query events grouped by source
    fetch(
      `${SUPABASE_URL}/rest/v1/events?city=eq.${encodeURIComponent(city)}&select=source&order=source`,
      { headers: { apikey: SUPABASE_KEY, Accept: 'application/json' } }
    )
      .then(r => r.json())
      .then(data => {
        if (!Array.isArray(data)) return;
        const unique = [...new Set(data.map(d => d.source).filter(Boolean))];
        setAvailableSources(unique.sort());
      })
      .catch(() => setAvailableSources([]));
  }, [newType, city]);

  // Load events when a collection is expanded
  useEffect(() => {
    if (!expanded) { setExpandedEvents([]); return; }
    getCollectionEvents(expanded).then(setExpandedEvents);
  }, [expanded, getCollectionEvents, collections]);

  const handleCreate = async () => {
    const name = newName.trim();
    if (!name) return;
    setCreating(true);
    if (newType === 'auto') {
      const rules = {};
      if (selectedSources.length) rules.sources = selectedSources;
      if (selectedCategories.length) rules.categories = selectedCategories;
      await createCollection(name, { type: 'auto', rules });
    } else {
      await createCollection(name);
    }
    setNewName('');
    setNewType('manual');
    setSelectedSources([]);
    setSelectedCategories([]);
    setCreating(false);
  };

  const handleDelete = async (id) => {
    await deleteCollection(id);
    if (expanded === id) setExpanded(null);
  };

  const handleRemoveEvent = async (collectionId, eventId, sourceUid) => {
    await removeEventFromCollection(collectionId, eventId, sourceUid);
    setExpandedEvents(prev => prev.filter(ce => ce.event_id !== eventId));
  };

  const copyShareUrl = (id) => {
    const url = `${window.location.origin}${window.location.pathname}?feed=${id}`;
    navigator.clipboard.writeText(url);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const toggleSource = (s) => setSelectedSources(prev =>
    prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s]
  );
  const toggleCategory = (c) => setSelectedCategories(prev =>
    prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]
  );

  return (
    <div className="mb-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-2">Collections</h3>

      {/* Create new */}
      <div className="mb-3">
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={newName}
            onChange={e => setNewName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleCreate()}
            placeholder="New collection name…"
            className="flex-1 px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-gray-400"
          />
          <button
            onClick={handleCreate}
            disabled={creating || !newName.trim()}
            className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-40"
          >
            <Plus size={14} /> New
          </button>
        </div>

        {/* Type toggle */}
        <div className="flex gap-1 mb-2">
          <button
            onClick={() => setNewType('manual')}
            className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
              newType === 'manual'
                ? 'bg-gray-900 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Manual
          </button>
          <button
            onClick={() => setNewType('auto')}
            className={`px-3 py-1 text-xs font-medium rounded-md transition-colors flex items-center gap-1 ${
              newType === 'auto'
                ? 'bg-gray-900 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <Zap size={11} /> Auto
          </button>
        </div>

        {/* Auto-collection rules panel */}
        {newType === 'auto' && (
          <div className="border border-gray-200 rounded-lg p-3 space-y-3 bg-gray-50">
            {/* Sources */}
            <div>
              <p className="text-xs font-medium text-gray-600 mb-1">Sources</p>
              {availableSources.length === 0 ? (
                <p className="text-xs text-gray-400">Loading sources…</p>
              ) : (
                <div className="flex flex-wrap gap-1.5">
                  {availableSources.map(s => (
                    <label key={s} className="flex items-center gap-1 text-xs text-gray-700 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedSources.includes(s)}
                        onChange={() => toggleSource(s)}
                        className="rounded border-gray-300 text-gray-900 focus:ring-gray-500 h-3.5 w-3.5"
                      />
                      {s}
                    </label>
                  ))}
                </div>
              )}
            </div>

            {/* Categories */}
            <div>
              <p className="text-xs font-medium text-gray-600 mb-1">Categories</p>
              <div className="flex flex-wrap gap-1.5">
                {categoryList.map(c => (
                  <label key={c} className="flex items-center gap-1 text-xs text-gray-700 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedCategories.includes(c)}
                      onChange={() => toggleCategory(c)}
                      className="rounded border-gray-300 text-gray-900 focus:ring-gray-500 h-3.5 w-3.5"
                    />
                    {c}
                  </label>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Collection list */}
      {collections.length === 0 && (
        <p className="text-xs text-gray-400">No collections yet. Create one to organize your picks.</p>
      )}

      <div className="space-y-1">
        {collections.map(col => {
          const isAuto = col.type === 'auto';
          const summary = isAuto ? ruleSummary(col.rules) : '';
          return (
            <div key={col.id} className="border border-gray-100 rounded-lg bg-white">
              <div className="flex items-center gap-2 px-3 py-2">
                <button
                  onClick={() => setExpanded(expanded === col.id ? null : col.id)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  {expanded === col.id ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                </button>
                {isAuto && <Zap size={12} className="text-amber-500 flex-shrink-0" />}
                <div className="flex-1 min-w-0">
                  <span className="text-sm font-medium text-gray-800 truncate block">{col.name}</span>
                  {isAuto && summary && (
                    <span className="text-[10px] text-gray-400 truncate block">{summary}</span>
                  )}
                </div>
                <button
                  onClick={() => copyShareUrl(col.id)}
                  className={`text-xs px-2 py-0.5 rounded transition-colors ${
                    copied === col.id
                      ? 'bg-green-100 text-green-700'
                      : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'
                  }`}
                  title="Copy share link"
                >
                  {copied === col.id ? 'Copied!' : <Link2 size={13} />}
                </button>
                <button
                  onClick={() => handleDelete(col.id)}
                  className="text-gray-300 hover:text-red-400 transition-colors"
                  title="Delete collection"
                >
                  <Trash2 size={13} />
                </button>
              </div>

              {/* Expanded: show events in this collection */}
              {expanded === col.id && (
                <div className="border-t border-gray-50 px-3 py-2">
                  {expandedEvents.length === 0 ? (
                    <p className="text-xs text-gray-400">
                      {isAuto ? 'No matching events.' : 'No events in this collection. Add them from your picks below.'}
                    </p>
                  ) : (
                    <div className="space-y-1">
                      {expandedEvents.map(ce => {
                        const ev = ce.events;
                        if (!ev) return null;
                        return (
                          <div key={ce.id || ce.event_id} className="flex items-center gap-2 text-xs text-gray-600">
                            <span className="flex-1 truncate">
                              {ev.title}
                              {ev.start_time && (
                                <span className="text-gray-400 ml-1">
                                  · {formatDayOfWeek(ev.start_time)} {formatMonthDay(ev.start_time)}
                                </span>
                              )}
                            </span>
                            <button
                              onClick={() => handleRemoveEvent(col.id, ce.event_id, ev.source_uid)}
                              className="text-gray-300 hover:text-red-400 flex-shrink-0"
                              title={isAuto ? 'Exclude from auto-collection' : 'Remove from collection'}
                            >
                              <X size={12} />
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
