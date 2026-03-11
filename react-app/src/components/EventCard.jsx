import React from 'react';
import { Star } from 'lucide-react';
import { useIsEventFeatured } from '../hooks/useFeatured.jsx';
import ClassicCard from './cards/ClassicCard.jsx';
import AccentCard from './cards/AccentCard.jsx';
import MagazineCard from './cards/MagazineCard.jsx';
import CompactCard from './cards/CompactCard.jsx';
import ModernCard from './cards/ModernCard.jsx';
import OverlayCard from './cards/OverlayCard.jsx';
import AlwaysImageCard from './cards/AlwaysImageCard.jsx';
import MinimalCard from './cards/MinimalCard.jsx';
import SplitCard from './cards/SplitCard.jsx';
import SplitImageCard from './cards/SplitImageCard.jsx';
import PolaroidCard from './cards/PolaroidCard.jsx';
import TicketCard from './cards/TicketCard.jsx';
const VARIANTS = {
  classic: ClassicCard,
  accent: AccentCard,
  magazine: MagazineCard,
  compact: CompactCard,
  modern: ModernCard,
  overlay: OverlayCard,
  alwaysimage: AlwaysImageCard,
  minimal: MinimalCard,
  split: SplitCard,
  splitimage: SplitImageCard,
  polaroid: PolaroidCard,
  ticket: TicketCard,
  list: SplitCard,
};

export default function EventCard({ event, filterTerm, onCategoryFilter, variant }) {
  const CardComponent = VARIANTS[variant] || AccentCard;
  const featured = useIsEventFeatured(event.id) || event._featured;

  if (featured) {
    return (
      <div className="relative ring-2 ring-amber-400/60 rounded-lg">
        <div className="absolute top-2 right-2 z-10 text-amber-400">
          <Star size={14} fill="currentColor" />
        </div>
        <CardComponent event={event} filterTerm={filterTerm} onCategoryFilter={onCategoryFilter} />
      </div>
    );
  }

  return <CardComponent event={event} filterTerm={filterTerm} onCategoryFilter={onCategoryFilter} />;
}
