import React from 'react';
import { Heart, MessageCircle } from 'lucide-react';

interface MomentEngagementControlsProps {
  compact?: boolean;
  liked: boolean;
  likePending: boolean;
  language: 'en' | 'zh';
  onLike: () => void;
  onComment: () => void;
}

const MomentEngagementControls: React.FC<MomentEngagementControlsProps> = ({
  compact = false,
  liked,
  likePending,
  language,
  onLike,
  onComment,
}) => {
  const likeLabel = language === 'zh' ? '赞' : 'Like';
  const commentLabel = language === 'zh' ? '评论' : 'Comment';
  const iconClass = compact ? 'size-3.5' : 'size-[18px]';

  if (compact) {
    return (
      <span className="inline-flex shrink-0 items-center gap-3">
        <button
          type="button"
          aria-label={likeLabel}
          aria-pressed={liked}
          disabled={likePending}
          onClick={onLike}
          className={`inline-flex size-7 items-center justify-center rounded-ds-xs transition-colors focus-visible:shadow-ds-focus disabled:cursor-wait disabled:opacity-50 ${
            liked ? 'text-red-500' : 'text-ds-fg-subtle hover:text-ds-fg'
          }`}
        >
          <Heart className={iconClass} fill={liked ? 'currentColor' : 'none'} aria-hidden />
        </button>
        <button
          type="button"
          aria-label={commentLabel}
          onClick={onComment}
          className="inline-flex size-7 items-center justify-center rounded-ds-xs text-ds-fg-subtle transition-colors hover:text-ds-fg focus-visible:shadow-ds-focus"
        >
          <MessageCircle className={iconClass} aria-hidden />
        </button>
      </span>
    );
  }

  return (
    <div className="moment-engagement-controls grid h-11 grid-cols-2 divide-x divide-ds-border rounded-ds-sm bg-ds-surface-2">
      <button
        type="button"
        aria-label={likeLabel}
        aria-pressed={liked}
        disabled={likePending}
        onClick={onLike}
        className={`inline-flex items-center justify-center gap-2 rounded-l-ds-sm text-ds-sm font-medium transition-colors focus-visible:shadow-ds-focus disabled:cursor-wait disabled:opacity-50 ${
          liked ? 'text-red-500' : 'text-ds-fg-muted hover:bg-ds-surface-3 hover:text-ds-fg'
        }`}
      >
        <Heart className={iconClass} fill={liked ? 'currentColor' : 'none'} aria-hidden />
        <span>{language === 'zh' ? '赞' : 'Like'}</span>
      </button>
      <button
        type="button"
        aria-label={commentLabel}
        onClick={onComment}
        className="inline-flex items-center justify-center gap-2 rounded-r-ds-sm text-ds-sm font-medium text-ds-fg-muted transition-colors hover:bg-ds-surface-3 hover:text-ds-fg focus-visible:shadow-ds-focus"
      >
        <MessageCircle className={iconClass} aria-hidden />
        <span>{language === 'zh' ? '评论' : 'Comment'}</span>
      </button>
    </div>
  );
};

export default MomentEngagementControls;
