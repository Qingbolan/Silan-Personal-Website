import type { ContentKind, EntityFilter, VersionScope } from '../../types';

export const masonryContentKinds = new Set<ContentKind>(['blog', 'project']);

export const editableMasonryContentKinds = new Set<ContentKind>([
  'blog',
  'project',
  'episode',
  'resume',
  'moment',
]);

export const stateManagedKinds = new Set<ContentKind>([
  'blog',
  'project',
  'episode',
  'moment',
]);

export const archivableKinds = new Set<ContentKind>([
  'blog',
  'project',
  'episode',
]);

export const navigationEntityFilters: EntityFilter[] = [
  'resume',
  'moment',
  'blog',
  'project',
];

const versionScopeFilters = new Set<EntityFilter>([
  'resume',
  'blog',
  'project',
  'moment',
]);

const contentKinds = new Set<ContentKind>([
  'blog',
  'project',
  'idea',
  'resume',
  'episode',
  'moment',
]);

export const isVersionScope = (filter: EntityFilter): filter is VersionScope => (
  versionScopeFilters.has(filter)
);

export const isContentKind = (value: string): value is ContentKind => (
  contentKinds.has(value as ContentKind)
);
