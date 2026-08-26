//! Durable authored-source snapshots and atomic disaster recovery.
//!
//! Production remains a projection target, not the authoring Git remote. A
//! deploy nevertheless carries the committed public source (`SCHEMA.md`,
//! `.gitignore`, and `resources/`) so a lost workstation can recover the
//! exact deployed tree. The private `agent/` namespace is intentionally not
//! present in this archive; its durability remains the responsibility of the
//! content repository's private Git remote.

use crate::{api_base_url, workspace_stats_sync_token, GitRepo};
use sha2::{Digest, Sha256};
use std::fs;
use std::io::{Cursor, Read};
use std::path::{Component, Path, PathBuf};
use std::time::Duration;
use tar::Archive;
use thiserror::Error;

const AUTHOR_NAME: &str = "Silan.Hu";
const AUTHOR_EMAIL: &str = "silan.hu@u.nus.edu";
const SOURCE_PATHS: &[&str] = &[".gitignore", "SCHEMA.md", "resources"];
const MAX_SOURCE_BYTES: u64 = 256 << 20;

#[derive(Debug, Error)]
pub enum ContentRecoveryError {
    #[error("content recovery repository error: {0}")]
    Repository(String),
    #[error("content recovery configuration error: {0}")]
    Configuration(String),
    #[error("content recovery remote error: {0}")]
    Remote(String),
    #[error("content recovery archive error: {0}")]
    Archive(String),
    #[error("content recovery destination error: {0}")]
    Destination(String),
    #[error("content recovery filesystem error: {0}")]
    Filesystem(String),
    #[error(
        "content recovery needs SILAN_STATS_SYNC_TOKEN in the process environment or project .env"
    )]
    MissingCredential,
}

#[derive(Debug, Clone)]
pub struct ContentSourceArchive {
    bytes: Vec<u8>,
    sha256: String,
}

impl ContentSourceArchive {
    /// Archive the committed public source at `HEAD` through Git, never the
    /// mutable working tree. Deployment's full-repository durability gate
    /// guarantees the projection and this source snapshot describe the same
    /// backed-up revision.
    pub fn from_repository(content_root: impl AsRef<Path>) -> Result<Self, ContentRecoveryError> {
        let repo = GitRepo::open(content_root)
            .map_err(|error| ContentRecoveryError::Repository(error.to_string()))?;
        let bytes = repo
            .archive("HEAD", SOURCE_PATHS)
            .map_err(|error| ContentRecoveryError::Repository(error.to_string()))?;
        validate_source_archive(&bytes)?;
        let sha256 = sha256_hex(&bytes);
        Ok(Self { bytes, sha256 })
    }

    pub fn from_bytes(bytes: Vec<u8>) -> Result<Self, ContentRecoveryError> {
        validate_source_archive(&bytes)?;
        let sha256 = sha256_hex(&bytes);
        Ok(Self { bytes, sha256 })
    }

    pub fn bytes(&self) -> &[u8] {
        &self.bytes
    }

