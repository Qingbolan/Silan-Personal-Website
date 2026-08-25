import React from 'react';
import { cn } from '../../lib/utils';
import { dsRoot } from '../ds/dsAttr';
import { EDITORIAL_CONTENT_FRAME_CLASS } from '../../layout/contentFrame';

interface MomentsProfileHeroProps {
  name: string;
  role?: string;
  avatarUrl: string;
  coverUrl: string;
  coverAlt: string;
  className?: string;
}

/**
 * Public identity header for the Moments feed.
 *
 * Desktop and Web intentionally share the same cover/profile mental model,
 * while the public site keeps its own navigation and responsive proportions.
 */
const MomentsProfileHero: React.FC<MomentsProfileHeroProps> = ({
  name,
  role,
  avatarUrl,
  coverUrl,
  coverAlt,
  className,
}) => (
  <header
    {...dsRoot}
    className={cn(
      'relative mb-16 sm:mb-20 lg:-mx-8 lg:w-[calc(100%_+_4rem)]',
      className,
    )}
  >
    <div className="relative min-h-[13rem] overflow-hidden bg-ds-surface-3 sm:min-h-[clamp(18rem,18vw,24rem)]">
      <img
        src={coverUrl}
        alt={coverAlt}
        className="absolute inset-0 size-full object-cover object-[center_42%]"
      />
      <div
        aria-hidden
        className="absolute inset-0 bg-[linear-gradient(180deg,rgba(7,13,18,0.16)_0%,rgba(7,13,18,0.08)_34%,rgba(7,13,18,0.76)_100%)]"
      />
    </div>

    <div className="absolute -bottom-16 inset-x-0 2xl:-bottom-20">
      <div className={cn(EDITORIAL_CONTENT_FRAME_CLASS, 'flex justify-end')}>
        <div className="flex max-w-full items-start gap-3 sm:gap-4 2xl:gap-5">
          <div className="min-w-0 pt-5 text-right">
            <strong className="block truncate text-xl font-semibold tracking-[-0.025em] text-white drop-shadow-[0_1px_12px_rgba(0,0,0,0.55)] sm:text-2xl 2xl:text-3xl">
              {name}
            </strong>
            {role && (
              <span className="mt-1 block line-clamp-2 max-w-64 text-xs leading-5 text-ds-fg-muted sm:text-sm 2xl:max-w-80 2xl:text-base 2xl:leading-6">
                {role}
              </span>
            )}
          </div>
          <img
            src={avatarUrl}
            alt={`${name} portrait`}
            className="size-24 shrink-0 rounded-full border-4 border-ds-canvas bg-ds-surface-3 object-cover shadow-ds-2 sm:size-28 2xl:size-32"
          />
        </div>
      </div>
    </div>
  </header>
);

export default MomentsProfileHero;
