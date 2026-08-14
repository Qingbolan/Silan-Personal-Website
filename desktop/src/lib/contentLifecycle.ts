import type { ContentKind } from '../types';

export type DocumentStateInput = {
  status: string;
  visibility: string;
  pinned?: boolean;
};

export type LifecycleActionId =
  | 'publish'
  | 'unpublish'
  | 'archive'
  | 'restore'
  | 'activate'
  | 'pause'
  | 'complete'
  | 'cancel'
  | 'hypothesis'
  | 'experiment'
  | 'validate'
  | 'conclude'
  | 'start'
  | 'reset'
  | 'make-private'
  | 'make-unlisted'
  | 'make-public';

export type LifecycleActionGroup = 'status' | 'visibility';

export type LifecycleAction = {
  id: LifecycleActionId;
  group: LifecycleActionGroup;
  label: string;
  description: string;
  tone: 'primary' | 'secondary' | 'danger';
  nextState: DocumentStateInput;
};

export type LifecycleView = {
  status: string;
  visibility: string;
  statusLabel: string;
  visibilityLabel: string;
  actions: LifecycleAction[];
};

export type SeriesLifecycleActionId = 'publish-all' | 'unpublish-all' | 'archive-all';

export type SeriesLifecycleAction = {
  id: SeriesLifecycleActionId;
  label: string;
  description: string;
  tone: 'primary' | 'secondary' | 'danger';
  nextState: DocumentStateInput;
};

export type SeriesLifecycleView = {
  status: 'published' | 'draft' | 'archived' | 'mixed';
  visibility: 'public' | 'private' | 'mixed';
  statusLabel: string;
  visibilityLabel: string;
  actions: SeriesLifecycleAction[];
};

const titleCase = (value: string) => (
  value
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((part) => part[0]?.toUpperCase() + part.slice(1))
    .join(' ')
);

const normalize = (value: string | null | undefined, fallback: string) => (
  value?.trim().toLowerCase() || fallback
);

/**
 * One content-kind state machine. Status and visibility stay orthogonal in
 * the model; coordinated actions such as Publish may still update both when
 * that is the product-level operation the author explicitly requested.
 */
abstract class ContentLifecyclePolicy {
  protected readonly status: string;

  protected readonly visibility: string;

  constructor(
    status: string,
    visibility: string,
  ) {
    this.status = status;
    this.visibility = visibility;
  }

  view(): LifecycleView {
    const statusActions = this.statusActions();
    const visibilityActions = this.canChangeVisibility()
      ? this.visibilityActions()
      : [];
    return {
      status: this.status,
      visibility: this.visibility,
      statusLabel: titleCase(this.status),
      visibilityLabel: titleCase(this.visibility),
      actions: [...statusActions, ...visibilityActions],
    };
  }

  protected abstract statusActions(): LifecycleAction[];

  protected canChangeVisibility() {
    return true;
  }

  protected statusAction(
    action: Omit<LifecycleAction, 'group'>,
  ): LifecycleAction {
    return { ...action, group: 'status' };
  }

  private visibilityActions(): LifecycleAction[] {
    const definitions: Array<{
      visibility: 'private' | 'unlisted' | 'public';
      id: 'make-private' | 'make-unlisted' | 'make-public';
      label: string;
      description: string;
      tone: LifecycleAction['tone'];
    }> = [
      {
        visibility: 'private',
        id: 'make-private',
        label: 'Private',
        description: 'Keep this content only in the local workspace.',
        tone: 'secondary',
      },
      {
        visibility: 'unlisted',
        id: 'make-unlisted',
        label: 'Unlisted',
        description: 'Allow direct access without listing this content on public discovery surfaces.',
        tone: 'secondary',
      },
      {
        visibility: 'public',
        id: 'make-public',
        label: 'Public',
        description: 'Make this content available to public website surfaces after the next deploy.',
        tone: 'primary',
      },
    ];
    return definitions
      .filter((definition) => definition.visibility !== this.visibility)
      .map((definition) => ({
        id: definition.id,
        group: 'visibility' as const,
        label: definition.label,
        description: definition.description,
        tone: definition.tone,
        nextState: { status: this.status, visibility: definition.visibility },
      }));
  }
}

class ProseLifecyclePolicy extends ContentLifecyclePolicy {
  protected canChangeVisibility() {
    return this.status !== 'archived';
  }

