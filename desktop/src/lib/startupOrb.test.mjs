import assert from 'node:assert/strict';
import test from 'node:test';
import { startupOrbEyePath, startupOrbFrameAt } from './startupOrb.ts';
import { STARTUP_LOADING_PHASE_DURATION_MS } from './startupSequence.ts';

test('the startup orb renders measured capsule eyes through a full spherical turn', () => {
  assert.match(startupOrbEyePath(), /^M/);
  assert.equal(startupOrbFrameAt(0).eyes.length, 2);
  assert.ok(startupOrbFrameAt(750).eyes.length < 2);
  assert.equal(startupOrbFrameAt(1_600).eyes.length, 2);
});

test('autonomous affect stays continuous across unrelated loading boundaries', () => {
  const boundary = STARTUP_LOADING_PHASE_DURATION_MS * 2;
  const before = startupOrbFrameAt(boundary - 2).eyes[0];
  const after = startupOrbFrameAt(boundary + 2).eyes[0];
  assert.ok(before && after);

  const values = (path) => [...path.matchAll(/-?\d+(?:\.\d+)?/g)].map(([value]) => Number(value));
  const beforeValues = values(before.path);
  const afterValues = values(after.path);
  assert.equal(beforeValues.length, afterValues.length);
  assert.ok(Math.max(...beforeValues.map((value, index) => Math.abs(value - afterValues[index]))) < 0.2);

  const freeEarlier = startupOrbFrameAt(boundary + 120).eyes[0];
  const freeLater = startupOrbFrameAt(boundary + 760).eyes[0];
  assert.ok(freeEarlier && freeLater);
  assert.notEqual(freeEarlier.path, freeLater.path);
});

test('pointer activity biases but does not replace the autonomous expression', () => {
  const free = startupOrbFrameAt(3_100, { nx: 0.7, ny: -0.4, activity: 0 });
  const attentive = startupOrbFrameAt(3_100, { nx: 0.7, ny: -0.4, activity: 1 });
  assert.ok(free.eyes[0] && attentive.eyes[0]);
  assert.notEqual(free.eyes[0].path, attentive.eyes[0].path);
});

test('pointer input is bounded and every sampled SVG transform remains finite', () => {
  for (let elapsed = 0; elapsed <= 5_000; elapsed += 50) {
    const frame = startupOrbFrameAt(elapsed, { nx: 12, ny: -9 });
    assert.doesNotMatch(frame.bodyTransform, /NaN|Infinity/);
    frame.eyes.forEach((eye) => {
      assert.doesNotMatch(eye.matrix, /NaN|Infinity/);
      assert.doesNotMatch(eye.path, /NaN|Infinity/);
      assert.ok(eye.opacity >= 0 && eye.opacity <= 1);
    });
  }
});
