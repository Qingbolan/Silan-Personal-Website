import assert from 'node:assert/strict';
import test from 'node:test';
import { summarizeMarkdownBlockChanges } from './markdownBlockDiff.ts';

test('Markdown block diff distinguishes changed, added, and preserved blocks', () => {
  const summary = summarizeMarkdownBlockChanges(
    '# Title\n\nKeep me.\n\nOld sentence.',
    '# Title\n\nKeep me.\n\nNew sentence.\n\nOne more.',
  );
  assert.deepEqual(summary, {
    before: 3,
    after: 4,
    changed: 1,
    added: 1,
    removed: 0,
    affected: 2,
  });
});
