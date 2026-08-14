// src/components/ds/Skeleton.tsx
//
// Design-system Skeleton — shimmer placeholders for loading content. The
// `ds-skeleton` class (design-system.css) supplies the shimmer; the component
// only adds radius and lets callers size it. `ArticleSkeleton` is a composed
// placeholder for the editor's article loading state.
import React from 'react';
import { cn } from '../../lib/utils';
import { dsRoot } from './dsAttr';

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

export const Skeleton: React.FC<SkeletonProps> = ({ className, ...props }) => (
  <div
    {...dsRoot}
    aria-hidden
    className={cn('ds-skeleton rounded-ds-sm', className)}
    {...props}
  />
);

/* --- ArticleSkeleton — composed editor loading state ---------------------- */

export const ArticleSkeleton: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  ...props
}) => (
  <div {...dsRoot} className={cn('space-y-3', className)} aria-hidden {...props}>
    {/* Title bar */}
    <Skeleton className="h-6 w-2/3" />
    {/* Body lines */}
    <Skeleton className="h-3.5 w-full" />
    <Skeleton className="h-3.5 w-11/12" />
    <Skeleton className="h-3.5 w-4/5" />
  </div>
);
ArticleSkeleton.displayName = 'ArticleSkeleton';
