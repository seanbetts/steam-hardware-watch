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

SOURCE_REPORT="$OUT_DIR/steamtracking-source.txt"

if [ -d "$TRACKING_DIR/.git" ]; then
  if ! git -C "$TRACKING_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "invalid SteamTracking git checkout: $TRACKING_DIR" >&2
    exit 1
  fi

  BEFORE_COMMIT="$(git -C "$TRACKING_DIR" rev-parse HEAD)"
  BEFORE_TIME="$(git -C "$TRACKING_DIR" log -1 --format=%cI)"
  if [ "${STEAMTRACKING_UPDATE:-1}" = "1" ]; then
    BRANCH="$(git -C "$TRACKING_DIR" rev-parse --abbrev-ref HEAD)"
    if [ "$BRANCH" = "HEAD" ]; then
      git -C "$TRACKING_DIR" fetch --prune --quiet
    else
      git -C "$TRACKING_DIR" pull --ff-only --quiet
    fi
  fi
  AFTER_COMMIT="$(git -C "$TRACKING_DIR" rev-parse HEAD)"
  AFTER_TIME="$(git -C "$TRACKING_DIR" log -1 --format=%cI)"
  {
    printf 'tracking_dir=%s\n' "$TRACKING_DIR"
    printf 'before_commit=%s\n' "$BEFORE_COMMIT"
    printf 'before_time=%s\n' "$BEFORE_TIME"
    printf 'after_commit=%s\n' "$AFTER_COMMIT"
    printf 'after_time=%s\n' "$AFTER_TIME"
    printf 'updated=%s\n' "$([ "$BEFORE_COMMIT" = "$AFTER_COMMIT" ] && printf no || printf yes)"
  } > "$SOURCE_REPORT"
else
  {
    printf 'tracking_dir=%s\n' "$TRACKING_DIR"
    printf 'git_checkout=no\n'
  } > "$SOURCE_REPORT"
fi

if [ ! -d "$TRACKING_DIR/ClientManifest" ] && [ ! -d "$TRACKING_DIR/ClientExtracted" ]; then
  echo "SteamTracking checkout has no ClientManifest or ClientExtracted content: $TRACKING_DIR" >&2
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

python3 "$SCRIPT_DIR/parse_steamtracking_hardware_signals.py" \
  --run-dir "$RUN_DIR" \
  --tracking-dir "$TRACKING_DIR"

printf '%s\n' \
  "Saved SteamTracking source metadata to $SOURCE_REPORT" \
  "Saved SteamTracking grep output to $OUT_DIR/steamtracking-hits.txt" \
  "Saved pairing-focused grep output to $OUT_DIR/steamtracking-pairing-focus.txt" \
  "Saved client manifest report to $OUT_DIR/steamtracking-client-manifests.md" \
  "Saved hardware signal report to $OUT_DIR/steamtracking-hardware-signals.md"
