import assert from 'node:assert/strict';
import test from 'node:test';
import { deploymentReadinessFor } from './deploymentReadiness.ts';

const readiness = (overrides = {}) => deploymentReadinessFor({
  localCommitCount: 2,
  remoteCommitCount: 0,
  workspaceChangeCount: 0,
  unsavedDocumentCount: 0,
  planState: 'ready',
  planError: null,
  deploying: false,
  ...overrides,
});

test('committed content with a loaded plan is ready to deploy', () => {
  assert.deepEqual(readiness(), {
    state: 'ready',
    canDeploy: true,
    message: '2 committed moments ready to deploy',
    actionTitle: 'Deploy committed content to the production website',
  });
});

test('unsaved editor state stays local without blocking the committed snapshot', () => {
  const result = readiness({ unsavedDocumentCount: 1 });
  assert.equal(result.state, 'ready_with_unsaved');
  assert.equal(result.canDeploy, true);
  assert.equal(result.message, '2 committed moments ready; 1 unsaved Markdown file will stay local');
});

test('uncommitted workspace changes explain the commit prerequisite', () => {
  const result = readiness({ workspaceChangeCount: 3 });
  assert.equal(result.state, 'blocked_uncommitted');
  assert.equal(result.canDeploy, false);
  assert.equal(result.message, '3 uncommitted changes must be committed first');
});

test('a deployment-plan failure is visible and retryable', () => {
  const result = readiness({
    planState: 'error',
    planError: 'Error: content schema could not be scanned',
  });
  assert.equal(result.state, 'check_failed');
  assert.equal(result.canDeploy, false);
  assert.equal(result.message, 'Deployment check failed: content schema could not be scanned');
});

test('version comparison and synchronized states do not expose deploy', () => {
  assert.equal(readiness({ localCommitCount: null }).state, 'comparing');
  assert.equal(readiness({ localCommitCount: 0 }).state, 'synchronized');
  assert.equal(readiness({ localCommitCount: 0 }).canDeploy, false);
});
