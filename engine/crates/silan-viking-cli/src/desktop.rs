//! Desktop application lifecycle adapter.
//!
//! The default command launches an installed, compiled application bundle.
//! Source-tree discovery, Node and the Tauri development server belong only
//! to the explicit `desktop dev` lifecycle.

use silan_viking_app::Workspace;
use std::env;
use std::ffi::OsString;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

const APPLICATION_BUNDLE: &str = "Silan Context System.app";
const APPLICATION_EXECUTABLE: &str = "Silan Context System";
const APPLICATION_OVERRIDE_ENV: &str = "SILAN_DESKTOP_APP";

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum DesktopLaunchMode {
    Installed,
    Development,
}

impl DesktopLaunchMode {
    fn parse(arguments: &[&str]) -> Result<Self, String> {
        match arguments {
            [] => Ok(Self::Installed),
            ["dev"] => Ok(Self::Development),
            [argument, ..] => Err(format!(
                "desktop: unknown argument `{argument}` · expected `desktop` or `desktop dev`"
            )),
        }
    }
}

pub(crate) fn run(content_root: &Path, db_path: &Path, arguments: &[&str]) -> Result<(), String> {
    match DesktopLaunchMode::parse(arguments)? {
        DesktopLaunchMode::Installed => {
            let application = InstalledDesktopApplication::discover()?;
            DesktopWorkspaceSession::prepare(content_root, db_path)?.launch(application)
        }
        DesktopLaunchMode::Development => {
            let application = DevelopmentDesktopApplication::discover(content_root)?;
            DesktopWorkspaceSession::prepare(content_root, db_path)?.develop(application)
        }
    }
}

#[derive(Debug)]
struct DesktopWorkspaceSession {
    content_root: PathBuf,
    db_path: PathBuf,
    project_root: PathBuf,
    current_cli: PathBuf,
}

impl DesktopWorkspaceSession {
    fn prepare(content_root: &Path, db_path: &Path) -> Result<Self, String> {
        let content_root = fs::canonicalize(content_root).map_err(|error| {
            format!(
                "desktop: resolve content root {}: {error}",
                content_root.display()
            )
        })?;
        let db_path = absolute_path(db_path)
            .map_err(|error| format!("desktop: resolve database path: {error}"))?;
        let project_root = content_root.parent().unwrap_or(&content_root).to_path_buf();
        let current_cli = env::current_exe()
            .map_err(|error| format!("desktop: resolve current CLI executable: {error}"))?;

        let workspace = Workspace::open(&content_root)
            .map_err(|error| format!("desktop: open content workspace: {error}"))?;
        let sync = workspace
            .sync(&db_path)
            .map_err(|error| format!("desktop: refresh SQLite projection: {error}"))?;

        println!("desktop editor: Silan Context System");
        println!("content root: {}", content_root.display());
        println!("database: {}", db_path.display());
        println!(
            "projection: {} items · {}",
            sync.items_scanned,
            if sync.wrote { "refreshed" } else { "current" }
        );

        Ok(Self {
            content_root,
            db_path,
            project_root,
            current_cli,
        })
    }

    fn configured_command(&self, executable: &Path) -> Command {
        let mut command = Command::new(executable);
        command
            .current_dir(&self.project_root)
            .env("SILAN_DESKTOP_PROJECT", &self.project_root)
            .env("SILAN_DESKTOP_CONTENT", &self.content_root)
            .env("SILAN_DESKTOP_DB", &self.db_path)
            // Desktop delivery actions must call the exact engine binary that
            // opened this session, not an older command found on PATH.
            .env("SILAN_VIKING_BIN", &self.current_cli);
        command
    }

    fn launch(self, application: InstalledDesktopApplication) -> Result<(), String> {
        println!("application: {}", application.bundle.display());
        let status = Command::new("open")
            .arg("-n")
            .arg("--env")
            .arg(environment_argument(
                "SILAN_DESKTOP_PROJECT",
                &self.project_root,
            ))
            .arg("--env")
            .arg(environment_argument(
                "SILAN_DESKTOP_CONTENT",
                &self.content_root,
            ))
            .arg("--env")
            .arg(environment_argument("SILAN_DESKTOP_DB", &self.db_path))
            .arg("--env")
            .arg(environment_argument("SILAN_VIKING_BIN", &self.current_cli))
            .arg(&application.bundle)
            .status()
            .map_err(|error| format!("desktop: ask macOS to launch application: {error}"))?;
        if !status.success() {
            return Err("macOS could not launch the compiled Desktop application".into());
        }
        println!("desktop: launched compiled application");
        Ok(())
    }

