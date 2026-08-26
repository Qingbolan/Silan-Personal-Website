import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const html = readFileSync(new URL('../../index.html', import.meta.url), 'utf8');
const startupExperience = readFileSync(
  new URL('../components/StartupExperience.tsx', import.meta.url),
  'utf8',
);

test('the pre-React primer is an autonomous animated character instead of a static image', () => {
  assert.match(html, /id="boot-primer"/);
  assert.match(html, /animation: boot-primer-gaze [^;]+ infinite/);
  assert.match(html, /animation: boot-primer-blink [^;]+ infinite/);
  assert.match(html, /animation: boot-copy-cycle [^;]+ infinite/);
  assert.doesNotMatch(html, /#root:empty/);
});

test('React crossfades and removes the primer after taking ownership', () => {
  assert.match(startupExperience, /getElementById\('boot-primer'\)/);
  assert.match(startupExperience, /classList\.add\('is-handoff'\)/);
  assert.match(startupExperience, /primer\.remove\(\)/);
});
