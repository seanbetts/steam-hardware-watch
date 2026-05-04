#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 RUN_DIR" >&2
  exit 1
fi

RUN_DIR="$1"
OUT_DIR="$RUN_DIR/api/steamvr-depots"
REPORT_DIR="$RUN_DIR/reports"
mkdir -p "$OUT_DIR" "$REPORT_DIR"

ERROR_FILE="$REPORT_DIR/steamvr-depots-errors.txt"
KEY_LINES="$REPORT_DIR/steamvr-depots-key-lines.txt"
LOCAL_HITS="$REPORT_DIR/steamvr-local-hits.txt"
NEWS_REPORT="$REPORT_DIR/steamvr-news.tsv"
COMMANDS="$REPORT_DIR/steamvr-depot-download-candidates.txt"
TERMS="${STEAMVR_TERMS:-fremont|deckard|steam frame|frame|roy|triton|ibex|puck|lilac|xr|qcom|snapdragon|aarch64|arm64|controller|dongle|firmware|foxnet|activeFrame|summonOverlayKey}"

: > "$ERROR_FILE"
: > "$KEY_LINES"
: > "$LOCAL_HITS"
: > "$NEWS_REPORT"

is_challenge_page() {
  path="$1"
  rg -qi "Checking your browser|Just a moment|Cloudflare|cf-chl|cf-browser-verification" "$path"
}

fetch_html() {
  name="$1"
  url="$2"
  tmp="$OUT_DIR/$name.tmp"
  out="$OUT_DIR/$name"

  if curl -A 'Mozilla/5.0' --retry 2 --retry-delay 2 --max-time 45 -fsSL "$url" > "$tmp" 2>/dev/null \
    && ! is_challenge_page "$tmp"; then
    mv "$tmp" "$out"
    return 0
  fi

  rm -f "$tmp" "$out"
  printf '%s\n' "failed to fetch $url: blocked or challenge page" >> "$ERROR_FILE"
  return 1
}

fetch_json() {
  name="$1"
  url="$2"
  out="$OUT_DIR/$name"

  if ! curl -A 'Mozilla/5.0' --retry 2 --retry-delay 2 --max-time 45 -fsSL "$url" > "$out" 2>/dev/null; then
    printf '%s\n' "failed to fetch $url" >> "$ERROR_FILE"
    rm -f "$out"
    return 1
  fi
}

fetch_html "steamdb-depots.html" "https://steamdb.info/app/250820/depots/" || true
fetch_json "steamvr-news.json" "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=250820&count=40&maxlength=12000&format=json" || true

if [ -f "$OUT_DIR/steamvr-news.json" ] && command -v jq >/dev/null 2>&1; then
  jq -r '
    .appnews.newsitems[]
    | [
        (try (.date | todate) catch (.date | tostring)),
        .title,
        ((.contents // "") | gsub("[\r\n\t]+"; " ") | .[0:360])
      ]
    | @tsv
  ' "$OUT_DIR/steamvr-news.json" > "$NEWS_REPORT" 2>>"$ERROR_FILE" || true
fi

cat > "$COMMANDS" <<'EOF'
# SteamVR AppID: 250820
# Fill in manifest IDs from SteamDB before running Steam's console download_depot command.
download_depot 250820 250821 <manifest_id>  # Windows OpenVR Win32
download_depot 250820 250823 <manifest_id>  # Linux OpenVR Linux
download_depot 250820 250824 <manifest_id>  # Windows/Linux OpenVR Content
download_depot 250820 250827 <manifest_id>  # Windows/Linux OpenVR Content 2
download_depot 250820 250830 <manifest_id>  # SteamVR Environments Content
download_depot 250820 250831 <manifest_id>  # SteamVR Environments Windows
download_depot 250820 250832 <manifest_id>  # SteamVR Environments Linux
EOF

SCAN_DIRS="${STEAMVR_SCAN_DIRS:-}"
DEFAULT_STEAMVR_DIR="$HOME/Library/Application Support/Steam/steamapps/common/SteamVR"
if [ -z "$SCAN_DIRS" ] && [ -d "$DEFAULT_STEAMVR_DIR" ]; then
  SCAN_DIRS="$DEFAULT_STEAMVR_DIR"
fi

if [ -n "$SCAN_DIRS" ]; then
  for scan_dir in $SCAN_DIRS; do
    if [ -d "$scan_dir" ]; then
      rg -n -i "$TERMS" "$scan_dir" >> "$LOCAL_HITS" || true
    else
      printf '%s\n' "missing SteamVR scan dir: $scan_dir" >> "$ERROR_FILE"
    fi
  done
fi

{
  if [ -f "$OUT_DIR/steamdb-depots.html" ]; then
    rg -n -i "$TERMS|Build ID|Time Updated|250821|250823|250824|250827|250830|public|beta|previous" "$OUT_DIR/steamdb-depots.html" || true
  fi
  if [ -s "$NEWS_REPORT" ]; then
    rg -n -i "$TERMS|OpenXR|dashboard|overlay|firmware" "$NEWS_REPORT" || true
  fi
  if [ -s "$LOCAL_HITS" ]; then
    cat "$LOCAL_HITS"
  fi
} > "$KEY_LINES"

printf '%s\n' \
  "Saved SteamVR depot metadata to $OUT_DIR" \
  "Saved local SteamVR hits to $LOCAL_HITS" \
  "Saved matching lines to $KEY_LINES" \
  "Saved candidate download commands to $COMMANDS"
