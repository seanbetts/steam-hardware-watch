#!/bin/sh
set -eu

usage() {
  echo "usage: $0 [--komodo-only] YYYY-MM-DD [base_dir] [tracking_dir]" >&2
}

KOMODO_ONLY=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --komodo-only)
      KOMODO_ONLY=1
      shift
      ;;
    --)
      shift
      break
      ;;
    -*)
      usage
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

if [ "$#" -lt 1 ]; then
  usage
  exit 1
fi

RUN_DATE="$1"

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
BASE_DIR="${2:-$REPO_DIR/runs}"
TRACKING_DIR="${3:-/tmp/SteamTracking-master}"

if [ "$KOMODO_ONLY" = "1" ]; then
  if [ "$#" -ge 3 ]; then
    "$SCRIPT_DIR/run_watch.sh" --komodo-only "$RUN_DATE" "$BASE_DIR" "$TRACKING_DIR"
  else
    "$SCRIPT_DIR/run_watch.sh" --komodo-only "$RUN_DATE" "$BASE_DIR"
  fi
  exit 0
fi

if [ "$#" -ge 3 ]; then
  "$SCRIPT_DIR/run_watch.sh" "$RUN_DATE" "$BASE_DIR" "$TRACKING_DIR"
else
  "$SCRIPT_DIR/run_watch.sh" "$RUN_DATE" "$BASE_DIR"
fi

RUN_DIR="$BASE_DIR/$RUN_DATE"
FRAME_FOCUS_OUT="$RUN_DIR/reports/frame-focus.md"

if [ ! -f "$FRAME_FOCUS_OUT" ]; then
  python3 "$SCRIPT_DIR/write_frame_focus_report.py" \
    --run-dir "$RUN_DIR" \
    --output "$FRAME_FOCUS_OUT"
fi

printf '%s\n' "Frame focus report: $FRAME_FOCUS_OUT"
