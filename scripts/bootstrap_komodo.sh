#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
LOCAL_DIR="$REPO_DIR/.local"

PROFILE_DIR="${1:-${KOMODO_PROFILE_DIR:-$LOCAL_DIR/playwright-komodo-profile}}"
PORT="${2:-${KOMODO_CDP_PORT:-55684}}"
URL="${KOMODO_BOOTSTRAP_URL:-https://komodostation.com/product/steam-controller_jpy/}"
ENV_FILE="${KOMODO_ENV_FILE:-$LOCAL_DIR/komodo-env.sh}"

mkdir -p "$PROFILE_DIR" "$LOCAL_DIR"

existing_pid="$(ps aux | awk -v profile="$PROFILE_DIR" -v port="$PORT" '
  index($0, "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome") &&
  index($0, profile) &&
  index($0, "--remote-debugging-port=" port) {
    print $2
    exit
  }
')"

if [ -z "$existing_pid" ]; then
  open -g -na "Google Chrome" --args \
    "--user-data-dir=$PROFILE_DIR" \
    "--remote-debugging-port=$PORT" \
    --no-first-run \
    --disable-sync \
    --new-window \
    "$URL"

  attempts=0
  until curl -fsS "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; do
    attempts=$((attempts + 1))
    if [ "$attempts" -ge 30 ]; then
      echo "failed to observe a Chrome CDP endpoint on port $PORT" >&2
      exit 1
    fi
    sleep 1
  done
else
  echo "Komodo bootstrap browser already running on port $PORT (pid $existing_pid)."
fi

cat > "$ENV_FILE" <<EOF
export KOMODO_PLAYWRIGHT_FALLBACK=1
export PLAYWRIGHT_PROFILE_DIR="$PROFILE_DIR"
export PLAYWRIGHT_CDP_ENDPOINT="http://127.0.0.1:$PORT"
export PLAYWRIGHT_BROWSER_CHANNEL="chrome"
export PLAYWRIGHT_REFERER="https://komodostation.com/product/steam-controller_jpy/"
EOF

printf '%s\n' "Komodo browser bootstrap ready."
printf '%s\n' "Profile: $PROFILE_DIR"
printf '%s\n' "CDP endpoint: http://127.0.0.1:$PORT"
printf '%s\n' "Env file: $ENV_FILE"
printf '%s\n' ""
printf '%s\n' "Next steps:"
printf '%s\n' "1. If Komodo needs any manual interaction, switch to the dedicated Chrome window when convenient."
printf '%s\n' "2. Leave that dedicated browser running in the background."
printf '%s\n' "3. Source the env file before a run, or let check_komodo.sh pick it up automatically."
