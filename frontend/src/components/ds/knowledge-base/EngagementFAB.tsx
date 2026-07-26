// EngagementFAB — two stacked floating pills bottom-right (Yuque parity).
// Tapping either one scrolls to the matching anchor inside the page so the
// canonical interaction (the ArticleFooter at the bottom) still runs the show.
import React from 'react';
import { ThumbsUp, MessageCircle } from 'lucide-react';
import { cn } from '../../../lib/utils';

interface EngagementFABProps {
  likes?: number;
  comments?: number;
  onLikeClick?: () => void;
  onCommentClick?: () => void;
}

const formatCount = (n: number): string => (n >= 100 ? '99+' : String(n));

const FabPill: React.FC<{
  icon: React.ReactNode;
  count: number;
  ariaLabel: string;
  onClick?: () => void;
}> = ({ icon, count, ariaLabel, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    aria-label={ariaLabel}
    className={cn(
      'group relative flex h-10 w-10 items-center justify-center rounded-full',
      'bg-ds-surface-1 text-ds-fg-muted shadow-ds-2',
      'border border-ds-border transition-all duration-150',
      'hover:-translate-y-0.5 hover:shadow-ds-3 hover:text-ds-fg active:scale-95',
    )}
  >
    {icon}
    <span
      className={cn(
        'absolute -bottom-1 -right-1 min-w-[20px] rounded-full',
        'bg-ds-surface-1 px-1 text-center text-[10px] font-medium text-ds-fg-muted',
        'border border-ds-border',
      )}
    >
      {formatCount(count)}
    </span>
  </button>
);

const EngagementFAB: React.FC<EngagementFABProps> = ({
  likes,
  comments,
  onLikeClick,
  onCommentClick,
}) => {
  return (
    // The mobile reading column uses the canonical ArticleFooter for these
    // actions; a second fixed stack would cover text. Desktop keeps the
    // shortcuts where the wider viewport has room for them.
    <div className="fixed bottom-6 right-6 z-30 hidden flex-col gap-3 sm:flex">
      {typeof likes === 'number' && (
        <FabPill
          icon={<ThumbsUp size={18} />}
          count={likes}
          ariaLabel="Likes"
          onClick={onLikeClick}
        />
      )}
      {typeof comments === 'number' && (
        <FabPill
          icon={<MessageCircle size={18} />}
          count={comments}
          ariaLabel="Comments"
          onClick={onCommentClick}
        />
      )}
    </div>
  );
};

export default EngagementFAB;
