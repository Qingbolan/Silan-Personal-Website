import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import {
  desktopWindowChromeClassFor,
  detectDesktopWindowPlatform,
  usesCustomWindowControlsFor,
} from './desktopWindow.ts';

const readJson = (relativePath) => JSON.parse(
  readFileSync(new URL(relativePath, import.meta.url), 'utf8'),
);

test('the browser preview does not receive native desktop chrome', () => {
  assert.equal(
    detectDesktopWindowPlatform(false, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
    'web',
  );
  assert.equal(desktopWindowChromeClassFor('web'), '');
});

test('the Tauri shell identifies every supported desktop platform', () => {
  assert.equal(
    detectDesktopWindowPlatform(true, 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'),
    'macos',
  );
  assert.equal(
    detectDesktopWindowPlatform(true, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
    'windows',
  );
  assert.equal(
    detectDesktopWindowPlatform(true, 'Mozilla/5.0 (X11; Linux x86_64)'),
    'linux',
  );
});

test('desktop platform classes select a shared titlebar with platform-specific controls', () => {
  assert.equal(
    desktopWindowChromeClassFor('macos'),
    'desktop-titlebar-enabled desktop-platform-macos',
  );
  assert.equal(
    desktopWindowChromeClassFor('windows'),
    'desktop-titlebar-enabled desktop-platform-windows',
  );
  assert.equal(
    desktopWindowChromeClassFor('linux'),
    'desktop-titlebar-enabled desktop-platform-linux',
  );
  assert.equal(usesCustomWindowControlsFor('macos'), false);
  assert.equal(usesCustomWindowControlsFor('windows'), true);
  assert.equal(usesCustomWindowControlsFor('linux'), true);
});

test('Tauri configuration keeps macOS native traffic lights and gives other desktops custom chrome', () => {
  const sharedConfig = readJson('../../src-tauri/tauri.conf.json');
  const macOsConfig = readJson('../../src-tauri/tauri.macos.conf.json');
  const permissions = readJson('../../src-tauri/capabilities/default.json').permissions;

  assert.equal(sharedConfig.app.windows[0].decorations, false);
  assert.equal(sharedConfig.bundle.targets, undefined);
  assert.equal(macOsConfig.app.windows[0].decorations, true);
  assert.equal(macOsConfig.app.windows[0].titleBarStyle, 'Overlay');
  assert.equal(macOsConfig.app.windows[0].hiddenTitle, true);
  assert.deepEqual(macOsConfig.app.windows[0].trafficLightPosition, { x: 14, y: 26 });
  assert.deepEqual(macOsConfig.bundle.targets, ['app']);
  assert.equal(macOsConfig.bundle.macOS.bundleName, 'Silan Context System');
  assert.ok(permissions.includes('core:window:allow-close'));
  assert.ok(permissions.includes('core:window:allow-minimize'));
  assert.ok(permissions.includes('core:window:allow-toggle-maximize'));
});
