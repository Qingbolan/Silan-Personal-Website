import React from 'react';
import { invoke, isTauri } from '@tauri-apps/api/core';
import {
  ArrowRight,
  Check,
  Database,
  FileCheck2,
  FolderGit2,
  GitBranch,
  KeyRound,
  LoaderCircle,
  LockKeyhole,
  RefreshCw,
  ServerCog,
} from 'lucide-react';
import { Badge } from './ds/Badge';
import { Button } from './ds/Button';
import { Field, Input } from './ds/Input';
import {
  authenticationLabel,
  conciseOnboardingError,
  defaultWorkspaceDestination,
  type GitAuthenticationKind,
} from '../lib/workspaceOnboardingModel';

type BootstrapStatus = {
  state: 'ready' | 'needs_workspace' | 'invalid_workspace' | 'deployment_key';
  project_root: string | null;
  project_name: string | null;
  repository_url: string | null;
  deployment_key_path: string | null;
  configured_deployment_key: string | null;
  deployment_key_required: boolean;
  deploy_host: string | null;
  deploy_user: string | null;
  error: string | null;
};

type RepositoryAccessResult = {
  authentication: GitAuthenticationKind;
  label: string;
};

type GitRepositoryStatus = {
  branch: string;
  upstream: string | null;
  head: string;
  upstream_head: string | null;
  dirty_files: number;
  ahead: number;
  behind: number;
  state: 'synchronized' | 'local_ahead' | 'remote_ahead' | 'diverged' | 'dirty' | 'no_upstream';
};

type DeploymentKeyRequirement = {
  required: boolean;
  configured_path: string | null;
  host: string | null;
  user: string | null;
};

type JoinWorkspaceResult = {
  project_root: string;
  content_root: string;
  database_path: string;
  project_name: string;
  repository_url: string;
  authentication: GitAuthenticationKind;
  layout: 'project_repository' | 'content_repository';
  repository: GitRepositoryStatus;
  deployment_key: DeploymentKeyRequirement;
  projection_revision: string;
  items_scanned: number;
  rows_written: number;
};

type DeploymentKeyValidation = {
  path: string;
  file_name: string;
  permission_mode: string | null;
};

type Phase = 'checking' | 'repository' | 'access' | 'joining' | 'device_key' | 'completing' | 'ready';

const steps = [
  { id: 'repository', label: 'Repository', detail: 'Choose the source of truth', Icon: FolderGit2 },
  { id: 'access', label: 'Device access', detail: 'Verify SSH or OAuth', Icon: LockKeyhole },
  { id: 'joining', label: 'Workspace sync', detail: 'Clone, fetch, inspect', Icon: GitBranch },
  { id: 'configuration', label: 'Local projection', detail: 'Read config and rebuild', Icon: Database },
  { id: 'device_key', label: 'Deployment key', detail: 'Keep credentials on-device', Icon: KeyRound },
] as const;

const phaseIndex = (phase: Phase) => {
  switch (phase) {
    case 'repository': return 0;
    case 'access': return 1;
    case 'joining': return 2;
    case 'device_key':
    case 'completing': return 4;
    case 'ready': return 5;
    default: return -1;
  }
};

const shortRevision = (revision: string) => revision.slice(0, 10);

