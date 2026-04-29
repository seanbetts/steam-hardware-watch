#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
LOCAL_DIR="$REPO_DIR/.local"

PROFILE_DIR="${1:-${STEAMDB_PROFILE_DIR:-$LOCAL_DIR/playwright-steamdb-profile}}"
ENV_FILE="${STEAMDB_ENV_FILE:-$LOCAL_DIR/steamdb-env.sh}"

pids="$(ps aux | awk -v profile="$PROFILE_DIR" '
  index($0, profile) && !index($0, "awk -v profile=") {
    print $2
  }
')"

if [ -n "$pids" ]; then
  for pid in $pids; do
    kill "$pid" 2>/dev/null || true
  done
  printf '%s\n' "Closed dedicated SteamDB browser/profile processes for $PROFILE_DIR."
else
  printf '%s\n' "No dedicated SteamDB browser/profile processes found for $PROFILE_DIR."
fi

rm -f \
  "$PROFILE_DIR/SingletonLock" \
  "$PROFILE_DIR/SingletonSocket" \
  "$PROFILE_DIR/SingletonCookie"

if [ -f "$ENV_FILE" ]; then
  rm -f "$ENV_FILE"
  printf '%s\n' "Removed $ENV_FILE"
fi
