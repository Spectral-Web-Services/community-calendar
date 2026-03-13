import React, { useMemo, useEffect, useRef, useCallback } from 'react';
import { useCollection } from '../hooks/useCollection.js';
import { useColumnCount } from '../hooks/useColumnCount.js';
import { getMasonryColumns } from '../lib/helpers.js';
import MasonryGrid from './MasonryGrid.jsx';
import UniformGrid from './UniformGrid.jsx';

/**
 * Minimal embeddable feed view.
 * URL params:
 *   embed={feedId}          — collection to display
 *   style={cardStyle}       — card variant (accent, compact, grid, gridtile, etc.)
 *   featured_style={cardStyle} — card variant for featured events (defaults to style)
 *   title={custom title}    — single heading above all events (legacy, overrides both)
 *   featured_title={text}   — heading above featured events section
 *   normal_title={text}     — heading above regular events section
 *   bg={color}              — background color
 *   mode=dark               — dark mode
 *
 * Posts height to parent window via postMessage so the host page
 * can auto-resize the iframe (no scroll-within-scroll).
 */
export default function EmbedView({ feedId, style, featuredStyle, title, featuredTitle, normalTitle, bg, mode }) {
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
  const featuredCardStyle = featuredStyle || cardStyle;

  const gridStyles = ['grid', 'gridcompact', 'gridtile'];
  const isGridLayout = gridStyles.includes(cardStyle);
  const isFeaturedGridLayout = gridStyles.includes(featuredCardStyle);
  const oneColStyles = ['list'];
  const twoColStyles = ['compact', 'split', 'splitimage'];
  const threeColStyles = ['ticket'];
  const columnCount = oneColStyles.includes(cardStyle) ? 1
    : twoColStyles.includes(cardStyle) ? Math.min(rawColumnCount, 2)
    : threeColStyles.includes(cardStyle) ? Math.max(1, Math.min(rawColumnCount - 1, 3))
    : rawColumnCount;
  const featuredColumnCount = oneColStyles.includes(featuredCardStyle) ? 1
    : twoColStyles.includes(featuredCardStyle) ? Math.min(rawColumnCount, 2)
    : threeColStyles.includes(featuredCardStyle) ? Math.max(1, Math.min(rawColumnCount - 1, 3))
    : rawColumnCount;

  const { featuredEvents, regularEvents } = useMemo(() => {
    const featured = events.filter(e => e._featured);
    if (featured.length === 0) return { featuredEvents: [], regularEvents: events };
    return { featuredEvents: featured, regularEvents: events.filter(e => !e._featured) };
  }, [events]);

  const featuredColumns = useMemo(
    () => getMasonryColumns(featuredEvents, featuredColumnCount),
    [featuredEvents, featuredColumnCount]
  );

  const masonryColumns = useMemo(
    () => getMasonryColumns(regularEvents, columnCount),
    [regularEvents, columnCount]
  );

  // Title resolution: legacy `title` param overrides both; otherwise use individual params
  const displayFeaturedTitle = title || featuredTitle;
  const displayNormalTitle = title ? null : normalTitle;

  // Domain allowlist check
  const domainBlocked = useMemo(() => {
    if (!collection?.allowed_domains?.length) return false;
    try {
      const referrerHost = new URL(document.referrer).hostname;
      return !collection.allowed_domains.some(d =>
        referrerHost === d || referrerHost.endsWith('.' + d)
      );
    } catch {
      // No referrer or invalid — block when allowlist is set
      return true;
    }
  }, [collection]);

  let content;
  if (loading) {
    content = (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-400"></div>
      </div>
    );
  } else if (!collection) {
    content = <p className="text-center text-gray-400 py-8 text-sm">Collection not found.</p>;
  } else if (domainBlocked) {
    content = <p className="text-center text-gray-400 py-8 text-sm">This embed is not authorized for this domain.</p>;
  } else if (events.length === 0) {
    content = <p className="text-center text-gray-400 py-8 text-sm">No events yet.</p>;
  } else {
    const hasFeatured = featuredEvents.length > 0;
    content = (
      <>
        {hasFeatured && (
          <div className="mb-6">
            {displayFeaturedTitle && (
              <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-3 px-1">{displayFeaturedTitle}</h2>
            )}
            {isFeaturedGridLayout ? (
              <UniformGrid
                events={featuredEvents}
                filterTerm=""
                onCategoryFilter={() => {}}
                variant={featuredCardStyle}
                columnCount={featuredColumnCount}
              />
            ) : (
              <MasonryGrid
                masonryColumns={featuredColumns}
                filterTerm=""
                onCategoryFilter={() => {}}
                variant={featuredCardStyle}
              />
            )}
          </div>
        )}
        {displayNormalTitle && (
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-3 px-1">{displayNormalTitle}</h2>
        )}
        {/* If no featured section exists and legacy title is set, show it above regular events */}
        {!hasFeatured && title && (
          <h1 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-3 px-1">{title}</h1>
        )}
        {isGridLayout ? (
          <UniformGrid
            events={regularEvents}
            filterTerm=""
            onCategoryFilter={() => {}}
            variant={cardStyle}
            columnCount={columnCount}
          />
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
  }

  return (
    <div ref={containerRef} className={`w-full px-3 py-4 ${isDark ? 'dark' : ''}`} style={{ backgroundColor: bg || 'transparent' }}>
      {content}
    </div>
  );
}
