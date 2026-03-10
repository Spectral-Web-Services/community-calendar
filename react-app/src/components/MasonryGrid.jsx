import React from 'react';
import EventCard from './EventCard.jsx';

export default function MasonryGrid({ masonryColumns, filterTerm, onCategoryFilter }) {
  if (!masonryColumns || !masonryColumns.length) return null;

  return (
    <div className="flex gap-4 items-start w-full">
      {masonryColumns.map((column, colIdx) => (
        <div key={colIdx} className="flex-1 min-w-0 flex flex-col">
          {column.map(event => (
            <EventCard
              key={event.id}
              event={event}
              filterTerm={filterTerm}
              onCategoryFilter={onCategoryFilter}
            />
          ))}
        </div>
      ))}
    </div>
  );
}
