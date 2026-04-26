#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 RUN_DIR" >&2
  exit 1
fi

RUN_DIR="$1"
OUT_DIR="$RUN_DIR/api/komodo"
REPORT_DIR="$RUN_DIR/reports"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
mkdir -p "$OUT_DIR" "$REPORT_DIR"

ERROR_FILE="$REPORT_DIR/komodo-errors.txt"

: > "$REPORT_DIR/komodo-product-modified.tsv"
: > "$REPORT_DIR/komodo-controller-sections.tsv"
: > "$REPORT_DIR/komodo-machine-sections.tsv"
: > "$REPORT_DIR/komodo-frame-sections.tsv"
: > "$REPORT_DIR/komodo-controller-media-interesting.tsv"
: > "$REPORT_DIR/komodo-machine-media.tsv"
: > "$REPORT_DIR/komodo-frame-media.tsv"
: > "$REPORT_DIR/komodo-visual-assets.tsv"
: > "$ERROR_FILE"

load_local_env() {
  env_file="${KOMODO_ENV_FILE:-$REPO_DIR/.local/komodo-env.sh}"
  if [ -f "$env_file" ]; then
    # shellcheck disable=SC1090
    . "$env_file"
  fi
}

maybe_set_cdp_endpoint() {
  if [ -n "${PLAYWRIGHT_CDP_ENDPOINT:-}" ] || [ -z "${PLAYWRIGHT_PROFILE_DIR:-}" ]; then
    return 0
  fi

  port="$(ps aux | awk -v profile="$PLAYWRIGHT_PROFILE_DIR" '
    index($0, profile) && match($0, /--remote-debugging-port=([0-9]+)/) {
      value = substr($0, RSTART, RLENGTH)
      sub(/^--remote-debugging-port=/, "", value)
      print value
      exit
    }
  ' 2>/dev/null || true)"

  if [ -n "$port" ]; then
    PLAYWRIGHT_CDP_ENDPOINT="http://127.0.0.1:$port"
    export PLAYWRIGHT_CDP_ENDPOINT
  fi
}

load_local_env

fetch_json() {
  name="$1"
  url="$2"
  allow_fallback="${3:-1}"
  tmp="$OUT_DIR/$name.json.tmp"
  if curl -A 'Mozilla/5.0' --retry 1 --retry-delay 1 --max-time 12 -fsSL "$url" > "$tmp" 2>/dev/null \
    && jq empty "$tmp" >/dev/null 2>&1; then
    mv "$tmp" "$OUT_DIR/$name.json"
    return 0
  fi

  rm -f "$tmp"

  if [ "$allow_fallback" = "1" ] && [ "${KOMODO_PLAYWRIGHT_FALLBACK:-0}" = "1" ] && command -v playwright-cli >/dev/null 2>&1; then
    maybe_set_cdp_endpoint
    PLAYWRIGHT_CLI_BIN="$(command -v playwright-cli)"
    PLAYWRIGHT_CORE_PATH="$(CDPATH= cd -- "$(dirname "$PLAYWRIGHT_CLI_BIN")/../lib/node_modules/@playwright/cli/node_modules/playwright-core" && pwd 2>/dev/null || true)"
    PLAYWRIGHT_CORE_PATH="$PLAYWRIGHT_CORE_PATH" node "$SCRIPT_DIR/fetch_with_playwright.js" "$url" "$tmp"
    if jq empty "$tmp" >/dev/null 2>&1; then
      mv "$tmp" "$OUT_DIR/$name.json"
      return 0
    fi
  fi

  rm -f "$tmp"
  printf '%s\n' "failed to fetch JSON from $url" >> "$ERROR_FILE"
  return 1
}

if ! fetch_json "wp-json-root" "https://komodostation.com/wp-json/"; then
  printf '%s\n' "Komodo API unavailable or blocked; leaving Komodo reports empty." >> "$ERROR_FILE"
  printf '%s\n' "Komodo fetch blocked; see $ERROR_FILE"
  exit 0
