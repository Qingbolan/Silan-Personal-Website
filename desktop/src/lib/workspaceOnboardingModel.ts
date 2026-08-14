export type GitAuthenticationKind = 'ssh' | 'oauth' | 'local';

export const repositoryName = (repositoryUrl: string) => {
  const normalized = repositoryUrl.trim().replace(/\/+$/, '');
  const tail = normalized.split(/[/:]/).filter(Boolean).at(-1) || 'research-workspace';
  return tail.replace(/\.git$/i, '').replace(/[^a-zA-Z0-9._-]+/g, '-');
};

export const defaultWorkspaceDestination = (repositoryUrl: string) => (
  `~/Silan Workspaces/${repositoryName(repositoryUrl)}`
);

export const authenticationLabel = (kind: GitAuthenticationKind) => {
  switch (kind) {
    case 'ssh':
      return 'SSH identity';
    case 'oauth':
      return 'Git OAuth session';
    default:
      return 'Local repository';
  }
};

export const conciseOnboardingError = (reason: unknown) => {
  const message = String(reason).replace(/^Error:\s*/i, '').trim();
  if (/Permission denied \(publickey\)/i.test(message)) {
    return 'SSH could not authenticate this device. Add the correct key to your SSH agent, then verify again.';
  }
  if (/Authentication failed|could not read Username|terminal prompts disabled/i.test(message)) {
    return 'Git HTTPS authentication is unavailable. Sign in with your system Git credential manager, then verify again.';
  }
  if (/Repository not found/i.test(message)) {
    return 'The repository was not found or this device does not have access to it.';
  }
  return message || 'The workspace operation could not be completed.';
};
