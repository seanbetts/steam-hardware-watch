#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 RUN_DIR" >&2
  exit 1
fi

RUN_DIR="$1"
OUT_DIR="$RUN_DIR/api/valve"
REPORT_DIR="$RUN_DIR/reports"
mkdir -p "$OUT_DIR" "$REPORT_DIR"

ERROR_FILE="$REPORT_DIR/valve-errors.txt"
: > "$ERROR_FILE"
: > "$REPORT_DIR/valve-key-lines.txt"

fetch_page() {
  name="$1"
  url="$2"
  if ! curl -A 'Mozilla/5.0' --retry 2 --retry-delay 2 --max-time 45 -fsSL "$url" > "$OUT_DIR/$name.html" 2>/dev/null; then
    printf '%s\n' "failed to fetch $url" >> "$ERROR_FILE"
    rm -f "$OUT_DIR/$name.html"
    return 1
  fi
}

fetch_page "steamdeck-site" "https://www.steamdeck.com/" || true
fetch_page "steam-support-deck" "https://help.steampowered.com/en/wizard/HelpWithSteamDeck" || true
fetch_page "steam-controller-store" "https://store.steampowered.com/app/4165870/" || true
fetch_page "steam-hardware-root" "https://steampowered.com/hardware" || true

rg -n "Steam Controller|Steam Machine|Steam Frame|coming soon|manual|safety|warranty|preorder|release" \
  "$OUT_DIR" \
  > "$REPORT_DIR/valve-key-lines.txt" || true

printf '%s\n' \
  "Saved Valve pages to $OUT_DIR" \
  "Saved matching lines to $REPORT_DIR/valve-key-lines.txt"
