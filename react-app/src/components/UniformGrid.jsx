import React from 'react';
import { parseCardStyle } from '../lib/cardStyles.js';
import EventCard from './EventCard.jsx';

export default function UniformGrid({ events, filterTerm, onCategoryFilter, variant, columnCount }) {
  if (!events || !events.length) return null;

  const { layout } = parseCardStyle(variant);
  const needsWrapper = layout === 'grid';

  return (
    <div
      className="grid w-full gap-4"
      style={{ gridTemplateColumns: `repeat(${columnCount}, minmax(0, 1fr))` }}
    >
      {events.map(event => (
        needsWrapper ? (
          <div key={event.id} className="h-[320px] overflow-hidden rounded-lg [&>*]:!mb-0">
            <EventCard
              event={event}
              filterTerm={filterTerm}
              onCategoryFilter={onCategoryFilter}
              variant={variant}
            />
          </div>
        ) : (
          <EventCard
            key={event.id}
            event={event}
            filterTerm={filterTerm}
            onCategoryFilter={onCategoryFilter}
            variant={variant}
          />
        )
      ))}
    </div>
  );
}
