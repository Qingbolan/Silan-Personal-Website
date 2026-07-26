#!/usr/bin/env bash
set -euo pipefail

mode="${1:-}"
case "$mode" in
  prepare|publish) ;;
  *)
    echo "usage: server-publish.sh prepare|publish" >&2
    exit 64
    ;;
esac

: "${SILAN_FRONTEND_STATE_ROOT:?SILAN_FRONTEND_STATE_ROOT is required}"
: "${SILAN_PUBLIC_ORIGIN:?SILAN_PUBLIC_ORIGIN is required}"

source_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
state_root="$SILAN_FRONTEND_STATE_ROOT"
published_root="$state_root/published"
releases_root="$published_root/releases"
current_link="$published_root/current"
previous_link="$published_root/previous"
puppeteer_cache="$state_root/cache/puppeteer"
dependency_marker="$state_root/dependencies.sha256"

mkdir -p "$state_root/cache" "$published_root" "$releases_root" "$puppeteer_cache"
exec 9>"$published_root/.publish.lock"
if ! flock -w 240 9; then
  echo "[frontend:server] another static publication is still running" >&2
  exit 75
fi

prepare_dependencies() {
  local lock_hash installed_hash
  lock_hash="$(
    sha256sum "$source_root/package.json" "$source_root/package-lock.json" \
      | sha256sum \
      | awk '{print $1}'
  )"
  installed_hash=""
  if [[ -f "$dependency_marker" ]]; then
    installed_hash="$(tr -d '[:space:]' < "$dependency_marker")"
  fi

  if [[ "$installed_hash" == "$lock_hash" && -x "$source_root/node_modules/.bin/vite" ]]; then
    echo "[frontend:server] dependencies unchanged"
    return
  fi

  echo "[frontend:server] npm ci"
  (
    cd "$source_root"
    PUPPETEER_CACHE_DIR="$puppeteer_cache" npm ci --no-audit --no-fund
    PUPPETEER_CACHE_DIR="$puppeteer_cache" \
      npx --no-install puppeteer browsers install chrome --install-deps
  )
  printf '%s\n' "$lock_hash" > "$dependency_marker.next"
  mv -f "$dependency_marker.next" "$dependency_marker"
}

prepare_dependencies
if [[ "$mode" == "prepare" ]]; then
  echo "[frontend:server] build environment ready"
  exit 0
fi

if [[ -r /etc/silan-backend/db.env ]]; then
  set -a
  # shellcheck disable=SC1091
  . /etc/silan-backend/db.env
  set +a
fi

export PUPPETEER_CACHE_DIR="$puppeteer_cache"
export PRERENDER_START_LOCAL_BACKEND=false
export VITE_API_ORIGIN="$SILAN_PUBLIC_ORIGIN"
export VITE_PUBLIC_ORIGIN="$SILAN_PUBLIC_ORIGIN"
export VITE_GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID:-}"

echo "[frontend:server] build:seo against $SILAN_PUBLIC_ORIGIN"
(
  cd "$source_root"
  npm run build:seo
)

dist="$source_root/dist"
test -s "$dist/index.html"
test -s "$dist/zh/blog/index.html"
test -s "$dist/sitemap.xml"
grep -q "Silan Hu" "$dist/index.html"
grep -q "GEM-Bench" "$dist/index.html"
grep -q "AI 回答里加了广告" "$dist/zh/blog/index.html"
if grep -q '"blogList"' "$dist/zh/blog/index.html"; then
  echo "[frontend:server] list page contains a serialized runtime snapshot" >&2
  exit 1
fi

release_id="$(date -u +%Y%m%dT%H%M%SZ)-$$"
next_release="$releases_root/.${release_id}.next"
release="$releases_root/$release_id"
next_current="$published_root/.current.next"
next_previous="$published_root/.previous.next"

rm -rf "$next_release"
rm -f "$next_current" "$next_previous"
mkdir -p "$next_release"
rsync -a --delete "$dist/" "$next_release/"
if [[ "$(id -u)" -eq 0 ]]; then
  chown -R www:www "$dist"
  chown -R www:www "$next_release"
fi
mv "$next_release" "$release"

if [[ -L "$current_link" ]]; then
  current_release="$(readlink -f "$current_link")"
  ln -s "$current_release" "$next_previous"
  mv -Tf "$next_previous" "$previous_link"
fi

ln -s "$release" "$next_current"
mv -Tf "$next_current" "$current_link"

mapfile -t stale_releases < <(find "$releases_root" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' \
  | sort -rn \
  | tail -n +4 \
  | cut -d' ' -f2-)
for stale_release in "${stale_releases[@]}"; do
  [[ "$stale_release" == "$release" ]] || rm -rf "$stale_release"
done

echo "[frontend:server] release=$release"
