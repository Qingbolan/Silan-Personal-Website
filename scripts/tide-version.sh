#!/usr/bin/env bash
# Resolve the canonical Silan Viking build coordinate through TideMark.
# Every component build calls this boundary instead of reading or incrementing
# package manifests independently.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

command -v tide >/dev/null 2>&1 || {
    echo "tide-version.sh: tide is required (https://github.com/Qingbolan/TideMark)" >&2
    exit 1
}

cd "$repo_root"
for argument in "$@"; do
    if [ "$argument" = "--explain" ]; then
        exec tide mark "$@"
    fi
done
version="$(tide mark "$@")"
if ! printf '%s\n' "$version" \
    | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+(\.[0-9A-Za-z-]+)*$'; then
    echo "tide-version.sh: invalid TideMark coordinate: $version" >&2
    exit 1
fi
printf '%s\n' "$version"
