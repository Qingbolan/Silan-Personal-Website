export type DeploymentPlanState = 'loading' | 'ready' | 'error';

export type DeploymentReadinessState =
  | 'comparing'
  | 'synchronized'
  | 'remote_ahead'
  | 'ready_with_unsaved'
  | 'blocked_uncommitted'
  | 'checking'
  | 'check_failed'
  | 'ready'
  | 'deploying';

export type DeploymentReadiness = {
  state: DeploymentReadinessState;
  canDeploy: boolean;
  message: string;
  actionTitle: string;
};

type DeploymentReadinessInput = {
  localCommitCount: number | null;
  remoteCommitCount: number;
  workspaceChangeCount: number;
  unsavedDocumentCount: number;
  planState: DeploymentPlanState;
  planError?: string | null;
  deploying: boolean;
};

const countLabel = (count: number, singular: string, plural = `${singular}s`) => (
  `${count} ${count === 1 ? singular : plural}`
);

const conciseError = (message: string | null | undefined) => (
  message?.replace(/^Error:\s*/i, '').trim() || 'The deployment plan could not be loaded.'
);

/**
 * The dashboard's single deploy-readiness state machine. The status copy,
 * button availability, and tooltip must all come from this result so the UI
 * cannot claim a release is ready while silently disabling its action.
 */
export const deploymentReadinessFor = ({
  localCommitCount,
  remoteCommitCount,
  workspaceChangeCount,
  unsavedDocumentCount,
  planState,
  planError,
  deploying,
}: DeploymentReadinessInput): DeploymentReadiness => {
  if (localCommitCount === null) {
    return {
      state: 'comparing',
      canDeploy: false,
      message: 'Comparing local and deployed versions…',
      actionTitle: 'Wait for the local and deployed versions to be compared',
    };
  }

  if (localCommitCount === 0) {
    if (remoteCommitCount > 0) {
      const remoteLabel = countLabel(remoteCommitCount, 'moment');
      return {
        state: 'remote_ahead',
        canDeploy: false,
        message: `${remoteLabel} ${remoteCommitCount === 1 ? 'exists' : 'exist'} on the deployed version`,
        actionTitle: 'The deployed version is ahead of this workspace',
      };
    }
    return {
      state: 'synchronized',
      canDeploy: false,
      message: 'Local and deployed content match',
      actionTitle: 'There are no committed changes to deploy',
    };
  }

  if (deploying) {
    return {
      state: 'deploying',
      canDeploy: false,
      message: `Deploying ${countLabel(localCommitCount, 'committed moment')}…`,
      actionTitle: 'Deployment is in progress',
    };
  }

  if (workspaceChangeCount > 0) {
    const changeLabel = countLabel(workspaceChangeCount, 'uncommitted change');
    return {
      state: 'blocked_uncommitted',
      canDeploy: false,
      message: `${changeLabel} must be committed first`,
      actionTitle: `Commit ${changeLabel} before deploying`,
    };
  }

  if (planState === 'loading') {
    return {
      state: 'checking',
      canDeploy: false,
      message: 'Checking deployment configuration…',
      actionTitle: 'Wait for the deployment check to finish',
    };
  }

  if (planState === 'error') {
    const error = conciseError(planError);
    return {
      state: 'check_failed',
      canDeploy: false,
      message: `Deployment check failed: ${error}`,
      actionTitle: `Retry deployment check. ${error}`,
    };
  }

  if (unsavedDocumentCount > 0) {
    const commitLabel = countLabel(localCommitCount, 'committed moment');
    const unsavedLabel = countLabel(unsavedDocumentCount, 'unsaved Markdown file');
    return {
      state: 'ready_with_unsaved',
      canDeploy: true,
      message: `${commitLabel} ready; ${unsavedLabel} will stay local`,
      actionTitle: `Deploy committed content. ${unsavedLabel} will stay local`,
    };
  }

  return {
    state: 'ready',
    canDeploy: true,
    message: `${countLabel(localCommitCount, 'committed moment')} ready to deploy`,
    actionTitle: 'Deploy committed content to the production website',
  };
};
