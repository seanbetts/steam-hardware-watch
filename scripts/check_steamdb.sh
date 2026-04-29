#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 RUN_DIR" >&2
  exit 1
fi

RUN_DIR="$1"
OUT_DIR="$RUN_DIR/api/steamdb"
REPORT_DIR="$RUN_DIR/reports"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
mkdir -p "$OUT_DIR" "$REPORT_DIR"

ERROR_FILE="$REPORT_DIR/steamdb-errors.txt"
: > "$ERROR_FILE"
: > "$REPORT_DIR/steamdb-key-lines.txt"

load_local_env() {
  env_file="${STEAMDB_ENV_FILE:-$REPO_DIR/.local/steamdb-env.sh}"
  if [ -f "$env_file" ]; then
    # shellcheck disable=SC1090
    . "$env_file"
  fi
}

maybe_set_cdp_endpoint() {
  if [ -n "${STEAMDB_CDP_ENDPOINT:-}" ] || [ -z "${STEAMDB_PROFILE_DIR:-}" ]; then
    return 0
  fi

  port="$(ps aux | awk -v profile="$STEAMDB_PROFILE_DIR" '
    index($0, profile) && match($0, /--remote-debugging-port=([0-9]+)/) {
      value = substr($0, RSTART, RLENGTH)
      sub(/^--remote-debugging-port=/, "", value)
      print value
      exit
    }
  ' 2>/dev/null || true)"

  if [ -n "$port" ]; then
    STEAMDB_CDP_ENDPOINT="http://127.0.0.1:$port"
    export STEAMDB_CDP_ENDPOINT
  fi
}

is_challenge_page() {
  path="$1"
  rg -qi "Checking your browser|Just a moment|Cloudflare|cf-chl|cf-browser-verification" "$path"
}

load_local_env

STEAMDB_USER_AGENT="${STEAMDB_USER_AGENT:-Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36}"
export STEAMDB_USER_AGENT

fetch_html() {
  name="$1"
  url="$2"
  tmp="$OUT_DIR/$name.html.tmp"
  out="$OUT_DIR/$name.html"

  if curl -A "$STEAMDB_USER_AGENT" \
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' \
    -H 'Accept-Language: en-US,en;q=0.9' \
    -H 'Upgrade-Insecure-Requests: 1' \
    --compressed \
    --retry 2 --retry-delay 2 --max-time 45 -fsSL "$url" > "$tmp" 2>/dev/null; then
    if ! is_challenge_page "$tmp"; then
      mv "$tmp" "$out"
      return 0
    fi
  fi

  if [ "${STEAMDB_PLAYWRIGHT_FALLBACK:-0}" = "1" ] && command -v node >/dev/null 2>&1; then
    maybe_set_cdp_endpoint
    if node "$SCRIPT_DIR/fetch_steamdb_with_playwright.js" "$url" "$tmp" >/dev/null 2>&1 \
      && [ -s "$tmp" ] \
      && ! is_challenge_page "$tmp"; then
      mv "$tmp" "$out"
      return 0
    fi
  fi

  rm -f "$tmp" "$out"
  printf '%s\n' "failed to fetch $url: blocked or challenge page" >> "$ERROR_FILE"
  return 1
}

fetch_html "controller-app" "https://steamdb.info/app/4165870/" || true
fetch_html "controller-history" "https://steamdb.info/app/4165870/history/" || true
fetch_html "controller-unboxing-app" "https://steamdb.info/app/4653940/" || true
fetch_html "controller-unboxing-package" "https://steamdb.info/sub/1620489/" || true

rg -n "Coming soon|released|ownersonly|free on demand|unboxing|package|depot|video" \
  "$OUT_DIR" \
  > "$REPORT_DIR/steamdb-key-lines.txt" || true

printf '%s\n' \
  "Saved SteamDB pages to $OUT_DIR" \
  "Saved matching lines to $REPORT_DIR/steamdb-key-lines.txt"
