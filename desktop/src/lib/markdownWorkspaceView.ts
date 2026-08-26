export const markdownWorkspaceViews = ['edit', 'split', 'preview'] as const;

export type MarkdownWorkspaceView = (typeof markdownWorkspaceViews)[number];

const markdownWorkspaceViewTransitions: Record<MarkdownWorkspaceView, MarkdownWorkspaceView> = {
  edit: 'split',
  split: 'preview',
  preview: 'edit',
};

export const parseMarkdownWorkspaceView = (value: string | null): MarkdownWorkspaceView => (
  markdownWorkspaceViews.includes(value as MarkdownWorkspaceView)
    ? value as MarkdownWorkspaceView
    : 'edit'
);

export const nextMarkdownWorkspaceView = (
  view: MarkdownWorkspaceView,
): MarkdownWorkspaceView => markdownWorkspaceViewTransitions[view];
