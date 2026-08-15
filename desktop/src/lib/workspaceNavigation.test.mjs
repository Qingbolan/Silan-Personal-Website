import assert from 'node:assert/strict';
import test from 'node:test';
import {
  canMoveWorkspaceNavigationHistory,
  createWorkspaceNavigationHistory,
  moveWorkspaceNavigationHistory,
  recordWorkspaceLocation,
  workspaceLocationFrom,
} from './workspaceNavigation.ts';

const snapshot = (overrides = {}) => ({
  screen: 'dashboard',
  entityFilter: 'all',
  selectedDocumentId: '',
  selectedSeriesId: '',
  editorOpen: false,
  railMode: 'files',
  railPanel: 'parts',
  ...overrides,
});

test('workspace locations retain only state that identifies the visible surface', () => {
  assert.deepEqual(workspaceLocationFrom(snapshot({
    selectedDocumentId: 'ignored-on-dashboard',
  })), { kind: 'dashboard' });
  assert.deepEqual(workspaceLocationFrom(snapshot({
    screen: 'content',
    entityFilter: 'moment',
    selectedDocumentId: 'moment:field-note:body',
  })), { kind: 'shelf', entityFilter: 'moment' });
  assert.deepEqual(workspaceLocationFrom(snapshot({
    screen: 'content',
    entityFilter: 'blog',
    selectedDocumentId: 'episode:one:body',
    selectedSeriesId: 'series:field-notes',
    editorOpen: true,
  })), {
    kind: 'editor',
    entityFilter: 'blog',
    documentId: 'episode:one:body',
    seriesId: 'series:field-notes',
    railMode: 'files',
    railPanel: 'parts',
  });
});

test('history moves backward and forward through distinct workspace surfaces', () => {
  let history = createWorkspaceNavigationHistory({ kind: 'dashboard' });
  history = recordWorkspaceLocation(history, { kind: 'shelf', entityFilter: 'moment' });
  history = recordWorkspaceLocation(history, { kind: 'shelf', entityFilter: 'blog' });

  assert.equal(canMoveWorkspaceNavigationHistory(history, -1), true);
  assert.equal(canMoveWorkspaceNavigationHistory(history, 1), false);

  history = moveWorkspaceNavigationHistory(history, -1);
  assert.deepEqual(history.entries[history.index], { kind: 'shelf', entityFilter: 'moment' });
  assert.equal(canMoveWorkspaceNavigationHistory(history, 1), true);

  history = moveWorkspaceNavigationHistory(history, 1);
  assert.deepEqual(history.entries[history.index], { kind: 'shelf', entityFilter: 'blog' });
});

test('a new visit after going back replaces the obsolete forward branch', () => {
  let history = createWorkspaceNavigationHistory({ kind: 'dashboard' });
  history = recordWorkspaceLocation(history, { kind: 'shelf', entityFilter: 'moment' });
  history = recordWorkspaceLocation(history, { kind: 'shelf', entityFilter: 'blog' });
  history = moveWorkspaceNavigationHistory(history, -1);
  history = recordWorkspaceLocation(history, { kind: 'shelf', entityFilter: 'project' });

  assert.deepEqual(history.entries, [
    { kind: 'dashboard' },
    { kind: 'shelf', entityFilter: 'moment' },
    { kind: 'shelf', entityFilter: 'project' },
  ]);
  assert.equal(canMoveWorkspaceNavigationHistory(history, 1), false);
});

test('recording the current location does not create duplicate history entries', () => {
  const initial = createWorkspaceNavigationHistory({ kind: 'dashboard' });
  const next = recordWorkspaceLocation(initial, { kind: 'dashboard' });
  assert.equal(next, initial);
});
