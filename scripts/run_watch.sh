#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 YYYY-MM-DD [base_dir] [tracking_dir]" >&2
  exit 1
fi

RUN_DATE="$1"

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
BASE_DIR="${2:-$REPO_DIR/runs}"
TRACKING_DIR="${3:-/tmp/SteamTracking-master}"
KOMODO_ENV_FILE="${KOMODO_ENV_FILE:-$REPO_DIR/.local/komodo-env.sh}"
STEAMDB_ENV_FILE="${STEAMDB_ENV_FILE:-$REPO_DIR/.local/steamdb-env.sh}"

cleanup() {
  if [ "${KOMODO_KEEP_BROWSER_OPEN:-0}" = "1" ]; then
    :
  elif [ -f "$KOMODO_ENV_FILE" ] && [ -x "$SCRIPT_DIR/close_komodo.sh" ]; then
    "$SCRIPT_DIR/close_komodo.sh" >/dev/null 2>&1 || true
  fi

  if [ "${STEAMDB_KEEP_BROWSER_OPEN:-0}" = "1" ]; then
    :
  elif [ -f "$STEAMDB_ENV_FILE" ] && [ -x "$SCRIPT_DIR/close_steamdb.sh" ]; then
    "$SCRIPT_DIR/close_steamdb.sh" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

INIT_OUTPUT="$("$SCRIPT_DIR/init_run.sh" "$RUN_DATE" "$BASE_DIR")"
RUN_DIR="$(printf '%s\n' "$INIT_OUTPUT" | awk -F= '/^RUN_DIR=/{print $2}')"
RUN_NOTE="$(printf '%s\n' "$INIT_OUTPUT" | awk -F= '/^RUN_NOTE=/{print $2}')"

if [ -z "$RUN_DIR" ] || [ -z "$RUN_NOTE" ]; then
  echo "failed to initialize run folder" >&2
  exit 1
fi

printf '%s\n' "Run dir: $RUN_DIR"
printf '%s\n' "Run note: $RUN_NOTE"

"$SCRIPT_DIR/check_komodo.sh" "$RUN_DIR"
"$SCRIPT_DIR/check_steamkit_pics.sh" "$RUN_DIR"
"$SCRIPT_DIR/check_steamdb.sh" "$RUN_DIR"
"$SCRIPT_DIR/check_steamtracking.sh" "$RUN_DIR" "$TRACKING_DIR"
"$SCRIPT_DIR/check_steamvr_depots.sh" "$RUN_DIR"
"$SCRIPT_DIR/check_steamos_mirror.sh" "$RUN_DIR"
"$SCRIPT_DIR/check_valve_endpoints.sh" "$RUN_DIR"
"$SCRIPT_DIR/check_customs_shipments.sh" "$RUN_DIR"
python3 "$SCRIPT_DIR/save_visual_assets.py" --run-dir "$RUN_DIR" --base-dir "$BASE_DIR"

PREVIOUS_DIR=""
for candidate in $(find "$BASE_DIR" -mindepth 1 -maxdepth 1 -type d -name '????-??-??' | sort); do
  if [ "$candidate" = "$RUN_DIR" ]; then
    continue
  fi
  case "$(basename "$candidate")" in
    "$RUN_DATE") ;;
    *)
      if [ "$(basename "$candidate")" \< "$RUN_DATE" ]; then
        PREVIOUS_DIR="$candidate"
      fi
      ;;
  esac
done

if [ -n "$PREVIOUS_DIR" ]; then
  COMPARE_OUT="$RUN_DIR/reports/compare-vs-$(basename "$PREVIOUS_DIR").md"
  python3 "$SCRIPT_DIR/compare_runs.py" \
    --previous "$PREVIOUS_DIR" \
    --current "$RUN_DIR" \
    --output "$COMPARE_OUT"
  printf '%s\n' "Comparison report: $COMPARE_OUT"
else
  printf '%s\n' "No previous run folder found under $BASE_DIR"
fi

STATUS_DRAFT_OUT="$RUN_DIR/reports/status-draft.md"
python3 "$SCRIPT_DIR/draft_status_update.py" \
  --run-dir "$RUN_DIR" \
  --output "$STATUS_DRAFT_OUT"
printf '%s\n' "Status draft: $STATUS_DRAFT_OUT"

RUN_SUMMARY_OUT="$RUN_DIR/reports/run-summary.md"
python3 "$SCRIPT_DIR/write_run_summary.py" \
  --run-dir "$RUN_DIR" \
  --output "$RUN_SUMMARY_OUT"
printf '%s\n' "Run summary: $RUN_SUMMARY_OUT"

printf '%s\n' "Run complete."
