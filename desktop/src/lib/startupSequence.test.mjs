import assert from 'node:assert/strict';
import test from 'node:test';
import {
  STARTUP_ARRIVAL_DURATION_MS,
  STARTUP_REVEAL_AT_MS,
  STARTUP_SETTLE_DURATION_MS,
  STARTUP_TOTAL_DURATION_MS,
  startupSequenceStageAt,
} from './startupSequence.ts';

test('the startup separates the avatar arrival from interface settlement and explanation', () => {
  assert.equal(startupSequenceStageAt(0), 'arrival');
  assert.equal(startupSequenceStageAt(STARTUP_ARRIVAL_DURATION_MS), 'settle');
  assert.equal(
    startupSequenceStageAt(STARTUP_ARRIVAL_DURATION_MS + STARTUP_SETTLE_DURATION_MS),
    'explain',
  );
  assert.equal(startupSequenceStageAt(STARTUP_REVEAL_AT_MS), 'reveal');
  assert.equal(startupSequenceStageAt(STARTUP_TOTAL_DURATION_MS), 'complete');
});

test('negative elapsed time remains at the beginning of the arrival', () => {
  assert.equal(startupSequenceStageAt(-100), 'arrival');
});