fi

if ! fetch_json "product-controller-jpy" "https://komodostation.com/wp-json/wp/v2/product/413763"; then
  printf '%s\n' "Komodo product fetch blocked; leaving Komodo reports empty." >> "$ERROR_FILE"
  printf '%s\n' "Komodo fetch blocked; see $ERROR_FILE"
  exit 0
fi

fetch_json "product-machine-jpy" "https://komodostation.com/wp-json/wp/v2/product/413772" 0 || true
fetch_json "product-frame-jpy" "https://komodostation.com/wp-json/wp/v2/product/413776" 0 || true

fetch_json "sections-controller-search" "https://komodostation.com/wp-json/wp/v2/sections?search=Steam%20Controller&per_page=100" || true
fetch_json "sections-machine-search" "https://komodostation.com/wp-json/wp/v2/sections?search=Steam%20Machine&per_page=100" 0 || true
fetch_json "sections-frame-search" "https://komodostation.com/wp-json/wp/v2/sections?search=Steam%20Frame&per_page=100" 0 || true

fetch_json "media-controller-search" "https://komodostation.com/wp-json/wp/v2/media?search=Steam%20Controller&per_page=100" || true
fetch_json "media-parent-product-controller" "https://komodostation.com/wp-json/wp/v2/media?parent=413763&per_page=100" || true

for id in $(jq -r '.[].id' "$OUT_DIR/sections-controller-search.json" 2>/dev/null || true); do
  fetch_json "media-parent-section-$id" "https://komodostation.com/wp-json/wp/v2/media?parent=$id&per_page=100" || true
done

{
  printf 'controller\t%s\n' "$(jq -r '.modified // "n/a"' "$OUT_DIR/product-controller-jpy.json" 2>/dev/null || printf 'n/a')"
  printf 'machine\t%s\n' "$(jq -r '.modified // "n/a"' "$OUT_DIR/product-machine-jpy.json" 2>/dev/null || printf 'n/a')"
  printf 'frame\t%s\n' "$(jq -r '.modified // "n/a"' "$OUT_DIR/product-frame-jpy.json" 2>/dev/null || printf 'n/a')"
} > "$REPORT_DIR/komodo-product-modified.tsv"

jq -r '.[]? | [.id,.date,.modified,.slug,.title.rendered] | @tsv' \
  "$OUT_DIR/sections-controller-search.json" \
  > "$REPORT_DIR/komodo-controller-sections.tsv"

jq -r '.[]? | [.id,.date,.modified,.slug,.title.rendered] | @tsv' \
  "$OUT_DIR/sections-machine-search.json" \
  > "$REPORT_DIR/komodo-machine-sections.tsv"

jq -r '.[]? | [.id,.date,.modified,.slug,.title.rendered] | @tsv' \
  "$OUT_DIR/sections-frame-search.json" \
  > "$REPORT_DIR/komodo-frame-sections.tsv"

jq -r '
  .[]?
  | select((.source_url + " " + .slug + " " + .title.rendered) | test("2026/|webm|mp4|avif|spec|manual"; "i"))
  | [.id,.date,.modified,.slug,.mime_type,.post,.source_url]
  | @tsv
' "$OUT_DIR/media-controller-search.json" > "$REPORT_DIR/komodo-controller-media-interesting.tsv"

: > "$REPORT_DIR/komodo-machine-media.tsv"
: > "$REPORT_DIR/komodo-frame-media.tsv"

jq -r '
  .[]?
  | select((.mime_type | startswith("image/")) or (.mime_type | startswith("video/")))
  | [.id,.mime_type,.source_url]
  | @tsv
' "$OUT_DIR"/media-*.json "$OUT_DIR"/media-parent-*.json 2>/dev/null \
  | sort -u \
  > "$REPORT_DIR/komodo-visual-assets.tsv"

printf '%s\n' \
  "Saved Komodo API responses to $OUT_DIR" \
  "Saved Komodo summaries to $REPORT_DIR"
