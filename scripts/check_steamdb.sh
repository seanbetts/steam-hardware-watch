#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 RUN_DIR" >&2
  exit 1
fi

RUN_DIR="$1"
OUT_DIR="$RUN_DIR/api/steamdb"
REPORT_DIR="$RUN_DIR/reports"
mkdir -p "$OUT_DIR" "$REPORT_DIR"

ERROR_FILE="$REPORT_DIR/steamdb-errors.txt"
: > "$ERROR_FILE"
: > "$REPORT_DIR/steamdb-key-lines.txt"

fetch_html() {
  name="$1"
  url="$2"
  if ! curl -A 'Mozilla/5.0' --retry 2 --retry-delay 2 --max-time 45 -fsSL "$url" > "$OUT_DIR/$name.html" 2>/dev/null; then
    printf '%s\n' "failed to fetch $url" >> "$ERROR_FILE"
    rm -f "$OUT_DIR/$name.html"
    return 1
  fi
}

fetch_html "controller-app" "https://steamdb.info/app/4165870/" || true
fetch_html "controller-history" "https://steamdb.info/app/4165870/history/" || true
fetch_html "controller-unboxing-app" "https://steamdb.info/app/4653940/" || true
fetch_html "controller-unboxing-package" "https://steamdb.info/sub/1620489/" || true

rg -n "Coming soon|released|ownersonly|free on demand|unboxing|package|depot|video" \
  "$OUT_DIR" \
  > "$REPORT_DIR/steamdb-key-lines.txt" || true

printf '%s\n' \
  "Saved SteamDB pages to $OUT_DIR" \
  "Saved matching lines to $REPORT_DIR/steamdb-key-lines.txt"
