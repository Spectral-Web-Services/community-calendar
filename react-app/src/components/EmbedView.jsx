import React, { useMemo, useEffect, useRef } from 'react';
import { useCollection } from '../hooks/useCollection.js';
import { useColumnCount } from '../hooks/useColumnCount.js';
import { getMasonryColumns } from '../lib/helpers.js';
import MasonryGrid from './MasonryGrid.jsx';

/**
 * Minimal embeddable feed view.
 * URL params: embed={feedId}, style={cardStyle}, title={custom title}
 *
 * Posts height to parent window via postMessage so the host page
 * can auto-resize the iframe (no scroll-within-scroll).
 */
export default function EmbedView({ feedId, style, title }) {
  const { collection, events, loading } = useCollection(feedId);
  const rawColumnCount = useColumnCount();
  const containerRef = useRef(null);

  // Post document height to parent for auto-resize
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const post = () => {
      window.parent.postMessage(
        { type: 'community-calendar-embed-resize', height: el.scrollHeight },
        '*'
      );
    };
    const observer = new ResizeObserver(post);
    observer.observe(el);
    post();
    return () => observer.disconnect();
  }, []);

  const cardStyle = style || collection?.card_style || 'compact';

  const oneColStyles = ['list'];
  const twoColStyles = ['compact', 'split', 'splitimage'];
  const columnCount = oneColStyles.includes(cardStyle) ? 1
    : twoColStyles.includes(cardStyle) ? Math.min(rawColumnCount, 2)
    : rawColumnCount;

  const masonryColumns = useMemo(
    () => getMasonryColumns(events, columnCount),
    [events, columnCount]
  );

  const displayTitle = title || collection?.name;

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-400"></div>
      </div>
    );
  }

  if (!collection) {
    return <p className="text-center text-gray-400 py-8 text-sm">Collection not found.</p>;
  }

  return (
    <div ref={containerRef} className="w-full px-3 py-4 bg-gray-50">
      {displayTitle && (
        <h1 className="text-lg font-bold text-gray-900 mb-3 px-1">{displayTitle}</h1>
      )}
      {events.length === 0 ? (
        <p className="text-center text-gray-400 py-8 text-sm">No events yet.</p>
      ) : (
        <MasonryGrid
          masonryColumns={masonryColumns}
          filterTerm=""
          onCategoryFilter={() => {}}
          variant={cardStyle}
        />
      )}
    </div>
  );
}
