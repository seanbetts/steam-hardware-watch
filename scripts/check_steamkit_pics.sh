#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 RUN_DIR" >&2
  exit 1
fi

RUN_DIR="$1"
OUT_DIR="$RUN_DIR/api/steamkit"
REPORT_DIR="$RUN_DIR/reports"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$REPO_DIR/tools/steamkit-pics"
mkdir -p "$OUT_DIR" "$REPORT_DIR"

ERROR_FILE="$REPORT_DIR/steamkit-pics-errors.txt"
REPORT_FILE="$REPORT_DIR/steamkit-pics-packages.tsv"
KEY_LINES_FILE="$REPORT_DIR/steamkit-pics-key-lines.txt"
DETAIL_REPORT_FILE="$REPORT_DIR/steamkit-pics-detail.md"
: > "$ERROR_FILE"
: > "$REPORT_FILE"
: > "$KEY_LINES_FILE"
: > "$DETAIL_REPORT_FILE"

find_previous_report() {
  current_base="$(basename "$RUN_DIR")"
  base_dir="$(dirname "$RUN_DIR")"
  previous_dir=""

  for candidate in $(find "$base_dir" -mindepth 1 -maxdepth 1 -type d -name '????-??-??' | sort); do
    if [ "$candidate" = "$RUN_DIR" ]; then
      continue
    fi
    candidate_base="$(basename "$candidate")"
    if [ "$candidate_base" \< "$current_base" ]; then
      previous_dir="$candidate"
    fi
  done

  if [ -n "$previous_dir" ] && [ -s "$previous_dir/reports/steamkit-pics-packages.tsv" ]; then
    printf '%s\n' "$previous_dir/reports/steamkit-pics-packages.tsv"
  fi
}

load_local_env() {
  env_file="${STEAMKIT_ENV_FILE:-$REPO_DIR/.local/steamkit-env.sh}"
  if [ -f "$env_file" ]; then
    # shellcheck disable=SC1090
    . "$env_file"
  fi
}

write_unavailable_report() {
  reason="$1"
  detail="$2"
  {
    printf '%s\n' "type	product	id	status	changenumber	previous_changenumber	changed_since_previous	sha_hash	only_public	name	related_ids	details"
    printf '%s\n' "app	Steam Controller	4165870	$reason								$detail"
    printf '%s\n' "app	Steam Frame	4165890	$reason								$detail"
    printf '%s\n' "app	Steam Machine	4165910	$reason								$detail"
    printf '%s\n' "package	Steam Controller	1558609	$reason								$detail"
    printf '%s\n' "package	Steam Machine	1629446	$reason								$detail"
    printf '%s\n' "package	Steam Machine	1629447	$reason								$detail"
    printf '%s\n' "package	Steam Machine	1629458	$reason								$detail"
    printf '%s\n' "package	Steam Machine	1629460	$reason								$detail"
    printf '%s\n' "package	Steam Frame	1629484	$reason								$detail"
    printf '%s\n' "package	Steam Frame	1629486	$reason								$detail"
  } > "$REPORT_FILE"

  {
    printf '%s\n' "SteamKit/PICS unavailable: $detail"
    printf '%s\n' ""
    printf '%s\n' "SteamKit/PICS package snapshot:"
    sed -n '1,40p' "$REPORT_FILE"
  } > "$KEY_LINES_FILE"

  {
    printf '%s\n\n' "# SteamKit / PICS Detail"
    printf '%s\n\n' "SteamKit/PICS unavailable: $detail"
    printf '%s\n' "The normal watcher continued and wrote placeholder rows so downstream reports still render."
  } > "$DETAIL_REPORT_FILE"
}

load_local_env

