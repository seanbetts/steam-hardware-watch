#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 YYYY-MM-DD [base_dir]" >&2
  exit 1
fi

RUN_DATE="$1"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
BASE_DIR="${2:-$REPO_DIR/runs}"
RUN_DIR="$BASE_DIR/$RUN_DATE"

mkdir -p "$RUN_DIR/api" "$RUN_DIR/assets" "$RUN_DIR/frames" "$RUN_DIR/reports"

RUN_NOTE_DIR="$(CDPATH= cd -- "$REPO_DIR/status/runs" && pwd)"
RUN_NOTE="$RUN_NOTE_DIR/$RUN_DATE.md"

if [ ! -f "$RUN_NOTE" ]; then
  cat >"$RUN_NOTE" <<EOF
# Run Note: $RUN_DATE

## Summary

-

## Source Checks

### Komodo

-

### SteamDB

-

### SteamTracking / GameTracking

-

### SteamVR Depots

-

### SteamOS Package Mirror

-

### Valve Support / CDN

-

### Customs / Regulatory

-

## Effect On Key Questions

- Price:
- Release date:
- Same-time launch:

## Next Checks

-
EOF
fi

printf 'RUN_DIR=%s\nRUN_NOTE=%s\n' "$RUN_DIR" "$RUN_NOTE"
