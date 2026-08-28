import React from 'react';
import { cn } from '../../lib/utils';
import { Avatar } from './Avatar';

export interface CardAuthorProps {
  name: string;
  avatarUrl?: string;
  onCover?: boolean;
  className?: string;
}

/** Shared author identity used on editorial and project card covers. */
export const CardAuthor: React.FC<CardAuthorProps> = ({
  name,
  avatarUrl,
  onCover = false,
  className,
}) => (
  <span className={cn('inline-flex items-center gap-1.5', className)}>
    <Avatar
      src={avatarUrl}
      name={name}
      size="xs"
      bordered={false}
      className={cn(
        'size-4 text-[0.5rem]',
        onCover && 'ring-1 ring-white/40',
      )}
    />
    {name}
  </span>
);
