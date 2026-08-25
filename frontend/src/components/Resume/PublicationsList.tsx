// src/components/Resume/PublicationsList.tsx
//
// The publications section body — a compact editorial reading list. Desktop
// cards alternate their figure side while preserving one stable reading order
// and a single-column mobile fallback.
import React from 'react';
import PublicationCard, { type PublicationCardData } from './PublicationCard';

interface PublicationsListProps {
  publications: PublicationCardData[];
  /** Author name to emphasise across the cards (the résumé owner). */
  highlightAuthor?: string;
}

const PublicationsList: React.FC<PublicationsListProps> = ({
  publications,
  highlightAuthor,
}) => (
  <div className="divide-y divide-ds-border">
    {publications.map((publication, index) => (
      <PublicationCard
        key={publication.id}
        publication={publication}
        index={index}
        highlightAuthor={highlightAuthor}
      />
    ))}
  </div>
);

export default PublicationsList;