  protected statusActions(): LifecycleAction[] {
    if (this.status === 'archived') {
      return [
        this.statusAction({
          id: 'restore',
          label: 'Restore draft',
          description: 'Move this content back to draft without making it public.',
          tone: 'secondary',
          nextState: { status: 'draft', visibility: 'private' },
        }),
        this.statusAction({
          id: 'publish',
          label: 'Publish',
          description: 'Publish this content and make it public.',
          tone: 'primary',
          nextState: { status: 'published', visibility: 'public' },
        }),
      ];
    }
    if (this.status === 'published') {
      return [
        this.statusAction({
          id: 'unpublish',
          label: 'Unpublish',
          description: 'Take this content offline and return it to a private draft.',
          tone: 'secondary',
          nextState: { status: 'draft', visibility: 'private' },
        }),
        this.statusAction({
          id: 'archive',
          label: 'Archive',
          description: 'Remove this content from publication while keeping the record.',
          tone: 'secondary',
          nextState: { status: 'archived', visibility: 'private' },
        }),
      ];
    }
    return [
      this.statusAction({
        id: 'publish',
        label: 'Publish',
        description: 'Publish this content and make it public.',
        tone: 'primary',
        nextState: { status: 'published', visibility: 'public' },
      }),
      this.statusAction({
        id: 'archive',
        label: 'Archive',
        description: 'Archive this draft without publishing it.',
        tone: 'secondary',
        nextState: { status: 'archived', visibility: 'private' },
      }),
    ];
  }
}

class ProjectLifecyclePolicy extends ContentLifecyclePolicy {
  protected canChangeVisibility() {
    return this.status !== 'cancelled' && this.status !== 'archived';
  }

  protected statusActions(): LifecycleAction[] {
    const keepVisibility = this.visibility || 'private';
    if (this.status === 'archived') {
      return [this.statusAction({
        id: 'restore',
        label: 'Restore project',
        description: 'Return this project to active work without making it public.',
        tone: 'secondary',
        nextState: { status: 'active', visibility: 'private' },
      })];
    }
    if (this.status === 'paused') {
      return [
        this.statusAction({
          id: 'activate',
          label: 'Resume',
          description: 'Resume active work on this project.',
          tone: 'primary',
          nextState: { status: 'active', visibility: keepVisibility },
        }),
        this.statusAction({
          id: 'cancel',
          label: 'Cancel',
          description: 'Stop this project and remove it from public surfaces.',
          tone: 'danger',
          nextState: { status: 'cancelled', visibility: 'private' },
        }),
        this.archiveAction(),
      ];
    }
    if (this.status === 'completed') {
      return [
        this.statusAction({
          id: 'activate',
          label: 'Reopen',
          description: 'Move this completed project back to active work.',
          tone: 'secondary',
          nextState: { status: 'active', visibility: keepVisibility },
        }),
        this.archiveAction(),
      ];
    }
    if (this.status === 'cancelled') {
      return [
        this.statusAction({
          id: 'activate',
          label: 'Reopen',
          description: 'Restart this cancelled project privately.',
          tone: 'secondary',
          nextState: { status: 'active', visibility: 'private' },
        }),
        this.archiveAction(),
      ];
    }
    return [
      this.statusAction({
        id: 'pause',
        label: 'Pause',
        description: 'Pause active work without removing project history.',
        tone: 'secondary',
        nextState: { status: 'paused', visibility: keepVisibility },
      }),
      this.statusAction({
        id: 'complete',
        label: 'Complete',
        description: 'Mark this project as completed.',
        tone: 'primary',
        nextState: { status: 'completed', visibility: keepVisibility },
      }),
      this.statusAction({
        id: 'cancel',
        label: 'Cancel',
        description: 'Stop this project and remove it from public surfaces.',
        tone: 'danger',
        nextState: { status: 'cancelled', visibility: 'private' },
      }),
      this.archiveAction(),
    ];
  }

  private archiveAction(): LifecycleAction {
    return this.statusAction({
      id: 'archive',
      label: 'Archive',
      description: 'Remove this project from project surfaces while keeping its files and history.',
      tone: 'secondary',
      nextState: { status: 'archived', visibility: 'private' },
    });
  }
}

