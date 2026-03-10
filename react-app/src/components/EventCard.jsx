import React, { useState } from 'react';
import { Card } from 'flowbite-react';
import { Info, CalendarPlus, Download } from 'lucide-react';
import {
  formatDayOfWeek,
  formatMonthDay,
  formatTime,
  getSnippet,
  getDescriptionSnippet,
  buildGoogleCalendarUrl,
  downloadEventICS,
} from '../lib/helpers.js';
import CategoryBadge from './CategoryBadge.jsx';

export default function EventCard({ event, filterTerm, onCategoryFilter }) {
  const [showDetail, setShowDetail] = useState(false);

  const dateStr = formatDayOfWeek(event.start_time) + ' ' + formatMonthDay(event.start_time);
  const timeStr = formatTime(event.start_time);
  const snippet = getSnippet(event.description, event.title);
  const searchSnippet = filterTerm ? getDescriptionSnippet(event.description, filterTerm) : null;

  return (
    <>
      <div className="mb-3">
        <Card
          className="max-w-sm"
          renderImage={event.image_url ? () => (
            <img
              src={event.image_url}
              alt=""
              className="w-full h-[180px] object-cover rounded-t-lg"
              loading="lazy"
            />
          ) : undefined}
        >
          <p className="text-sm text-gray-500">
            {dateStr}{timeStr ? `, ${timeStr}` : ''}
          </p>

          {event.url ? (
            <a
              href={event.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-lg font-bold tracking-tight text-gray-900 hover:text-blue-700 hover:underline"
            >
              {event.title}
            </a>
          ) : (
            <h5 className="text-lg font-bold tracking-tight text-gray-900">
              {event.title}
            </h5>
          )}

          {event.location && (
            <p className="font-normal text-sm text-gray-500">{event.location}</p>
          )}

          {event.source && (
            <p className="text-sm text-gray-400 italic">{event.source}</p>
          )}

          {searchSnippet && (
            <p
              className="text-sm text-gray-700"
              dangerouslySetInnerHTML={{
                __html: searchSnippet
                  .replace(/\*\*(.+?)\*\*/g, '<mark class="bg-yellow-200 text-yellow-800 px-0.5 rounded">$1</mark>')
              }}
            />
          )}

          {snippet && (
            <p
              className="font-normal text-sm text-gray-700 cursor-pointer"
              onClick={() => setShowDetail(true)}
            >
              {snippet}
            </p>
          )}

          <div className="flex items-center gap-2 pt-1">
            <CategoryBadge
              category={event.category}
              onClick={() => onCategoryFilter && onCategoryFilter(event.category)}
            />
            <div className="flex-1" />
            {(event.description || event.image_url) && (
              <button
                onClick={() => setShowDetail(true)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
                title="View details"
              >
                <Info size={18} />
              </button>
            )}
            <a
              href={buildGoogleCalendarUrl(event)}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-gray-600 transition-colors"
              title="Add to Google Calendar"
            >
              <CalendarPlus size={18} />
            </a>
            <button
              onClick={() => downloadEventICS(event)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              title="Download .ics"
            >
              <Download size={18} />
            </button>
          </div>
        </Card>
      </div>

      {/* Detail modal */}
      {showDetail && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          onClick={() => setShowDetail(false)}
        >
          <div
            className="bg-white rounded-lg max-w-lg w-full max-h-[80vh] overflow-y-auto p-6 shadow-xl"
            onClick={e => e.stopPropagation()}
          >
            <h2 className="text-xl font-bold tracking-tight text-gray-900 mb-2">{event.title}</h2>
            <p className="text-sm text-gray-500 mb-1">
              {dateStr}{timeStr ? `, ${timeStr}` : ''}
            </p>
            {event.location && <p className="text-sm text-gray-700 mb-1">{event.location}</p>}
            {event.source && <p className="text-sm text-gray-400 italic mb-3">{event.source}</p>}
            {event.image_url && (
              <img src={event.image_url} alt="" className="w-full object-contain mb-4 rounded-lg" />
            )}
            {event.description && (
              <div
                className="text-sm font-normal text-gray-700 whitespace-pre-wrap break-words"
                dangerouslySetInnerHTML={{ __html: event.description }}
              />
            )}
            {event.url && (
              <a
                href={event.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:underline mt-3 block"
              >
                Event link
              </a>
            )}
            <button
              onClick={() => setShowDetail(false)}
              className="mt-4 px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 text-sm font-medium transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </>
  );
}
