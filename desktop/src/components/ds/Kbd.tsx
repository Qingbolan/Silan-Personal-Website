// src/components/ds/Kbd.tsx
//
// Design-system Kbd — a keyboard-shortcut badge. Renders a key name or
// chord segment in mono on a filled surface chip; use inside hints and
// shortcut pickers.
import React from 'react';
import { cn } from '../../lib/utils';
import { dsRoot } from './dsAttr';

export interface KbdProps extends React.HTMLAttributes<HTMLElement> {}

export const Kbd: React.FC<KbdProps> = ({ className, ...props }) => (
  <kbd
    {...dsRoot}
    className={cn(
      'inline-flex items-center rounded-ds-xs border border-ds-border bg-ds-surface-2',
      'px-1.5 py-0.5 font-mono text-[10px] leading-none text-ds-fg-muted',
      className,
    )}
    {...props}
  />
);
Kbd.displayName = 'Kbd';