if [ -z "${STEAMKIT_USERNAME:-}" ] || { [ -z "${STEAMKIT_PASSWORD:-}" ] && [ -z "${STEAMKIT_ACCESS_TOKEN:-}" ]; }; then
  detail="STEAMKIT_USERNAME/STEAMKIT_PASSWORD not set"
  if [ -n "${STEAMKIT_USERNAME:-}" ] && [ -z "${STEAMKIT_PASSWORD:-}" ]; then
    detail="STEAMKIT_PASSWORD or STEAMKIT_ACCESS_TOKEN not set"
  fi
  write_unavailable_report "missing_credentials" "$detail"
  printf '%s\n' "$detail" >> "$ERROR_FILE"
  printf '%s\n' \
    "SteamKit/PICS unavailable: $detail" \
    "Saved SteamKit/PICS report to $REPORT_FILE"
  exit 0
fi

export STEAMKIT_USERNAME
if [ -n "${STEAMKIT_PASSWORD:-}" ]; then
  export STEAMKIT_PASSWORD
fi
if [ -n "${STEAMKIT_ACCESS_TOKEN:-}" ]; then
  export STEAMKIT_ACCESS_TOKEN
fi
if [ -n "${STEAMKIT_AUTH_CODE:-}" ]; then
  export STEAMKIT_AUTH_CODE
fi
if [ -n "${STEAMKIT_TWO_FACTOR_CODE:-}" ]; then
  export STEAMKIT_TWO_FACTOR_CODE
fi
if [ -n "${STEAMKIT_TIMEOUT_SECONDS:-}" ]; then
  export STEAMKIT_TIMEOUT_SECONDS
fi

if ! command -v dotnet >/dev/null 2>&1; then
  detail="dotnet CLI not found"
  write_unavailable_report "missing_dotnet" "$detail"
  printf '%s\n' "$detail" >> "$ERROR_FILE"
  printf '%s\n' \
    "SteamKit/PICS unavailable: $detail" \
    "Saved SteamKit/PICS report to $REPORT_FILE"
  exit 0
fi

PREVIOUS_REPORT="${STEAMKIT_PREVIOUS_REPORT:-}"
if [ -z "$PREVIOUS_REPORT" ]; then
  PREVIOUS_REPORT="$(find_previous_report || true)"
fi

if [ -n "$PREVIOUS_REPORT" ]; then
  if ! dotnet run --project "$PROJECT_DIR" -- \
    --out-dir "$OUT_DIR" \
    --report "$REPORT_FILE" \
    --key-lines "$KEY_LINES_FILE" \
    --markdown-report "$DETAIL_REPORT_FILE" \
    --previous-report "$PREVIOUS_REPORT" \
    >> "$REPORT_DIR/steamkit-pics-dotnet.log" 2>> "$ERROR_FILE"; then
    detail="SteamKit/PICS helper failed; see steamkit-pics-errors.txt and steamkit-pics-dotnet.log"
    if [ ! -s "$REPORT_FILE" ]; then
      write_unavailable_report "helper_failed" "$detail"
    fi
    printf '%s\n' "$detail" >> "$ERROR_FILE"
  fi
else
  if ! dotnet run --project "$PROJECT_DIR" -- \
    --out-dir "$OUT_DIR" \
    --report "$REPORT_FILE" \
    --key-lines "$KEY_LINES_FILE" \
    --markdown-report "$DETAIL_REPORT_FILE" \
    >> "$REPORT_DIR/steamkit-pics-dotnet.log" 2>> "$ERROR_FILE"; then
  detail="SteamKit/PICS helper failed; see steamkit-pics-errors.txt and steamkit-pics-dotnet.log"
    if [ ! -s "$REPORT_FILE" ]; then
      write_unavailable_report "helper_failed" "$detail"
    fi
    printf '%s\n' "$detail" >> "$ERROR_FILE"
  fi
fi

printf '%s\n' \
  "Saved SteamKit/PICS snapshots to $OUT_DIR" \
  "Saved matching lines to $KEY_LINES_FILE" \
  "Saved SteamKit/PICS report to $REPORT_FILE" \
  "Saved SteamKit/PICS detail report to $DETAIL_REPORT_FILE"