    fn develop(self, application: DevelopmentDesktopApplication) -> Result<(), String> {
        println!("development source: {}", application.source_root.display());
        println!("press Ctrl-C to stop the Tauri development session");
        let status = self
            .configured_command(Path::new("npm"))
            .current_dir(&application.source_root)
            .args(["run", "desktop"])
            .status()
            .map_err(|error| format!("desktop dev: launch Tauri: {error}"))?;
        if !status.success() {
            return Err("Tauri desktop development session exited with a non-zero status".into());
        }
        Ok(())
    }
}

#[derive(Debug)]
struct InstalledDesktopApplication {
    bundle: PathBuf,
}

impl InstalledDesktopApplication {
    fn discover() -> Result<Self, String> {
        if let Some(configured) = env::var_os(APPLICATION_OVERRIDE_ENV) {
            return Self::from_bundle(PathBuf::from(configured)).map_err(|error| {
                format!("desktop: invalid {APPLICATION_OVERRIDE_ENV} override: {error}")
            });
        }

        for bundle in installed_bundle_candidates() {
            if let Ok(application) = Self::from_bundle(bundle) {
                return Ok(application);
            }
        }

        Err(format!(
            "desktop: compiled application is not installed · run \
             `packaging/release/dev-install-local.sh --desktop-only --user-apps`, \
             or set {APPLICATION_OVERRIDE_ENV} to an installed .app bundle"
        ))
    }

    fn from_bundle(bundle: PathBuf) -> Result<Self, String> {
        if !bundle.is_dir() {
            return Err(format!(
                "application bundle is missing: {}",
                bundle.display()
            ));
        }
        let executable = bundle
            .join("Contents")
            .join("MacOS")
            .join(APPLICATION_EXECUTABLE);
        if !executable.is_file() {
            return Err(format!(
                "compiled application executable is missing: {}",
                executable.display()
            ));
        }
        Ok(Self { bundle })
    }
}

fn installed_bundle_candidates() -> Vec<PathBuf> {
    let mut candidates = Vec::with_capacity(2);
    if let Some(home) = env::var_os("HOME") {
        candidates.push(
            PathBuf::from(home)
                .join("Applications")
                .join(APPLICATION_BUNDLE),
        );
    }
    candidates.push(PathBuf::from("/Applications").join(APPLICATION_BUNDLE));
    candidates
}

#[derive(Debug)]
struct DevelopmentDesktopApplication {
    source_root: PathBuf,
}

impl DevelopmentDesktopApplication {
    fn discover(content_root: &Path) -> Result<Self, String> {
        let project_root = content_root.parent().unwrap_or(content_root);
        let source_root = project_root.join("desktop");
        let package_json = source_root.join("package.json");
        if !package_json.is_file() {
            return Err(format!(
                "desktop dev: source package is missing: {}",
                package_json.display()
            ));
        }
        let tauri = source_root.join("node_modules/.bin/tauri");
        if !tauri.is_file() {
            return Err(format!(
                "desktop dev: Tauri dependencies are not installed · run `npm ci --prefix {}`",
                source_root.display()
            ));
        }
        Ok(Self { source_root })
    }
}

fn absolute_path(path: &Path) -> Result<PathBuf, String> {
    if path.is_absolute() {
        return Ok(path.to_path_buf());
    }
    Ok(env::current_dir()
        .map_err(|error| error.to_string())?
        .join(path))
}

fn environment_argument(name: &str, value: &Path) -> OsString {
    let mut argument = OsString::from(name);
    argument.push("=");
    argument.push(value);
    argument
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn launch_mode_requires_an_explicit_dev_subcommand() {
        assert_eq!(
            DesktopLaunchMode::parse(&[]).expect("installed mode"),
            DesktopLaunchMode::Installed
        );
        assert_eq!(
            DesktopLaunchMode::parse(&["dev"]).expect("development mode"),
            DesktopLaunchMode::Development
        );
        assert!(DesktopLaunchMode::parse(&["--debug"]).is_err());
        assert!(DesktopLaunchMode::parse(&["dev", "extra"]).is_err());
    }

    #[test]
    fn installed_bundle_requires_the_compiled_macos_executable() {
        let missing = PathBuf::from("/definitely/missing/Silan Context System.app");
        let error = InstalledDesktopApplication::from_bundle(missing)
            .expect_err("missing bundle must fail");
        assert!(error.contains("application bundle is missing"));
    }
}
