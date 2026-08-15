import { isTauri } from '@tauri-apps/api/core';

export type DesktopWindowPlatform = 'macos' | 'windows' | 'linux' | 'web';

export function detectDesktopWindowPlatform(
  tauriRuntime: boolean,
  userAgent: string,
): DesktopWindowPlatform {
  if (!tauriRuntime) return 'web';
  if (/Windows/i.test(userAgent)) return 'windows';
  if (/Linux|X11/i.test(userAgent)) return 'linux';
  if (/Macintosh|Mac OS X/i.test(userAgent)) return 'macos';
  return 'web';
}

export function desktopWindowChromeClassFor(platform: DesktopWindowPlatform) {
  return platform === 'web'
    ? ''
    : `desktop-titlebar-enabled desktop-platform-${platform}`;
}

export function usesCustomWindowControlsFor(platform: DesktopWindowPlatform) {
  return platform === 'windows' || platform === 'linux';
}

const userAgent = typeof navigator === 'undefined' ? '' : navigator.userAgent;
export const desktopWindowPlatform = detectDesktopWindowPlatform(isTauri(), userAgent);

export const usesDesktopTitlebar = desktopWindowPlatform !== 'web';
export const usesCustomWindowControls = usesCustomWindowControlsFor(desktopWindowPlatform);

export const desktopWindowChromeClassName = desktopWindowChromeClassFor(desktopWindowPlatform);
