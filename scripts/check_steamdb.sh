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
: > "$REPORT_DIR/steamdb-reservation-packages.tsv"

load_local_env() {
  env_file="${STEAMDB_ENV_FILE:-$REPO_DIR/.local/steamdb-env.sh}"
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
  endpoint="${STEAMDB_CDP_ENDPOINT:-}"
  if [ -z "$endpoint" ]; then
    return 1
  fi
  curl --max-time 2 -fsS "$endpoint/json/version" >/dev/null 2>&1
}

STEAMDB_BOOTSTRAP_ATTEMPTED=0

bootstrap_dedicated_browser() {
  if [ "${STEAMDB_PLAYWRIGHT_FALLBACK:-0}" != "1" ] || [ "${STEAMDB_AUTO_BOOTSTRAP:-1}" = "0" ]; then
    return 0
  fi
  if [ "$STEAMDB_BOOTSTRAP_ATTEMPTED" = "1" ]; then
    return 0
  fi

  STEAMDB_BOOTSTRAP_ATTEMPTED=1
  bootstrap_cmd="${STEAMDB_BOOTSTRAP_CMD:-$SCRIPT_DIR/bootstrap_steamdb.sh}"
  if [ ! -x "$bootstrap_cmd" ]; then
    printf '%s\n' "SteamDB bootstrap command not executable: $bootstrap_cmd" >> "$ERROR_FILE"
    return 0
  fi

  if "$bootstrap_cmd" >/dev/null 2>>"$ERROR_FILE"; then
    load_local_env
  fi
}

maybe_set_cdp_endpoint() {
  if [ -n "${STEAMDB_CDP_ENDPOINT:-}" ]; then
    if cdp_endpoint_alive; then
      return 0
    fi
    unset STEAMDB_CDP_ENDPOINT
  fi

  if [ -z "${STEAMDB_PROFILE_DIR:-}" ]; then
    bootstrap_dedicated_browser
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
    if cdp_endpoint_alive; then
      return 0
    fi
    unset STEAMDB_CDP_ENDPOINT
  fi

  bootstrap_dedicated_browser
}

is_challenge_page() {
  path="$1"
  rg -qi "Checking your browser|Just a moment|cf-chl|cf-browser-verification|challenge-platform|cdn-cgi/challenge-platform" "$path"
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

  if [ "${STEAMDB_PLAYWRIGHT_FALLBACK:-0}" = "1" ]; then
    configure_playwright_runtime
    maybe_set_cdp_endpoint
    if [ -n "${NODE_BIN:-}" ] \
      && "$NODE_BIN" "$SCRIPT_DIR/fetch_steamdb_with_playwright.js" "$url" "$tmp" >/dev/null 2>&1 \
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

for packageid in 1558609 1629446 1629447 1629458 1629460 1629484 1629486; do
  fetch_html "package-$packageid" "https://steamdb.info/sub/$packageid/" || true
done

python3 - "$OUT_DIR" "$REPORT_DIR/steamdb-reservation-packages.tsv" <<'PY'
import html
import sys
from html.parser import HTMLParser
from pathlib import Path


out_dir = Path(sys.argv[1])
report_path = Path(sys.argv[2])

packages = {
    "1558609": ("Steam Controller", "4165870", "Steam Controller"),
    "1629446": ("Steam Machine", "4165910", "Steam Machine"),
    "1629447": ("Steam Machine", "4165910", "Steam Machine"),
    "1629458": ("Steam Machine", "4165910", "Steam Machine"),
    "1629460": ("Steam Machine", "4165910", "Steam Machine"),
    "1629484": ("Steam Frame", "4165890", "Steam Frame"),
    "1629486": ("Steam Frame", "4165890", "Steam Frame"),
}


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        text = html.unescape(data).strip()
        if text:
            self.parts.append(text)


def clean(value):
    return str(value or "").replace("\t", " ").replace("\n", " ").strip()


def normalized_text(path):
    parser = TextParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    parts = [part.replace("\u2013", "-") for part in parser.parts]
    return parts, " ".join(parts)


def field_after(parts, label):
    for index, part in enumerate(parts):
        if part == label:
            for candidate in parts[index + 1 :]:
                if candidate:
                    return candidate
    return ""


rows = [[
    "product",
    "package_id",
    "last_record_update",
    "last_changenumber",
    "possible_apps",
    "status",
]]

for packageid, (product, expected_appid, expected_name) in packages.items():
    path = out_dir / f"package-{packageid}.html"
    if not path.exists():
        rows.append([product, packageid, "", "", "", "missing_or_blocked"])
        continue

    parts, text = normalized_text(path)
    last_record_update = field_after(parts, "Last Record Update")
    last_changenumber = field_after(parts, "Last Changenumber")
    possible_apps = ""
    if expected_appid in text and expected_name in text:
        possible_apps = f"{expected_appid}:{expected_name}"

    lower_text = text.lower()
    if "besides the fact that it exists" in lower_text:
        status = "private_exists_only"
    elif last_record_update or last_changenumber:
        status = "details_available"
    else:
        status = "unknown"

    rows.append([
        product,
        packageid,
        last_record_update,
        last_changenumber,
        possible_apps,
        status,
    ])

report_path.write_text(
    "\n".join("\t".join(clean(value) for value in row) for row in rows) + "\n",
    encoding="utf-8",
)
PY

{
  printf '%s\n' "Reservation package SteamDB snapshot:"
  sed -n '1,40p' "$REPORT_DIR/steamdb-reservation-packages.tsv"
  printf '\n%s\n' "HTML key matches:"
} > "$REPORT_DIR/steamdb-key-lines.txt"

rg -n -o "Coming soon|released|ownersonly|free on demand|unboxing|package|depot|video" \
  "$OUT_DIR" \
  | sort -u \
  >> "$REPORT_DIR/steamdb-key-lines.txt" || true

printf '%s\n' \
  "Saved SteamDB pages to $OUT_DIR" \
  "Saved matching lines to $REPORT_DIR/steamdb-key-lines.txt" \
  "Saved reservation package report to $REPORT_DIR/steamdb-reservation-packages.tsv"
