#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 RUN_DIR [TRACKING_DIR]" >&2
  exit 1
fi

RUN_DIR="$1"
TRACKING_DIR="${2:-/tmp/SteamTracking-master}"
OUT_DIR="$RUN_DIR/reports"
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

printf '%s\n' \
  "Saved SteamTracking grep output to $OUT_DIR/steamtracking-hits.txt" \
  "Saved pairing-focused grep output to $OUT_DIR/steamtracking-pairing-focus.txt"
