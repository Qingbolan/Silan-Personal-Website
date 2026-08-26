import assert from 'node:assert/strict';
import test from 'node:test';
import {
  nextMarkdownWorkspaceView,
  parseMarkdownWorkspaceView,
} from './markdownWorkspaceView.ts';

test('workspace view cycles through edit, split, preview, and back to edit', () => {
  assert.equal(nextMarkdownWorkspaceView('edit'), 'split');
  assert.equal(nextMarkdownWorkspaceView('split'), 'preview');
  assert.equal(nextMarkdownWorkspaceView('preview'), 'edit');
});

test('workspace view restores known values and rejects obsolete values', () => {
  assert.equal(parseMarkdownWorkspaceView('split'), 'split');
  assert.equal(parseMarkdownWorkspaceView('preview'), 'preview');
  assert.equal(parseMarkdownWorkspaceView('unknown'), 'edit');
  assert.equal(parseMarkdownWorkspaceView(null), 'edit');
});