    pub fn sha256(&self) -> &str {
        &self.sha256
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ContentRecoveryResult {
    pub deployed_commit: String,
    pub local_commit: String,
    pub destination: PathBuf,
    pub files_restored: usize,
    pub source_sha256: String,
}

pub struct ContentRecoveryClient {
    content_root: PathBuf,
    base_url: String,
    bearer_token: Option<String>,
}

impl ContentRecoveryClient {
    /// Open from the expected content path. The path itself may be absent;
    /// only its parent project configuration is needed to locate production.
    pub fn open(expected_content_root: impl AsRef<Path>) -> Result<Self, ContentRecoveryError> {
        let content_root = expected_content_root.as_ref().to_path_buf();
        let base_url = api_base_url(&content_root)
            .map_err(|error| ContentRecoveryError::Configuration(error.to_string()))?;
        let bearer_token = workspace_stats_sync_token(&content_root);
        Ok(Self {
            content_root,
            base_url,
            bearer_token,
        })
    }

    pub fn with_bearer_token(mut self, token: impl Into<String>) -> Self {
        let token = token.into();
        self.bearer_token = (!token.trim().is_empty()).then(|| token.trim().to_owned());
        self
    }

    pub fn recover(
        &self,
        destination: impl AsRef<Path>,
    ) -> Result<ContentRecoveryResult, ContentRecoveryError> {
        ensure_empty_destination(destination.as_ref())?;
        let token = self
            .bearer_token
            .as_ref()
            .ok_or(ContentRecoveryError::MissingCredential)?;
        let url = format!(
            "{}/api/v1/content/source",
            self.base_url.trim_end_matches('/')
        );
        let response = ureq::AgentBuilder::new()
            .timeout_connect(Duration::from_secs(5))
            .timeout_read(Duration::from_secs(300))
            .build()
            .get(&url)
            .set("Authorization", &format!("Bearer {token}"))
            .call()
            .map_err(|error| ContentRecoveryError::Remote(format!("{url}: {error}")))?;
        let deployed_commit = required_header(&response, "X-Silan-Content-Commit")?;
        let expected_sha256 = required_header(&response, "X-Silan-Source-SHA256")?;
        if !is_hex(&deployed_commit, 40) || !is_hex(&expected_sha256, 64) {
            return Err(ContentRecoveryError::Remote(
                "server returned invalid recovery provenance".to_owned(),
            ));
        }
        let mut bytes = Vec::new();
        response
            .into_reader()
            .take(MAX_SOURCE_BYTES + 1)
            .read_to_end(&mut bytes)
            .map_err(|error| ContentRecoveryError::Remote(error.to_string()))?;
        if bytes.len() as u64 > MAX_SOURCE_BYTES {
            return Err(ContentRecoveryError::Remote(format!(
                "source archive exceeds {MAX_SOURCE_BYTES} bytes"
            )));
        }
        let source = ContentSourceArchive::from_bytes(bytes)?;
        if source.sha256() != expected_sha256 {
            return Err(ContentRecoveryError::Archive(
                "source archive checksum does not match server provenance".to_owned(),
            ));
        }
        restore_source_archive(&source, destination.as_ref(), &deployed_commit)
    }

    pub fn recover_default(&self) -> Result<ContentRecoveryResult, ContentRecoveryError> {
        self.recover(&self.content_root)
    }
}

pub fn restore_source_archive(
    source: &ContentSourceArchive,
    destination: &Path,
    deployed_commit: &str,
) -> Result<ContentRecoveryResult, ContentRecoveryError> {
    if !is_hex(deployed_commit, 40) {
        return Err(ContentRecoveryError::Archive(
            "deployed commit must be a 40-character Git object id".to_owned(),
        ));
    }
    ensure_empty_destination(destination)?;
    let parent = destination.parent().ok_or_else(|| {
        ContentRecoveryError::Destination(format!(
            "{} has no parent directory",
            destination.display()
        ))
    })?;
    fs::create_dir_all(parent)
        .map_err(|error| ContentRecoveryError::Filesystem(error.to_string()))?;
    let staging = tempfile::Builder::new()
        .prefix(".silan-content-recovery-")
        .tempdir_in(parent)
        .map_err(|error| ContentRecoveryError::Filesystem(error.to_string()))?;
    extract_source_archive(source.bytes(), staging.path())?;
    let files_restored = regular_file_count(staging.path())?;
    let private_namespace = staging.path().join("agent");
    fs::create_dir_all(&private_namespace)
        .map_err(|error| ContentRecoveryError::Filesystem(error.to_string()))?;
    fs::write(private_namespace.join(".gitkeep"), [])
        .map_err(|error| ContentRecoveryError::Filesystem(error.to_string()))?;
    let repo =
        GitRepo::initialize_recovered(staging.path(), deployed_commit, AUTHOR_NAME, AUTHOR_EMAIL)
            .map_err(|error| ContentRecoveryError::Repository(error.to_string()))?;
    let local_commit = repo
        .rev_parse("HEAD")
        .map_err(|error| ContentRecoveryError::Repository(error.to_string()))?;
    if destination.exists() {
        fs::remove_dir(destination)
            .map_err(|error| ContentRecoveryError::Filesystem(error.to_string()))?;
    }
    fs::rename(staging.path(), destination).map_err(|error| {
        ContentRecoveryError::Filesystem(format!(
            "activate {} as {}: {error}",
            staging.path().display(),
            destination.display()
        ))
    })?;
    Ok(ContentRecoveryResult {
        deployed_commit: deployed_commit.to_owned(),
        local_commit,
        destination: destination.to_path_buf(),
        files_restored,
        source_sha256: source.sha256().to_owned(),
    })
}

fn validate_source_archive(bytes: &[u8]) -> Result<(), ContentRecoveryError> {
    let mut archive = Archive::new(Cursor::new(bytes));
    let mut has_schema = false;
    let mut has_resources = false;
    let entries = archive
        .entries()
        .map_err(|error| ContentRecoveryError::Archive(error.to_string()))?;
    for entry in entries {
        let entry = entry.map_err(|error| ContentRecoveryError::Archive(error.to_string()))?;
        let entry_type = entry.header().entry_type();
        if is_archive_metadata(entry_type) {
            continue;
        }
        let path = entry
            .path()
            .map_err(|error| ContentRecoveryError::Archive(error.to_string()))?;
        validate_source_path(&path)?;
        if !(entry_type.is_file() || entry_type.is_dir()) {
            return Err(ContentRecoveryError::Archive(format!(
                "unsupported source archive entry {}",
                path.display()
            )));
        }
        has_schema |= path == Path::new("SCHEMA.md");
        has_resources |= path == Path::new("resources") || path.starts_with("resources/");
    }
    if !has_schema || !has_resources {
        return Err(ContentRecoveryError::Archive(
            "source archive must contain SCHEMA.md and resources/".to_owned(),
        ));
    }
    Ok(())
}

fn extract_source_archive(bytes: &[u8], destination: &Path) -> Result<(), ContentRecoveryError> {
    validate_source_archive(bytes)?;
    let mut archive = Archive::new(Cursor::new(bytes));
    for entry in archive
        .entries()
        .map_err(|error| ContentRecoveryError::Archive(error.to_string()))?
    {
        let mut entry = entry.map_err(|error| ContentRecoveryError::Archive(error.to_string()))?;
        let entry_type = entry.header().entry_type();
        if is_archive_metadata(entry_type) {
            continue;
        }
        let path = entry
            .path()
            .map_err(|error| ContentRecoveryError::Archive(error.to_string()))?
            .into_owned();
        let target = destination.join(&path);
        if entry_type.is_dir() {
            fs::create_dir_all(&target)
                .map_err(|error| ContentRecoveryError::Filesystem(error.to_string()))?;
        } else {
            if let Some(parent) = target.parent() {
                fs::create_dir_all(parent)
                    .map_err(|error| ContentRecoveryError::Filesystem(error.to_string()))?;
            }
            entry
                .unpack(&target)
                .map_err(|error| ContentRecoveryError::Filesystem(error.to_string()))?;
        }
    }
    Ok(())
}

fn is_archive_metadata(entry_type: tar::EntryType) -> bool {
    entry_type.is_pax_global_extensions()
        || entry_type.is_pax_local_extensions()
        || entry_type.is_gnu_longname()
        || entry_type.is_gnu_longlink()
}

fn validate_source_path(path: &Path) -> Result<(), ContentRecoveryError> {
    if path.components().any(|component| {
        matches!(
            component,
            Component::ParentDir | Component::RootDir | Component::Prefix(_)
        )
    }) {
        return Err(ContentRecoveryError::Archive(format!(
            "unsafe source archive path {}",
            path.display()
        )));
    }
    let allowed = path == Path::new(".gitignore")
        || path == Path::new("SCHEMA.md")
        || path == Path::new("resources")
        || path.starts_with("resources/");
    if !allowed {
        return Err(ContentRecoveryError::Archive(format!(
            "source archive contains non-public path {}",
            path.display()
        )));
    }
    Ok(())
}

fn ensure_empty_destination(destination: &Path) -> Result<(), ContentRecoveryError> {
    if !destination.exists() {
        return Ok(());
    }
    if !destination.is_dir() {
        return Err(ContentRecoveryError::Destination(format!(
            "{} is not a directory",
            destination.display()
        )));
    }
    let mut entries = fs::read_dir(destination)
        .map_err(|error| ContentRecoveryError::Filesystem(error.to_string()))?;
    if entries.next().is_some() {
        return Err(ContentRecoveryError::Destination(format!(
            "{} is not empty",
            destination.display()
        )));
    }
    Ok(())
}

fn regular_file_count(root: &Path) -> Result<usize, ContentRecoveryError> {
    fn visit(path: &Path, count: &mut usize) -> std::io::Result<()> {
        for entry in fs::read_dir(path)? {
            let entry = entry?;
            if entry.file_type()?.is_dir() {
                visit(&entry.path(), count)?;
            } else if entry.file_type()?.is_file() {
                *count += 1;
            }
        }
        Ok(())
    }
    let mut count = 0;
    visit(root, &mut count).map_err(|error| ContentRecoveryError::Filesystem(error.to_string()))?;
    Ok(count)
}

fn required_header(response: &ureq::Response, name: &str) -> Result<String, ContentRecoveryError> {
    response
        .header(name)
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .map(ToOwned::to_owned)
        .ok_or_else(|| ContentRecoveryError::Remote(format!("response is missing {name}")))
}

fn sha256_hex(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

fn is_hex(value: &str, len: usize) -> bool {
    value.len() == len && value.bytes().all(|byte| byte.is_ascii_hexdigit())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use std::process::Command;

    fn git(root: &Path, args: &[&str]) {
        let status = Command::new("git")
            .args(args)
            .current_dir(root)
            .status()
            .expect("git");
        assert!(status.success());
    }

    fn source_fixture() -> (tempfile::TempDir, ContentSourceArchive, String) {
        let root = tempfile::tempdir().expect("tempdir");
        fs::create_dir_all(root.path().join("resources/blog/post")).expect("resources");
        fs::write(root.path().join("SCHEMA.md"), "schema\n").expect("schema");
        fs::write(root.path().join(".gitignore"), "*.db\n").expect("gitignore");
        fs::write(root.path().join("resources/blog/post/en.md"), "body\n").expect("body");
        fs::create_dir_all(root.path().join("agent/notes")).expect("agent");
        fs::write(root.path().join("agent/notes/private.md"), "secret\n").expect("private");
        git(root.path(), &["init", "-q", "-b", "main"]);
        git(root.path(), &["add", "-A"]);
        git(
            root.path(),
            &[
                "-c",
                "user.name=Silan.Hu",
                "-c",
                "user.email=silan.hu@u.nus.edu",
                "commit",
                "-q",
                "-m",
                "fixture",
            ],
        );
        let commit = GitRepo::open(root.path())
            .expect("repo")
            .rev_parse("HEAD")
            .expect("head");
        let source = ContentSourceArchive::from_repository(root.path()).expect("archive");
        (root, source, commit)
    }

    #[test]
    fn source_snapshot_excludes_private_agent_namespace() {
        let (_root, source, _commit) = source_fixture();
        let mut archive = Archive::new(Cursor::new(source.bytes()));
        let paths = archive
            .entries()
            .expect("entries")
            .map(|entry| entry.expect("entry").path().expect("path").into_owned())
            .collect::<Vec<_>>();
        assert!(paths.iter().any(|path| path == Path::new("SCHEMA.md")));
        assert!(!paths.iter().any(|path| path.starts_with("agent")));
    }

    #[test]
    fn recovery_is_atomic_and_initializes_a_new_repository() {
        let (_root, source, deployed_commit) = source_fixture();
        let parent = tempfile::tempdir().expect("destination parent");
        let destination = parent.path().join("content");
        fs::create_dir(&destination).expect("empty destination");
        let result = restore_source_archive(&source, &destination, &deployed_commit)
            .expect("recover source");
        assert_eq!(result.deployed_commit, deployed_commit);
        assert!(destination.join("SCHEMA.md").is_file());
        assert!(destination.join("resources/blog/post/en.md").is_file());
        assert!(destination.join("agent/.gitkeep").is_file());
        assert!(destination.join(".git").is_dir());
        assert_eq!(
            GitRepo::open(&destination)
                .expect("repo")
                .rev_parse("HEAD")
                .expect("head"),
            result.local_commit
        );
    }

    #[test]
    fn source_archive_rejects_paths_outside_public_source() {
        let mut bytes = Vec::new();
        {
            let mut archive = tar::Builder::new(&mut bytes);
            let payload = b"private\n";
            let mut header = tar::Header::new_gnu();
            header.set_size(payload.len() as u64);
            header.set_mode(0o600);
            header.set_cksum();
            archive
                .append_data(&mut header, "agent/notes/private.md", &payload[..])
                .expect("append");
            archive.finish().expect("finish");
        }
        assert!(matches!(
            ContentSourceArchive::from_bytes(bytes),
            Err(ContentRecoveryError::Archive(_))
        ));
    }

    #[test]
    fn recovery_refuses_a_non_empty_destination() {
        let (_root, source, deployed_commit) = source_fixture();
        let parent = tempfile::tempdir().expect("destination parent");
        let destination = parent.path().join("content");
        fs::create_dir(&destination).expect("destination");
        fs::File::create(destination.join("keep.txt"))
            .expect("keep")
            .write_all(b"keep")
            .expect("write");
        assert!(matches!(
            restore_source_archive(&source, &destination, &deployed_commit),
            Err(ContentRecoveryError::Destination(_))
        ));
        assert_eq!(
            fs::read(destination.join("keep.txt")).expect("keep"),
            b"keep"
        );
    }
}
