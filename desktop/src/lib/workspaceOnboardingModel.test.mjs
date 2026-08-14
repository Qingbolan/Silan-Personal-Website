import assert from 'node:assert/strict';
import test from 'node:test';
import {
  authenticationLabel,
  conciseOnboardingError,
  defaultWorkspaceDestination,
  repositoryName,
} from './workspaceOnboardingModel.ts';

test('repository addresses produce a stable device-local destination', () => {
  assert.equal(repositoryName('git@github.com:Qingbolan/silan-content.git'), 'silan-content');
  assert.equal(
    defaultWorkspaceDestination('https://github.com/Qingbolan/silan-content.git'),
    '~/Silan Workspaces/silan-content',
  );
});

test('credential labels and errors explain the device action', () => {
  assert.equal(authenticationLabel('oauth'), 'Git OAuth session');
  assert.match(
    conciseOnboardingError('Permission denied (publickey)'),
    /SSH could not authenticate this device/,
  );
  assert.match(
    conciseOnboardingError('fatal: could not read Username; terminal prompts disabled'),
    /credential manager/,
  );
});
