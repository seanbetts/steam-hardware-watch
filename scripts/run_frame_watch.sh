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
