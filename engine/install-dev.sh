#!/usr/bin/env bash
#
# install-dev.sh — compile and install the current silan-viking engine checkout.
#
# This is the canonical engine-only installer for contributors. It builds the
# CLI from the current source tree, verifies it before activation, atomically
# replaces the installed binary, creates the `silan` / `svk` aliases, and
# records an installation receipt containing the source revision and SHA-256.
#
# Usage:
#   engine/install-dev.sh
#   engine/install-dev.sh --prefix DIR
#   engine/install-dev.sh --debug
#   engine/install-dev.sh --skip-tests
#   engine/install-dev.sh --state-dir DIR
#
# End users who want a published release should use engine/install.sh instead.
# The full CLI + Desktop installer is packaging/release/dev-install-local.sh.
#
# Author: Silan.Hu <silan.hu@u.nus.edu>
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
engine_root="$script_dir"

install_dir="${SILAN_INSTALL_DIR:-$HOME/.local/bin}"
state_dir="${SILAN_VIKING_STATE_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/silan-viking}"
profile="release"
run_tests=1

usage() {
    sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

die() {
    echo "install-dev.sh: $*" >&2
    exit 1
}

have() {
    command -v "$1" >/dev/null 2>&1
}

sha256_file() {
    if have shasum; then
        shasum -a 256 "$1" | awk '{print $1}'
    elif have sha256sum; then
        sha256sum "$1" | awk '{print $1}'
    else
        die "need shasum or sha256sum to verify the installed binary"
    fi
}

install_alias() {
    alias_name="$1"
    alias_path="$install_dir/$alias_name"
    if [ -e "$alias_path" ] && [ ! -L "$alias_path" ]; then
        die "refusing to replace non-symlink alias: $alias_path"
    fi
    ln -sfn "silan-viking" "$alias_path"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --prefix)
            shift
            [ $# -gt 0 ] || die "--prefix needs a directory"
            install_dir="$1"
            ;;
        --state-dir)
            shift
            [ $# -gt 0 ] || die "--state-dir needs a directory"
            state_dir="$1"
            ;;
        --debug)
            profile="debug"
            ;;
        --release)
            profile="release"
            ;;
        --skip-tests)
            run_tests=0
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            die "unknown argument: $1 (run with --help for usage)"
            ;;
    esac
    shift
done

have cargo || die "cargo is required (install Rust from https://rustup.rs)"
have rustc || die "rustc is required (install Rust from https://rustup.rs)"
have install || die "the POSIX install command is required"
have tide || die "tide is required to resolve the project build version"

project_version="$("$repo_root/scripts/tide-version.sh")"
export SILAN_BUILD_VERSION="$project_version"

source_revision="unknown"
source_state="not-a-git-checkout"
if have git && git -C "$repo_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    source_revision="$(git -C "$repo_root" rev-parse HEAD)"
    source_state="clean"
    if [ -n "$(git -C "$repo_root" status --porcelain --untracked-files=all -- \
        engine/Cargo.toml engine/Cargo.lock engine/crates)" ]; then
        source_state="modified"
    fi
fi

if [ "$run_tests" -eq 1 ]; then
    echo "==> [1/4] test the complete silan-viking engine workspace"
    cargo test --locked --manifest-path "$engine_root/Cargo.toml" --workspace
    build_step=2
    install_step=3
    verify_step=4
    total_steps=4
else
    echo "==> tests skipped by explicit --skip-tests"
    build_step=1
    install_step=2
    verify_step=3
    total_steps=3
fi

echo "==> [$build_step/$total_steps] build current engine source ($profile)"
build_args=(
    build
    --locked
    --manifest-path "$engine_root/Cargo.toml"
    -p silan-viking-cli
)
if [ "$profile" = "release" ]; then
    build_args+=(--release)
fi
cargo "${build_args[@]}"

built_bin="$engine_root/target/$profile/silan-viking"
[ -x "$built_bin" ] || die "build succeeded but binary is missing: $built_bin"
built_version="$("$built_bin" --version)"
expected_version="silan-viking $project_version"
[ "$built_version" = "$expected_version" ] \
    || die "compiled CLI reports $built_version; TideMark requires $expected_version"
"$built_bin" --help >/dev/null
built_sha256="$(sha256_file "$built_bin")"

echo "==> [$install_step/$total_steps] atomically install engine to $install_dir"
mkdir -p "$install_dir" "$state_dir"
staged_bin="$install_dir/.silan-viking.new.$$"
staged_receipt="$state_dir/.install-receipt.new.$$"
cleanup() {
    rm -f "$staged_bin" "$staged_receipt"
}
trap cleanup EXIT HUP INT TERM

install -m 755 "$built_bin" "$staged_bin"
staged_sha256="$(sha256_file "$staged_bin")"
[ "$staged_sha256" = "$built_sha256" ] \
    || die "staged binary checksum differs from the compiled artifact"
"$staged_bin" --version >/dev/null
mv -f "$staged_bin" "$install_dir/silan-viking"
install_alias silan
install_alias svk

echo "==> [$verify_step/$total_steps] verify installation and write provenance receipt"
installed_bin="$install_dir/silan-viking"
installed_sha256="$(sha256_file "$installed_bin")"
[ "$installed_sha256" = "$built_sha256" ] \
    || die "installed binary checksum differs from the compiled artifact"
installed_version="$("$installed_bin" --version)"
[ "$installed_version" = "$built_version" ] \
    || die "installed version differs from the compiled artifact"

installed_at="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
{
    printf 'format=1\n'
    printf 'installed_at=%s\n' "$installed_at"
    printf 'source_root=%s\n' "$repo_root"
    printf 'source_revision=%s\n' "$source_revision"
    printf 'source_state=%s\n' "$source_state"
    printf 'profile=%s\n' "$profile"
    printf 'tide_version=%s\n' "$project_version"
    printf 'version=%s\n' "$installed_version"
    printf 'binary=%s\n' "$installed_bin"
    printf 'sha256=%s\n' "$installed_sha256"
    printf 'rustc=%s\n' "$(rustc --version)"
} > "$staged_receipt"
mv -f "$staged_receipt" "$state_dir/install-receipt"

trap - EXIT HUP INT TERM

echo
echo "  ✓ installed current source build"
echo "    version:  $installed_version"
echo "    tide:     $project_version"
echo "    source:   $source_revision ($source_state)"
echo "    sha256:   $installed_sha256"
echo "    commands: $install_dir/{silan,svk,silan-viking}"
echo "    receipt:  $state_dir/install-receipt"

case ":${PATH}:" in
    *":${install_dir}:"*)
        echo "    next:     silan guide"
        ;;
    *)
        echo
        echo "  $install_dir is not on PATH. Add this to your shell profile:"
        echo "    export PATH=\"$install_dir:\$PATH\""
        ;;
esac
