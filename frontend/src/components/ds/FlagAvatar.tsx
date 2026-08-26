import React from 'react';
import { cn } from '../../lib/utils';
import { dsRoot } from './dsAttr';

interface FlagAvatarProps {
  countryCode: string;
  label: string;
  visitorNumber?: string;
  className?: string;
  onError?: () => void;
}

// Shared flag identity treatment used by comments, liker grids and profiles.
// The DS root opts the border out of the legacy global border reset, so the
// same rounded hairline is preserved in every host surface.
const FlagAvatar: React.FC<FlagAvatarProps> = ({
  countryCode,
  label,
  visitorNumber,
  className,
  onError,
}) => (
  <span
    {...dsRoot}
    className={cn(
      'ds-hairline relative inline-flex shrink-0 overflow-visible rounded-[7px] bg-ds-surface-1 shadow-sm',
      className,
    )}
    title={label}
    aria-label={label}
  >
    <img
      src={`https://flagcdn.com/w80/${countryCode.toLowerCase()}.png`}
      alt=""
      className="h-full w-full rounded-[6px] object-contain p-[2px]"
      loading="lazy"
      decoding="async"
      onError={onError}
    />
    {visitorNumber && (
      <span className="absolute bottom-[-1px] right-[-1px] flex min-w-[16px] items-center justify-center rounded-[5px] border border-white/90 bg-ds-fg px-0.5 font-mono text-[10px] font-semibold leading-[12px] tabular-nums text-ds-surface-1 shadow-sm">
        {visitorNumber}
      </span>
    )}
  </span>
);

export default FlagAvatar;
