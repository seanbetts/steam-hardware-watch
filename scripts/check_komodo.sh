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

configure_playwright_runtime() {
  NODE_BIN="${NODE_BIN:-}"
  if [ -z "$NODE_BIN" ]; then
    NODE_BIN="$(command -v node 2>/dev/null || true)"
  fi
  bundled_node="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
  if [ -z "$NODE_BIN" ] && [ -x "$bundled_node" ]; then
    NODE_BIN="$bundled_node"
  fi
  export NODE_BIN

  if [ -z "${NODE_PATH:-}" ]; then
    for node_modules in \
      "$REPO_DIR/node_modules" \
      "$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"
    do
      if [ -d "$node_modules" ]; then
        NODE_PATH="$node_modules"
        export NODE_PATH
        break
      fi
    done
  fi
}

cdp_endpoint_alive() {
  endpoint="${PLAYWRIGHT_CDP_ENDPOINT:-}"
  if [ -z "$endpoint" ]; then
    return 1
  fi
  curl --max-time 2 -fsS "$endpoint/json/version" >/dev/null 2>&1
}

KOMODO_BOOTSTRAP_ATTEMPTED=0

bootstrap_dedicated_browser() {
  if [ "${KOMODO_PLAYWRIGHT_FALLBACK:-0}" != "1" ] || [ "${KOMODO_AUTO_BOOTSTRAP:-1}" = "0" ]; then
    return 0
  fi
  if [ "$KOMODO_BOOTSTRAP_ATTEMPTED" = "1" ]; then
    return 0
  fi

  KOMODO_BOOTSTRAP_ATTEMPTED=1
  bootstrap_cmd="${KOMODO_BOOTSTRAP_CMD:-$SCRIPT_DIR/bootstrap_komodo.sh}"
  if [ ! -x "$bootstrap_cmd" ]; then
    printf '%s\n' "Komodo bootstrap command not executable: $bootstrap_cmd" >> "$ERROR_FILE"
    return 0
  fi

  if "$bootstrap_cmd" >/dev/null 2>>"$ERROR_FILE"; then
    load_local_env
  fi
}

maybe_set_cdp_endpoint() {
  if [ -n "${PLAYWRIGHT_CDP_ENDPOINT:-}" ]; then
    if cdp_endpoint_alive; then
      return 0
    fi
    unset PLAYWRIGHT_CDP_ENDPOINT
  fi

  if [ -z "${PLAYWRIGHT_PROFILE_DIR:-}" ]; then
    bootstrap_dedicated_browser
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
    if cdp_endpoint_alive; then
      return 0
    fi
    unset PLAYWRIGHT_CDP_ENDPOINT
  fi

  bootstrap_dedicated_browser
}

load_local_env

KOMODO_USER_AGENT="${KOMODO_USER_AGENT:-Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36}"
export KOMODO_USER_AGENT

fetch_json() {
  name="$1"
  url="$2"
  allow_fallback="${3:-1}"
  tmp="$OUT_DIR/$name.json.tmp"
  if curl -A "$KOMODO_USER_AGENT" --retry 1 --retry-delay 1 --max-time 12 -fsSL "$url" > "$tmp" 2>/dev/null \
    && jq empty "$tmp" >/dev/null 2>&1; then
    mv "$tmp" "$OUT_DIR/$name.json"
    return 0
  fi

  rm -f "$tmp"

  if [ "$allow_fallback" = "1" ] && [ "${KOMODO_PLAYWRIGHT_FALLBACK:-0}" = "1" ]; then
    configure_playwright_runtime
    if [ -z "${NODE_BIN:-}" ]; then
      printf '%s\n' "Playwright fallback unavailable: node executable not found" >> "$ERROR_FILE"
      rm -f "$tmp"
      printf '%s\n' "failed to fetch JSON from $url" >> "$ERROR_FILE"
      return 1
    fi
    maybe_set_cdp_endpoint
    PLAYWRIGHT_CORE_PATH="${PLAYWRIGHT_CORE_PATH:-}"
    if command -v playwright-cli >/dev/null 2>&1; then
      PLAYWRIGHT_CLI_BIN="$(command -v playwright-cli)"
      PLAYWRIGHT_CORE_PATH="$(CDPATH= cd -- "$(dirname "$PLAYWRIGHT_CLI_BIN")/../lib/node_modules/@playwright/cli/node_modules/playwright-core" 2>/dev/null && pwd || true)"
    fi
    PLAYWRIGHT_CORE_PATH="$PLAYWRIGHT_CORE_PATH" "$NODE_BIN" "$SCRIPT_DIR/fetch_with_playwright.js" "$url" "$tmp"
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

fetch_json "product-machine-jpy" "https://komodostation.com/wp-json/wp/v2/product/413772" || true
fetch_json "product-frame-jpy" "https://komodostation.com/wp-json/wp/v2/product/413776" || true

fetch_json "sections-controller-search" "https://komodostation.com/wp-json/wp/v2/sections?search=Steam%20Controller&per_page=100" || true
fetch_json "sections-machine-search" "https://komodostation.com/wp-json/wp/v2/sections?search=Steam%20Machine&per_page=100" || true
fetch_json "sections-frame-search" "https://komodostation.com/wp-json/wp/v2/sections?search=Steam%20Frame&per_page=100" || true

fetch_json "media-controller-search" "https://komodostation.com/wp-json/wp/v2/media?search=Steam%20Controller&per_page=100" || true
fetch_json "media-parent-product-controller" "https://komodostation.com/wp-json/wp/v2/media?parent=413763&per_page=100" || true

for optional_array in \
  sections-controller-search \
  sections-machine-search \
  sections-frame-search \
  media-controller-search \
  media-parent-product-controller
do
  if [ ! -f "$OUT_DIR/$optional_array.json" ]; then
    printf '%s\n' "[]" > "$OUT_DIR/$optional_array.json"
  fi
done

for section_report in \
  sections-controller-search \
  sections-machine-search \
  sections-frame-search
do
  for id in $(jq -r '.[].id' "$OUT_DIR/$section_report.json" 2>/dev/null || true); do
    fetch_json "media-parent-section-$id" "https://komodostation.com/wp-json/wp/v2/media?parent=$id&per_page=100" || true
  done
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

write_section_media_report() {
  sections_file="$1"
  output_file="$2"
  : > "$output_file"
  for id in $(jq -r '.[].id' "$sections_file" 2>/dev/null || true); do
    media_file="$OUT_DIR/media-parent-section-$id.json"
    if [ -f "$media_file" ]; then
      jq -r '
        .[]?
        | [.id,.date,.modified,.slug,.mime_type,.post,.source_url]
        | @tsv
      ' "$media_file" >> "$output_file"
    fi
  done
}

write_section_media_report "$OUT_DIR/sections-machine-search.json" "$REPORT_DIR/komodo-machine-media.tsv"
write_section_media_report "$OUT_DIR/sections-frame-search.json" "$REPORT_DIR/komodo-frame-media.tsv"

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
