//! Process-wide desktop workspace selection and its durable, device-local record.
//!
//! The selected project path and deployment-key path are machine concerns, so
//! they live under the app config directory rather than in the Git workspace.
//! No key material or repository credential is ever persisted here.

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::{OnceLock, RwLock};

const REGISTRY_FILE: &str = "workspace.json";
const REGISTRY_VERSION: u8 = 1;

static RUNTIME: OnceLock<DesktopRuntime> = OnceLock::new();

#[derive(Debug)]
struct DesktopRuntime {
    registry_path: PathBuf,
    selection: RwLock<Option<WorkspaceSelection>>,
    initialization_error: RwLock<Option<String>>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum WorkspaceActivationState {
    Prepared,
    Ready,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub(crate) struct WorkspaceSelection {
    version: u8,
    pub(crate) project_root: PathBuf,
    pub(crate) repository_url: String,
    pub(crate) project_name: String,
    pub(crate) deployment_key_path: Option<PathBuf>,
    pub(crate) state: WorkspaceActivationState,
}

impl WorkspaceSelection {
    pub(crate) fn prepared(
        project_root: PathBuf,
        repository_url: String,
        project_name: String,
    ) -> Self {
        Self {
            version: REGISTRY_VERSION,
            project_root,
            repository_url,
            project_name,
            deployment_key_path: None,
            state: WorkspaceActivationState::Prepared,
        }
    }
}

pub(crate) fn initialize(config_dir: impl AsRef<Path>) -> Result<(), String> {
    let config_dir = config_dir.as_ref();
    fs::create_dir_all(config_dir).map_err(|error| {
        format!(
            "cannot create desktop config directory `{}`: {error}",
            config_dir.display()
        )
    })?;
    let registry_path = config_dir.join(REGISTRY_FILE);
    let (selection, initialization_error) = match read_selection(&registry_path) {
        Ok(selection) => (selection, None),
        Err(error) => (None, Some(error)),
    };
    apply_device_environment(selection.as_ref());
    RUNTIME
        .set(DesktopRuntime {
            registry_path,
            selection: RwLock::new(selection),
            initialization_error: RwLock::new(initialization_error),
        })
        .map_err(|_| "desktop workspace runtime was initialized more than once".to_owned())
}

pub(crate) fn initialization_error() -> Option<String> {
    runtime()
        .ok()
        .and_then(|runtime| runtime.initialization_error.read().ok()?.clone())
}

pub(crate) fn selection() -> Option<WorkspaceSelection> {
    runtime()
        .ok()
        .and_then(|runtime| runtime.selection.read().ok()?.clone())
}

pub(crate) fn active_project_root() -> Option<PathBuf> {
    selection().and_then(|selection| {
        (selection.state == WorkspaceActivationState::Ready).then_some(selection.project_root)
    })
}

pub(crate) fn save_selection(selection: WorkspaceSelection) -> Result<(), String> {
    let runtime = runtime()?;
    persist_selection(&runtime.registry_path, &selection)?;
    let mut active = runtime
        .selection
        .write()
        .map_err(|_| "desktop workspace registry lock is poisoned".to_owned())?;
    apply_device_environment(Some(&selection));
    *active = Some(selection);
    if let Ok(mut error) = runtime.initialization_error.write() {
        *error = None;
    }
    Ok(())
}

fn apply_device_environment(selection: Option<&WorkspaceSelection>) {
    if let Some(selection) = selection {
        match selection.deployment_key_path.as_ref() {
            Some(path) => std::env::set_var("SILAN_DEPLOY_SSH_KEY_PATH", path),
            None => std::env::remove_var("SILAN_DEPLOY_SSH_KEY_PATH"),
        }
    }
}

pub(crate) fn complete_selection(deployment_key_path: Option<PathBuf>) -> Result<(), String> {
    let mut selection = selection().ok_or_else(|| {
        "no prepared workspace exists; join a workspace before completing onboarding".to_owned()
    })?;
    selection.deployment_key_path = deployment_key_path;
    selection.state = WorkspaceActivationState::Ready;
    save_selection(selection)
}

fn runtime() -> Result<&'static DesktopRuntime, String> {
    RUNTIME
        .get()
        .ok_or_else(|| "desktop workspace runtime is not initialized".to_owned())
}

fn read_selection(path: &Path) -> Result<Option<WorkspaceSelection>, String> {
    if !path.is_file() {
        return Ok(None);
    }
    let source = fs::read_to_string(path)
        .map_err(|error| format!("cannot read `{}`: {error}", path.display()))?;
    let selection: WorkspaceSelection = serde_json::from_str(&source)
        .map_err(|error| format!("cannot parse `{}`: {error}", path.display()))?;
    if selection.version != REGISTRY_VERSION {
        return Err(format!(
            "unsupported desktop workspace registry version {}",
            selection.version
        ));
    }
    Ok(Some(selection))
}

fn persist_selection(path: &Path, selection: &WorkspaceSelection) -> Result<(), String> {
    let parent = path.parent().ok_or_else(|| {
        format!(
            "cannot resolve desktop config directory for `{}`",
            path.display()
        )
    })?;
    let bytes = serde_json::to_vec_pretty(selection)
        .map_err(|error| format!("cannot encode workspace registry: {error}"))?;
    let mut temporary = tempfile::NamedTempFile::new_in(parent)
        .map_err(|error| format!("cannot stage `{}`: {error}", path.display()))?;
    use std::io::Write;
    temporary
        .write_all(&bytes)
        .map_err(|error| format!("cannot stage `{}`: {error}", path.display()))?;
    temporary
        .as_file()
        .sync_all()
        .map_err(|error| format!("cannot sync `{}`: {error}", path.display()))?;
    temporary
        .persist(path)
        .map_err(|error| format!("cannot replace `{}`: {}", path.display(), error.error))?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn registry_round_trip_never_contains_key_material() {
        let directory = tempfile::tempdir().expect("temporary config");
        let path = directory.path().join(REGISTRY_FILE);
        let selection = WorkspaceSelection {
            version: REGISTRY_VERSION,
            project_root: PathBuf::from("/work/site"),
            repository_url: "git@github.com:owner/site.git".to_owned(),
            project_name: "site".to_owned(),
            deployment_key_path: Some(PathBuf::from("/keys/deploy.pem")),
            state: WorkspaceActivationState::Ready,
        };
        persist_selection(&path, &selection).expect("persist");
        let restored = read_selection(&path).expect("read").expect("selection");
        assert_eq!(restored.project_root, selection.project_root);
        assert_eq!(restored.deployment_key_path, selection.deployment_key_path);
        let source = fs::read_to_string(path).expect("registry source");
        assert!(!source.contains("PRIVATE KEY"));
    }
}
