import type { ContentRailMode, ContentRailPanel } from '../app/settings/contentSettings';
import type { EntityFilter } from '../types';

export type WorkspaceNavigationSnapshot = {
  screen: 'dashboard' | 'content' | 'settings';
  entityFilter: EntityFilter;
  selectedDocumentId: string;
  selectedSeriesId: string;
  editorOpen: boolean;
  railMode: ContentRailMode;
  railPanel: ContentRailPanel;
};

export type WorkspaceLocation =
  | { kind: 'dashboard' }
  | { kind: 'settings' }
  | { kind: 'shelf'; entityFilter: EntityFilter }
  | { kind: 'series'; entityFilter: EntityFilter; seriesId: string }
  | {
      kind: 'editor';
      entityFilter: EntityFilter;
      documentId: string;
      seriesId: string;
      railMode: ContentRailMode;
      railPanel: ContentRailPanel;
    };

export type WorkspaceNavigationHistory = {
  entries: WorkspaceLocation[];
  index: number;
};

export type WorkspaceTab = {
  id: string;
  history: WorkspaceNavigationHistory;
};

export type WorkspaceTabsState = {
  tabs: WorkspaceTab[];
  activeTabId: string;
  nextTabNumber: number;
};

const historyLimit = 100;

export const workspaceLocationFrom = (
  snapshot: WorkspaceNavigationSnapshot,
): WorkspaceLocation => {
  if (snapshot.screen === 'dashboard') return { kind: 'dashboard' };
  if (snapshot.screen === 'settings') return { kind: 'settings' };
  if (snapshot.editorOpen && snapshot.selectedDocumentId) {
    return {
      kind: 'editor',
      entityFilter: snapshot.entityFilter,
      documentId: snapshot.selectedDocumentId,
      seriesId: snapshot.selectedSeriesId,
      railMode: snapshot.railMode,
      railPanel: snapshot.railPanel,
    };
  }
  if (snapshot.selectedSeriesId) {
    return {
      kind: 'series',
      entityFilter: snapshot.entityFilter,
      seriesId: snapshot.selectedSeriesId,
    };
  }
  return { kind: 'shelf', entityFilter: snapshot.entityFilter };
};

export const workspaceLocationKey = (location: WorkspaceLocation) => {
  switch (location.kind) {
    case 'dashboard':
    case 'settings':
      return location.kind;
    case 'shelf':
      return `shelf:${location.entityFilter}`;
    case 'series':
      return `series:${location.entityFilter}:${location.seriesId}`;
    case 'editor':
      return [
        'editor',
        location.entityFilter,
        location.documentId,
        location.seriesId,
        location.railMode,
        location.railPanel,
      ].join(':');
  }
};

export const createWorkspaceNavigationHistory = (
  initialLocation: WorkspaceLocation,
): WorkspaceNavigationHistory => ({
  entries: [initialLocation],
  index: 0,
});

export const recordWorkspaceLocation = (
  history: WorkspaceNavigationHistory,
  location: WorkspaceLocation,
): WorkspaceNavigationHistory => {
  const current = history.entries[history.index];
  if (current && workspaceLocationKey(current) === workspaceLocationKey(location)) {
    return history;
  }

  const entries = [...history.entries.slice(0, history.index + 1), location]
    .slice(-historyLimit);
  return {
    entries,
    index: entries.length - 1,
  };
};

export const moveWorkspaceNavigationHistory = (
  history: WorkspaceNavigationHistory,
  direction: -1 | 1,
): WorkspaceNavigationHistory => {
  const index = Math.min(
    history.entries.length - 1,
    Math.max(0, history.index + direction),
  );
  return index === history.index ? history : { ...history, index };
};

export const canMoveWorkspaceNavigationHistory = (
  history: WorkspaceNavigationHistory,
  direction: -1 | 1,
) => direction === -1
  ? history.index > 0
  : history.index < history.entries.length - 1;

export const currentWorkspaceLocation = (
  history: WorkspaceNavigationHistory,
) => history.entries[history.index] || history.entries[0];

export const createWorkspaceTabs = (
  initialLocation: WorkspaceLocation,
): WorkspaceTabsState => ({
  tabs: [{
    id: 'workspace-tab-1',
    history: createWorkspaceNavigationHistory(initialLocation),
  }],
  activeTabId: 'workspace-tab-1',
  nextTabNumber: 2,
});

export const activeWorkspaceTab = (
  state: WorkspaceTabsState,
) => state.tabs.find((tab) => tab.id === state.activeTabId) || state.tabs[0];

export const activeWorkspaceLocation = (
  state: WorkspaceTabsState,
) => {
  const tab = activeWorkspaceTab(state);
  return tab ? currentWorkspaceLocation(tab.history) : undefined;
};

export const recordActiveWorkspaceLocation = (
  state: WorkspaceTabsState,
  location: WorkspaceLocation,
): WorkspaceTabsState => {
  let changed = false;
  const tabs = state.tabs.map((tab) => {
    if (tab.id !== state.activeTabId) return tab;
    const history = recordWorkspaceLocation(tab.history, location);
    if (history === tab.history) return tab;
    changed = true;
    return { ...tab, history };
  });
  return changed ? { ...state, tabs } : state;
};

export const addWorkspaceTab = (
  state: WorkspaceTabsState,
  initialLocation: WorkspaceLocation = { kind: 'dashboard' },
): WorkspaceTabsState => {
  const id = `workspace-tab-${state.nextTabNumber}`;
  return {
    tabs: [...state.tabs, {
      id,
      history: createWorkspaceNavigationHistory(initialLocation),
    }],
    activeTabId: id,
    nextTabNumber: state.nextTabNumber + 1,
  };
};

export const activateWorkspaceTab = (
  state: WorkspaceTabsState,
  tabId: string,
): WorkspaceTabsState => state.activeTabId === tabId
  || !state.tabs.some((tab) => tab.id === tabId)
  ? state
  : { ...state, activeTabId: tabId };

export const closeWorkspaceTab = (
  state: WorkspaceTabsState,
  tabId: string,
): WorkspaceTabsState => {
  if (state.tabs.length === 1) return state;
  const closingIndex = state.tabs.findIndex((tab) => tab.id === tabId);
  if (closingIndex < 0) return state;

  const tabs = state.tabs.filter((tab) => tab.id !== tabId);
  if (state.activeTabId !== tabId) return { ...state, tabs };

  return {
    ...state,
    tabs,
    activeTabId: tabs[Math.min(closingIndex, tabs.length - 1)].id,
  };
};

export const moveActiveWorkspaceTabHistory = (
  state: WorkspaceTabsState,
  direction: -1 | 1,
): WorkspaceTabsState => {
  let changed = false;
  const tabs = state.tabs.map((tab) => {
    if (tab.id !== state.activeTabId) return tab;
    const history = moveWorkspaceNavigationHistory(tab.history, direction);
    if (history === tab.history) return tab;
    changed = true;
    return { ...tab, history };
  });
  return changed ? { ...state, tabs } : state;
};

export const canMoveActiveWorkspaceTabHistory = (
  state: WorkspaceTabsState,
  direction: -1 | 1,
) => {
  const tab = activeWorkspaceTab(state);
  return tab ? canMoveWorkspaceNavigationHistory(tab.history, direction) : false;
};