export function WorkspaceBootstrapGate({ children }: { children: React.ReactNode }) {
  const [phase, setPhase] = React.useState<Phase>(() => (isTauri() ? 'checking' : 'ready'));
  const [bootstrap, setBootstrap] = React.useState<BootstrapStatus | null>(null);
  const [repositoryUrl, setRepositoryUrl] = React.useState('');
  const [destination, setDestination] = React.useState('~/Silan Workspaces/research-workspace');
  const [destinationTouched, setDestinationTouched] = React.useState(false);
  const [branch, setBranch] = React.useState('');
  const [access, setAccess] = React.useState<RepositoryAccessResult | null>(null);
  const [joined, setJoined] = React.useState<JoinWorkspaceResult | null>(null);
  const [deploymentKeyPath, setDeploymentKeyPath] = React.useState('');
  const [keyValidation, setKeyValidation] = React.useState<DeploymentKeyValidation | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!isTauri()) return;
    let active = true;
    invoke<BootstrapStatus>('get_workspace_bootstrap_status')
      .then((status) => {
        if (!active) return;
        setBootstrap(status);
        setRepositoryUrl(status.repository_url || '');
        setDeploymentKeyPath(status.deployment_key_path || status.configured_deployment_key || '');
        if (status.state === 'ready') setPhase('ready');
        else if (status.state === 'deployment_key') setPhase('device_key');
        else {
          setPhase('repository');
          setError(status.error);
        }
      })
      .catch((reason) => {
        if (!active) return;
        setPhase('repository');
        setError(conciseOnboardingError(reason));
      });
    return () => { active = false; };
  }, []);

  React.useEffect(() => {
    if (!destinationTouched) setDestination(defaultWorkspaceDestination(repositoryUrl));
  }, [destinationTouched, repositoryUrl]);

  if (phase === 'ready') return <>{children}</>;

  const currentIndex = phaseIndex(phase);
  const deployment = joined?.deployment_key || (bootstrap ? {
    required: bootstrap.deployment_key_required,
    configured_path: bootstrap.configured_deployment_key,
    host: bootstrap.deploy_host,
    user: bootstrap.deploy_user,
  } : null);
  const projectName = joined?.project_name || bootstrap?.project_name || 'Your workspace';
  const projectRoot = joined?.project_root || bootstrap?.project_root;

  const verifyAccess = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!repositoryUrl.trim()) {
      setError('Enter the SSH or HTTPS address of the Git repository.');
      return;
    }
    if (!destination.trim()) {
      setError('Choose where this device should keep the workspace.');
      return;
    }
    setError(null);
    setAccess(null);
    setPhase('checking');
    try {
      const verified = await invoke<RepositoryAccessResult>('verify_workspace_repository', {
        input: { repositoryUrl: repositoryUrl.trim() },
      });
      setAccess(verified);
      setPhase('access');
    } catch (reason) {
      setError(conciseOnboardingError(reason));
      setPhase('repository');
    }
  };

  const joinWorkspace = async () => {
    setError(null);
    setPhase('joining');
    try {
      const result = await invoke<JoinWorkspaceResult>('join_workspace', {
        input: {
          repositoryUrl: repositoryUrl.trim(),
          destination: destination.trim(),
          branch: branch.trim() || null,
        },
      });
      setJoined(result);
      setDeploymentKeyPath(result.deployment_key.configured_path || '');
      setBootstrap((current) => ({
        ...current,
        state: 'deployment_key',
        project_root: result.project_root,
        project_name: result.project_name,
        repository_url: result.repository_url,
        deployment_key_path: null,
        configured_deployment_key: result.deployment_key.configured_path,
        deployment_key_required: result.deployment_key.required,
        deploy_host: result.deployment_key.host,
        deploy_user: result.deployment_key.user,
        error: null,
      }));
      setPhase('device_key');
    } catch (reason) {
      setError(conciseOnboardingError(reason));
      setPhase('access');
    }
  };

  const completeOnboarding = async () => {
    setError(null);
    setKeyValidation(null);
    setPhase('completing');
    try {
      const key = deploymentKeyPath.trim();
      if (key) {
        const validation = await invoke<DeploymentKeyValidation>('validate_workspace_deployment_key', { path: key });
        setKeyValidation(validation);
      }
      const status = await invoke<BootstrapStatus>('complete_workspace_onboarding', {
        input: { deploymentKeyPath: key || null },
      });
      setBootstrap(status);
      setPhase('ready');
    } catch (reason) {
      setError(conciseOnboardingError(reason));
      setPhase('device_key');
    }
  };

  return (
    <main className="workspace-onboarding" aria-busy={phase === 'checking' || phase === 'joining' || phase === 'completing'}>
      <div className="workspace-onboarding-ambient" aria-hidden="true" />
      <aside className="onboarding-rail">
        <div className="onboarding-brand">
          <span className="onboarding-brand-mark">S</span>
          <div>
            <strong>Silan Context System</strong>
            <span>Local-first research publishing</span>
          </div>
        </div>

        <div className="onboarding-rail-copy">
          <span className="onboarding-kicker">New device setup</span>
          <h1>Continue from the source, not the server.</h1>
          <p>Git carries the authoring workspace. Production keeps runtime data. This device joins without mixing those responsibilities.</p>
        </div>

        <ol className="onboarding-steps" aria-label="Workspace onboarding progress">
          {steps.map(({ id, label, detail, Icon }, index) => {
            const configurationComplete = currentIndex >= 4;
            const complete = index < currentIndex || (id === 'configuration' && configurationComplete);
            const active = index === currentIndex || (id === 'configuration' && phase === 'joining');
            return (
              <li key={id} data-complete={complete || undefined} data-active={active || undefined}>
                <span className="onboarding-step-icon">{complete ? <Check size={14} /> : <Icon size={15} />}</span>
                <span><strong>{label}</strong><small>{detail}</small></span>
              </li>
            );
          })}
        </ol>

        <div className="onboarding-privacy-note">
          <KeyRound size={15} />
          <span>Credentials stay in your SSH agent, Git credential manager, or local filesystem.</span>
        </div>
      </aside>

      <section className="onboarding-stage">
        <div className="onboarding-stage-inner">
          {phase === 'checking' && !bootstrap && !repositoryUrl && (
            <section className="onboarding-task onboarding-task-progress onboarding-task-enter">
              <header className="onboarding-task-header">
                <span className="onboarding-step-number"><LoaderCircle className="spin" size={18} /></span>
                <div><p>Workspace bootstrap</p><h2>Looking for this device's workspace.</h2></div>
              </header>
              <p className="onboarding-lede">Reading the device-local workspace registry and validating its project configuration.</p>
              <div className="onboarding-progress-track"><span /></div>
            </section>
          )}

          {(phase === 'repository' || phase === 'checking' && bootstrap !== null) && (
            <form className="onboarding-task onboarding-task-enter" onSubmit={verifyAccess}>
              <header className="onboarding-task-header">
                <span className="onboarding-step-number">01</span>
                <div>
                  <p>Join existing workspace</p>
                  <h2>Where does the work live?</h2>
                </div>
              </header>
              <p className="onboarding-lede">Use the Git repository that owns the Markdown source and its history. Do not enter the production server address.</p>

              <div className="onboarding-fields">
                <Field label="Git repository" hint="SSH uses your agent; HTTPS uses the system Git credential manager.">
                  <div className="onboarding-input-with-icon">
                    <GitBranch size={16} />
                    <Input
                      autoFocus
                      disabled={phase === 'checking'}
                      value={repositoryUrl}
                      onChange={(event) => setRepositoryUrl(event.target.value)}
                      placeholder="git@github.com:owner/workspace.git"
                      spellCheck={false}
                      autoCapitalize="none"
                      autoCorrect="off"
                    />
                  </div>
                </Field>
                <Field label="Workspace folder" hint="An existing checkout is fetched; a missing or empty folder is cloned.">
                  <div className="onboarding-input-with-icon">
                    <FolderGit2 size={16} />
                    <Input
                      disabled={phase === 'checking'}
                      value={destination}
                      onChange={(event) => {
                        setDestinationTouched(true);
                        setDestination(event.target.value);
                      }}
                      placeholder="~/Silan Workspaces/research-site"
                      spellCheck={false}
                    />
                  </div>
                </Field>
                <Field label="Branch" hint="Leave empty to use the repository's default branch.">
                  <Input
                    disabled={phase === 'checking'}
                    value={branch}
                    onChange={(event) => setBranch(event.target.value)}
                    placeholder="Default branch"
                    spellCheck={false}
                    autoCapitalize="none"
                  />
                </Field>
              </div>

              {error && <div className="onboarding-inline-error" role="alert">{error}</div>}
              <footer className="onboarding-actions">
                <span>We verify read access before writing any files.</span>
                <Button type="submit" loading={phase === 'checking'}>
                  Verify access <ArrowRight size={15} />
                </Button>
              </footer>
            </form>
          )}

          {phase === 'access' && access && (
            <section className="onboarding-task onboarding-task-enter">
              <header className="onboarding-task-header">
                <span className="onboarding-step-number">02</span>
                <div><p>Device access</p><h2>This device can read the repository.</h2></div>
              </header>
              <div className="onboarding-access-proof">
                <span className="onboarding-proof-icon"><Check size={22} /></span>
                <div>
                  <Badge tone="success" dot>{authenticationLabel(access.authentication)}</Badge>
                  <strong>{access.label}</strong>
                  <code>{repositoryUrl}</code>
                </div>
              </div>
              <div className="onboarding-operation-preview">
                <div><FolderGit2 size={16} /><span><strong>Destination</strong><small>{destination}</small></span></div>
                <div><RefreshCw size={16} /><span><strong>Update policy</strong><small>Fetch, inspect, then fast-forward only</small></span></div>
                <div><GitBranch size={16} /><span><strong>Conflict policy</strong><small>Dirty or diverged workspaces stop without mutation</small></span></div>
              </div>
              {error && <div className="onboarding-inline-error" role="alert">{error}</div>}
              <footer className="onboarding-actions">
                <Button variant="ghost" onClick={() => { setPhase('repository'); setError(null); }}>Change repository</Button>
                <Button onClick={joinWorkspace}>Clone or update workspace <ArrowRight size={15} /></Button>
              </footer>
            </section>
          )}

          {phase === 'joining' && (
            <section className="onboarding-task onboarding-task-progress onboarding-task-enter">
              <header className="onboarding-task-header">
                <span className="onboarding-step-number"><LoaderCircle className="spin" size={18} /></span>
                <div><p>Workspace sync</p><h2>Preparing a clean local workspace.</h2></div>
              </header>
              <p className="onboarding-lede">Git is fetching the source, checking branch safety, reading the project configuration, and rebuilding the local database.</p>
              <div className="onboarding-progress-track"><span /></div>
              <div className="onboarding-progress-list">
                <div><RefreshCw size={16} /><span>Clone or fetch origin</span></div>
                <div><GitBranch size={16} /><span>Check dirty, ahead, behind, and divergence state</span></div>
                <div><FileCheck2 size={16} /><span>Validate silan-viking.toml and content schema</span></div>
                <div><Database size={16} /><span>Rebuild portfolio.db from Markdown</span></div>
              </div>
            </section>
          )}

          {(phase === 'device_key' || phase === 'completing') && (
            <section className="onboarding-task onboarding-task-enter">
              <header className="onboarding-task-header">
                <span className="onboarding-step-number">05</span>
                <div><p>Device-specific security</p><h2>Keep deployment access on this device.</h2></div>
              </header>

              <div className="onboarding-ready-summary">
                <div className="onboarding-ready-title">
                  <span><Check size={17} /></span>
                  <div><strong>{projectName}</strong><small>{projectRoot}</small></div>
                </div>
                {joined && (
                  <dl>
                    <div><dt>Branch</dt><dd>{joined.repository.branch}</dd></div>
                    <div><dt>Revision</dt><dd>{shortRevision(joined.repository.head)}</dd></div>
                    <div><dt>Content</dt><dd>{joined.items_scanned} items</dd></div>
                    <div><dt>Projection</dt><dd>{joined.rows_written} rows</dd></div>
                  </dl>
                )}
              </div>

              {deployment?.required ? (
                <div className="onboarding-key-section">
                  <div className="onboarding-key-context">
                    <ServerCog size={17} />
                    <span>
                      <strong>{deployment.user ? `${deployment.user}@` : ''}{deployment.host}</strong>
                      <small>The shared config names the server; this field selects only this device's private key.</small>
                    </span>
                  </div>
                  <Field label="Deployment private key" hint="Only the path is saved. The key file never enters the workspace or desktop registry.">
                    <div className="onboarding-input-with-icon">
                      <KeyRound size={16} />
                      <Input
                        value={deploymentKeyPath}
                        onChange={(event) => { setDeploymentKeyPath(event.target.value); setKeyValidation(null); }}
                        placeholder="~/.ssh/site-deploy-ed25519"
                        spellCheck={false}
                      />
                    </div>
                  </Field>
                </div>
              ) : (
                <div className="onboarding-key-optional">
                  <KeyRound size={18} />
                  <div><strong>No remote deployment key is required.</strong><span>The workspace has no remote deploy target. You can configure one later without blocking local authoring.</span></div>
                </div>
              )}

              {keyValidation && (
                <div className="onboarding-key-valid"><Check size={14} /> {keyValidation.file_name} · permissions {keyValidation.permission_mode || 'verified'}</div>
              )}
              {error && <div className="onboarding-inline-error" role="alert">{error}</div>}
              <footer className="onboarding-actions onboarding-actions-final">
                <span>{deployment?.required ? 'The key must be a private-key file with restricted permissions.' : 'Deployment remains available from Settings when you need it.'}</span>
                <div className="onboarding-final-buttons">
                  <Button
                    variant="ghost"
                    disabled={phase === 'completing'}
                    onClick={() => {
                      setJoined(null);
                      setAccess(null);
                      setError(null);
                      setKeyValidation(null);
                      setPhase('repository');
                    }}
                  >
                    Use another repository
                  </Button>
                  <Button loading={phase === 'completing'} onClick={completeOnboarding}>
                    Enter workspace <ArrowRight size={15} />
                  </Button>
                </div>
              </footer>
            </section>
          )}
        </div>
      </section>
    </main>
  );
}
