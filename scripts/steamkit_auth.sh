#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$REPO_DIR/tools/steamkit-pics"
ENV_FILE="${STEAMKIT_ENV_FILE:-$REPO_DIR/.local/steamkit-env.sh}"
SESSION_FILE="${STEAMKIT_SESSION_FILE:-$REPO_DIR/.local/steamkit-session.json}"

if [ -f "$ENV_FILE" ]; then
  printf '%s\n' "Loading SteamKit environment from $ENV_FILE" >&2
  # shellcheck disable=SC1090
  . "$ENV_FILE"
fi

if [ -z "${STEAMKIT_USERNAME:-}" ] || [ -z "${STEAMKIT_PASSWORD:-}" ]; then
  echo "STEAMKIT_USERNAME and STEAMKIT_PASSWORD are required in $ENV_FILE or the environment" >&2
  exit 1
fi

export STEAMKIT_USERNAME STEAMKIT_PASSWORD
if [ -n "${STEAMKIT_AUTH_CODE:-}" ]; then
  export STEAMKIT_AUTH_CODE
fi
if [ -n "${STEAMKIT_TWO_FACTOR_CODE:-}" ]; then
  export STEAMKIT_TWO_FACTOR_CODE
fi
if [ -n "${STEAMKIT_ACCEPT_MOBILE_CONFIRMATION:-}" ]; then
  export STEAMKIT_ACCEPT_MOBILE_CONFIRMATION
fi
if [ -n "${STEAMKIT_TIMEOUT_SECONDS:-}" ]; then
  export STEAMKIT_TIMEOUT_SECONDS
fi

mkdir -p "$(dirname "$SESSION_FILE")"

printf '%s\n' "Starting SteamKit auth bootstrap. Waiting for Steam to request any required Guard confirmation..." >&2
dotnet run --project "$PROJECT_DIR" -- --auth-session-out "$SESSION_FILE" --session-file "$SESSION_FILE"
chmod 600 "$SESSION_FILE"
printf '%s\n' "Saved SteamKit session to $SESSION_FILE"
