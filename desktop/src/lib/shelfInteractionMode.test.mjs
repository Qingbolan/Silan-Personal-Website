import assert from 'node:assert/strict';
import test from 'node:test';
import {
  initialShelfInteractionMode,
  managementControlsVisible,
  transitionShelfInteractionMode,
} from './shelfInteractionMode.ts';

test('shelves open in browse mode with management controls hidden', () => {
  assert.equal(initialShelfInteractionMode, 'browse');
  assert.equal(managementControlsVisible(initialShelfInteractionMode), false);
});

test('the toggle moves between browse and manage modes', () => {
  const managing = transitionShelfInteractionMode(initialShelfInteractionMode, { type: 'toggle' });
  assert.equal(managing, 'manage');
  assert.equal(managementControlsVisible(managing), true);
  assert.equal(transitionShelfInteractionMode(managing, { type: 'toggle' }), 'browse');
});

test('explicit mode events are idempotent', () => {
  assert.equal(transitionShelfInteractionMode('manage', { type: 'manage' }), 'manage');
  assert.equal(transitionShelfInteractionMode('browse', { type: 'browse' }), 'browse');
});
