#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 RUN_DIR [TRACKING_DIR]" >&2
  exit 1
fi

RUN_DIR="$1"
TRACKING_DIR="${2:-/tmp/SteamTracking-master}"
OUT_DIR="$RUN_DIR/reports"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
mkdir -p "$OUT_DIR"

if [ ! -d "$TRACKING_DIR" ]; then
  echo "missing tracking dir: $TRACKING_DIR" >&2
  exit 1
fi

rg -n -i "Triton|Ibex|Puck|Steam Controller|firmware|pair|dock|dongle" \
  "$TRACKING_DIR" \
  > "$OUT_DIR/steamtracking-hits.txt" || true

rg -n -i "ShouldTritonPairInOobe|PairDongleTriton|UnpairedTriton|ibex_internal|ibex_external" \
  "$TRACKING_DIR" \
  > "$OUT_DIR/steamtracking-pairing-focus.txt" || true

python3 "$SCRIPT_DIR/parse_steamtracking_client_manifests.py" \
  --run-dir "$RUN_DIR" \
  --tracking-dir "$TRACKING_DIR"

printf '%s\n' \
  "Saved SteamTracking grep output to $OUT_DIR/steamtracking-hits.txt" \
  "Saved pairing-focused grep output to $OUT_DIR/steamtracking-pairing-focus.txt" \
  "Saved client manifest report to $OUT_DIR/steamtracking-client-manifests.md"