class MomentLifecyclePolicy extends ContentLifecyclePolicy {
  protected statusActions(): LifecycleAction[] {
    if (this.status === 'completed') {
      return [this.statusAction({
        id: 'activate',
        label: 'Reopen',
        description: 'Return this completed moment to ongoing work.',
        tone: 'secondary',
        nextState: { status: 'ongoing', visibility: this.visibility },
      })];
    }
    if (this.status === 'ongoing') {
      return [
        this.statusAction({
          id: 'reset',
          label: 'Reset to active',
          description: 'Return this moment to its active starting state.',
          tone: 'secondary',
          nextState: { status: 'active', visibility: this.visibility },
        }),
        this.statusAction({
          id: 'complete',
          label: 'Complete',
          description: 'Mark this moment lifecycle as completed.',
          tone: 'primary',
          nextState: { status: 'completed', visibility: this.visibility },
        }),
      ];
    }
    return [
      this.statusAction({
        id: 'start',
        label: 'Start progress',
        description: 'Advance this moment from active to ongoing.',
        tone: 'primary',
        nextState: { status: 'ongoing', visibility: this.visibility },
      }),
      this.statusAction({
        id: 'complete',
        label: 'Complete',
        description: 'Mark this moment lifecycle as completed.',
        tone: 'secondary',
        nextState: { status: 'completed', visibility: this.visibility },
      }),
    ];
  }
}

export const contentLifecycleFor = (
  kind: ContentKind,
  rawStatus: string | null | undefined,
  rawVisibility: string | null | undefined,
): LifecycleView => {
  const visibility = normalize(rawVisibility, 'private');

  if (kind === 'blog' || kind === 'episode') {
    return new ProseLifecyclePolicy(normalize(rawStatus, 'draft'), visibility).view();
  }
  if (kind === 'project') {
    return new ProjectLifecyclePolicy(normalize(rawStatus, 'active'), visibility).view();
  }
  if (kind === 'moment') {
    return new MomentLifecyclePolicy(normalize(rawStatus, 'active'), visibility).view();
  }
  return {
    status: normalize(rawStatus, 'draft'),
    visibility,
    statusLabel: titleCase(normalize(rawStatus, 'draft')),
    visibilityLabel: titleCase(visibility),
    actions: [],
  };
};

export const contentStateSummary = (
  kind: ContentKind,
  status: string | null | undefined,
  visibility: string | null | undefined,
) => {
  const lifecycle = contentLifecycleFor(kind, status, visibility);
  return `${lifecycle.statusLabel} · ${lifecycle.visibilityLabel}`;
};

export const hasDocumentStateChanges = (
  kind: ContentKind,
  draft: DocumentStateInput,
  current: DocumentStateInput,
) => (
  draft.status !== current.status
  || draft.visibility !== current.visibility
  || (kind === 'moment' && Boolean(draft.pinned) !== Boolean(current.pinned))
);

export const seriesLifecycleFor = (
  episodes: Array<{ status: string | null | undefined; visibility: string | null | undefined }>,
): SeriesLifecycleView => {
  const normalized = episodes.map((episode) => ({
    status: normalize(episode.status, 'draft'),
    visibility: normalize(episode.visibility, 'private'),
  }));
  const statusSet = new Set(normalized.map((episode) => episode.status));
  const visibilitySet = new Set(normalized.map((episode) => episode.visibility));
  const status = statusSet.size === 1
    ? normalized[0]?.status === 'published'
      ? 'published'
      : normalized[0]?.status === 'archived'
        ? 'archived'
        : 'draft'
    : 'mixed';
  const visibility = visibilitySet.size === 1
    ? normalized[0]?.visibility === 'public' ? 'public' : 'private'
    : 'mixed';
  const allPublicPublished = normalized.length > 0
    && normalized.every((episode) => episode.status === 'published' && episode.visibility === 'public');
  const allArchived = normalized.length > 0
    && normalized.every((episode) => episode.status === 'archived');
  const actions: SeriesLifecycleAction[] = allPublicPublished
    ? [
        {
          id: 'unpublish-all',
          label: 'Unpublish all',
          description: 'Take every episode in this series offline and return them to draft.',
          tone: 'secondary',
          nextState: { status: 'draft', visibility: 'private' },
        },
        {
          id: 'archive-all',
          label: 'Archive all',
          description: 'Archive every episode in this series.',
          tone: 'secondary',
          nextState: { status: 'archived', visibility: 'private' },
        },
      ]
    : [
        {
          id: 'publish-all',
          label: allArchived ? 'Publish all' : 'Publish all',
          description: 'Publish every episode in this series and make them public.',
          tone: 'primary',
          nextState: { status: 'published', visibility: 'public' },
        },
        {
          id: 'archive-all',
          label: 'Archive all',
          description: 'Archive every episode in this series.',
          tone: 'secondary',
          nextState: { status: 'archived', visibility: 'private' },
        },
      ];

  return {
    status,
    visibility,
    statusLabel: status === 'mixed' ? 'Mixed' : titleCase(status),
    visibilityLabel: visibility === 'mixed' ? 'Mixed visibility' : titleCase(visibility),
    actions,
  };
};
