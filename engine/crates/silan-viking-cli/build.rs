use std::env;
use std::path::{Path, PathBuf};
use std::process::Command;

const BUILD_VERSION_ENV: &str = "SILAN_BUILD_VERSION";

fn main() {
    let manifest_dir = PathBuf::from(
        env::var_os("CARGO_MANIFEST_DIR").expect("Cargo must provide CARGO_MANIFEST_DIR"),
    );
    let repository = manifest_dir
        .join("../../..")
        .canonicalize()
        .expect("CLI crate must remain inside the Silan Viking repository");

    println!("cargo:rerun-if-env-changed={BUILD_VERSION_ENV}");
    println!(
        "cargo:rerun-if-changed={}",
        repository.join(".tidemark.toml").display()
    );
    watch_git_state(&repository);

    let version = env::var(BUILD_VERSION_ENV).unwrap_or_else(|_| resolve_tide(&repository));
    validate_coordinate(&version);
    println!("cargo:rustc-env={BUILD_VERSION_ENV}={version}");
}

fn resolve_tide(repository: &Path) -> String {
    let output = Command::new("tide")
        .arg("mark")
        .current_dir(repository)
        .output()
        .unwrap_or_else(|error| {
            panic!("TideMark is required to build silan-viking; could not run `tide mark`: {error}")
        });
    if !output.status.success() {
        panic!(
            "`tide mark` failed: {}",
            String::from_utf8_lossy(&output.stderr).trim()
        );
    }
    String::from_utf8(output.stdout)
        .expect("TideMark output must be UTF-8")
        .trim()
        .to_owned()
}

fn validate_coordinate(version: &str) {
    let mut segments = version.split('.');
    let numeric_prefix_is_valid = (0..3).all(|_| {
        segments.next().is_some_and(|segment| {
            !segment.is_empty() && segment.chars().all(|c| c.is_ascii_digit())
        })
    });
    let metadata_is_valid = segments.all(|segment| {
        !segment.is_empty()
            && segment
                .chars()
                .all(|c| c.is_ascii_alphanumeric() || c == '-')
    });
    assert!(
        numeric_prefix_is_valid && metadata_is_valid,
        "invalid TideMark coordinate: {version}"
    );
}

fn watch_git_state(repository: &Path) {
    for relative in [".git/HEAD", ".git/logs/HEAD", ".git/packed-refs"] {
        let path = repository.join(relative);
        if path.exists() {
            println!("cargo:rerun-if-changed={}", path.display());
        }
    }
}
