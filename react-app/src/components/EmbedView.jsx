import React, { useMemo, useEffect, useRef, useCallback } from 'react';
import { useCollection } from '../hooks/useCollection.js';
import { useColumnCount } from '../hooks/useColumnCount.js';
import { getMasonryColumns } from '../lib/helpers.js';
import MasonryGrid from './MasonryGrid.jsx';

/**
 * Minimal embeddable feed view.
 * URL params: embed={feedId}, style={cardStyle}, title={custom title}, bg={color}
 *
 * Posts height to parent window via postMessage so the host page
 * can auto-resize the iframe (no scroll-within-scroll).
 */
export default function EmbedView({ feedId, style, title, bg, mode }) {
  const isDark = mode === 'dark';
  const { collection, events, loading } = useCollection(feedId);
  const rawColumnCount = useColumnCount();
  const containerRef = useRef(null);
  const observerRef = useRef(null);

  const postHeight = useCallback(() => {
    const el = containerRef.current;
    if (!el) return;
    const height = document.documentElement.scrollHeight;
    window.parent.postMessage(
      { type: 'community-calendar-embed-resize', height },
      '*'
    );
  }, []);

  // Observe the container for size changes
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    observerRef.current?.disconnect();
    const observer = new ResizeObserver(postHeight);
    observer.observe(el);
    observerRef.current = observer;
    return () => observer.disconnect();
  }, [postHeight]);

  // Re-post height whenever content changes (events load, window resize)
  useEffect(() => {
    postHeight();
  }, [events, loading, postHeight]);

  useEffect(() => {
    window.addEventListener('resize', postHeight);
    return () => window.removeEventListener('resize', postHeight);
  }, [postHeight]);

  const cardStyle = style || collection?.card_style || 'compact';

  const oneColStyles = ['list'];
  const twoColStyles = ['compact', 'split', 'splitimage'];
  const columnCount = oneColStyles.includes(cardStyle) ? 1
    : twoColStyles.includes(cardStyle) ? Math.min(rawColumnCount, 2)
    : rawColumnCount;

  const { featuredEvents, regularEvents } = useMemo(() => {
    const featured = events.filter(e => e._featured);
    if (featured.length === 0) return { featuredEvents: [], regularEvents: events };
    return { featuredEvents: featured, regularEvents: events.filter(e => !e._featured) };
  }, [events]);

  const featuredColumns = useMemo(
    () => getMasonryColumns(featuredEvents, columnCount),
    [featuredEvents, columnCount]
  );

  const masonryColumns = useMemo(
    () => getMasonryColumns(regularEvents, columnCount),
    [regularEvents, columnCount]
  );

  const displayTitle = title || collection?.name;

  let content;
  if (loading) {
    content = (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-400"></div>
      </div>
    );
  } else if (!collection) {
    content = <p className="text-center text-gray-400 py-8 text-sm">Collection not found.</p>;
  } else if (events.length === 0) {
    content = <p className="text-center text-gray-400 py-8 text-sm">No events yet.</p>;
  } else {
    content = (
      <>
        {displayTitle && (
          <h1 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-3 px-1">{displayTitle}</h1>
        )}
        {featuredColumns.some(col => col.length > 0) && (
          <div className="mb-6">
            <MasonryGrid
              masonryColumns={featuredColumns}
              filterTerm=""
              onCategoryFilter={() => {}}
              variant={cardStyle}
            />
          </div>
        )}
        <MasonryGrid
          masonryColumns={masonryColumns}
          filterTerm=""
          onCategoryFilter={() => {}}
          variant={cardStyle}
        />
      </>
    );
  }

  return (
    <div ref={containerRef} className={`w-full px-3 py-4 ${isDark ? 'dark' : ''}`} style={{ backgroundColor: bg || 'transparent' }}>
      {content}
    </div>
  );
}
