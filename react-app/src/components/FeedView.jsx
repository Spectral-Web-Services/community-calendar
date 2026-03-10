import React, { useState, useMemo, useCallback } from 'react';
import { useCollection } from '../hooks/useCollection.js';
import { useCollections } from '../hooks/useCollections.js';
import { useAuth } from '../hooks/useAuth.jsx';
import { useColumnCount } from '../hooks/useColumnCount.js';
import { FeedProvider } from '../hooks/useFeedContext.jsx';
import { getMasonryColumns } from '../lib/helpers.js';
import MasonryGrid from './MasonryGrid.jsx';
import StyleSwitcher from './StyleSwitcher.jsx';

export default function FeedView({ feedId }) {
  const { collection, events: rawEvents, loading } = useCollection(feedId);
  const { user } = useAuth();
  const { removeEventFromCollection } = useCollections();
  const rawColumnCount = useColumnCount();

  const [styleOverride, setStyleOverride] = useState(null);
  const [removedIds, setRemovedIds] = useState(new Set());
  const cardStyle = styleOverride || collection?.card_style || 'accent';

  const oneColStyles = ['list'];
  const twoColStyles = ['compact', 'split', 'splitimage'];
  const columnCount = oneColStyles.includes(cardStyle) ? 1
    : twoColStyles.includes(cardStyle) ? Math.min(rawColumnCount, 2)
    : rawColumnCount;

  const events = useMemo(
    () => rawEvents.filter(ev => !removedIds.has(ev.id)),
    [rawEvents, removedIds]
  );

  const masonryColumns = useMemo(
    () => getMasonryColumns(events, columnCount),
    [events, columnCount]
  );

  const isOwner = user && collection && user.id === collection.user_id;

  const handleRemoveEvent = useCallback(async (event) => {
    if (!collection) return;
    await removeEventFromCollection(collection.id, event.id, event.source_uid, { type: collection.type });
    setRemovedIds(prev => new Set(prev).add(event.id));
  }, [collection, removeEventFromCollection]);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600"></div>
      </div>
    );
  }

  if (!collection) {
    return (
      <div className="flex justify-center w-full min-h-screen bg-gray-50">
        <div className="max-w-[1400px] w-full px-4 py-12 text-center">
          <p className="text-lg text-gray-500">Collection not found.</p>
        </div>
      </div>
    );
  }

  const grid = (
    <>
      <StyleSwitcher value={cardStyle} onChange={setStyleOverride} />

      {events.length === 0 ? (
        <p className="text-center text-gray-400 py-12">This collection has no events yet.</p>
      ) : (
        <MasonryGrid
          masonryColumns={masonryColumns}
          filterTerm=""
          onCategoryFilter={() => {}}
          variant={cardStyle}
        />
      )}
    </>
  );

  return (
    <div className="flex justify-center w-full overflow-x-hidden bg-gray-50 min-h-screen">
      <div className="max-w-[1400px] w-full px-4 py-6">
        {/* Collection header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">{collection.name}</h1>
          {collection.type === 'auto' && collection.rules && (
            <p className="text-sm text-gray-500 mt-1">
              Auto-updating
              {collection.rules.categories?.length ? ` · ${collection.rules.categories.join(', ')}` : ''}
              {collection.rules.sources?.length ? ` from ${collection.rules.sources.join(', ')}` : ''}
            </p>
          )}
          {collection.description && (
            <p className="text-gray-500 mt-1">{collection.description}</p>
          )}
          <p className="text-xs text-gray-400 mt-1">
            {events.length} event{events.length !== 1 ? 's' : ''}
          </p>
        </div>

        {isOwner ? (
          <FeedProvider collection={collection} onRemoveEvent={handleRemoveEvent}>
            {grid}
          </FeedProvider>
        ) : (
          grid
        )}
      </div>
    </div>
  );
}
