import assert from 'node:assert/strict';
import test from 'node:test';
import {
  initialTranslationSyncState,
  translationSyncTransition,
} from './translationSyncWorkflow.ts';

const sourceChanges = {
  before: 3,
  after: 4,
  changed: 1,
  added: 1,
  removed: 0,
  affected: 2,
};

test('translation sync exposes saving, syncing, and completion phases', () => {
  const saving = translationSyncTransition(initialTranslationSyncState, {
    type: 'started',
    key: 'body:en:zh',
    documentId: 'body',
    sourceLanguage: 'en',
    targetLanguage: 'zh',
    sourceChanges,
    saveRequired: true,
  });
  assert.equal(saving.phase, 'saving_source');

  const syncing = translationSyncTransition(saving, { type: 'sourceSaved' });
  assert.equal(syncing.phase, 'syncing');

  const complete = translationSyncTransition(syncing, {
    type: 'completed',
    targetChanges: { ...sourceChanges, affected: 1 },
  });
  assert.equal(complete.phase, 'complete');
  assert.equal(complete.targetChanges?.affected, 1);
});
