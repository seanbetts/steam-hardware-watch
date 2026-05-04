#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 RUN_DIR" >&2
  exit 1
fi

RUN_DIR="$1"
BASE_URL="${STEAMOS_MIRROR_BASE_URL:-https://steamdeck-packages.steamos.cloud/archlinux-mirror}"
REPOS="${STEAMOS_MIRROR_REPOS:-holo-3.8 holo-main jupiter-3.8 jupiter-main}"
TERMS="${STEAMOS_MIRROR_TERMS:-fremont|deckard|steam frame|frame|roy|triton|ibex|puck|lilac|xr|qcom|snapdragon|aarch64|arm64|controller|dongle|firmware|foxnet}"

OUT_DIR="$RUN_DIR/api/steamos-mirror"
REPORT_DIR="$RUN_DIR/reports"
EXTRACT_DIR="$RUN_DIR/extracted/steamos-mirror"
mkdir -p "$OUT_DIR" "$REPORT_DIR" "$EXTRACT_DIR"

ERROR_FILE="$REPORT_DIR/steamos-mirror-errors.txt"
ALL_REPOS="$REPORT_DIR/steamos-mirror-repos.txt"
INTERESTING_REPOS="$REPORT_DIR/steamos-mirror-interesting-repos.txt"
PACKAGES="$REPORT_DIR/steamos-mirror-packages.tsv"
KEY_LINES="$REPORT_DIR/steamos-mirror-key-lines.txt"

: > "$ERROR_FILE"
: > "$ALL_REPOS"
: > "$INTERESTING_REPOS"
: > "$PACKAGES"
: > "$KEY_LINES"

fetch() {
  name="$1"
  url="$2"
  out="$OUT_DIR/$name"

  if ! curl -A 'Mozilla/5.0' --retry 2 --retry-delay 2 --max-time 45 -fsSL "$url" > "$out" 2>/dev/null; then
    printf '%s\n' "failed to fetch $url" >> "$ERROR_FILE"
    rm -f "$out"
    return 1
  fi
}

extract_repo_links() {
  path="$1"
  if [ ! -f "$path" ]; then
    return 0
  fi
  rg -o 'href="[^"]+/"' "$path" \
    | sed 's/^href="//; s|/"$||; s|/$||' \
    | awk '$0 != ".." && $0 != "Parent directory" { print }' || true
}

parse_desc_files() {
  repo="$1"
  dir="$2"
  find "$dir" -name desc -print | while IFS= read -r desc; do
    awk -v repo="$repo" '
      /^%NAME%$/ { getline name }
      /^%VERSION%$/ { getline version }
      END {
        if (name != "" && version != "") {
          print repo "\t" name "\t" version
        }
      }
    ' "$desc"
  done
}

fetch "root.html" "$BASE_URL/" || true
fetch "sources-root.html" "$BASE_URL/sources/" || true

{
  extract_repo_links "$OUT_DIR/root.html"
  extract_repo_links "$OUT_DIR/sources-root.html" | sed 's|^|sources/|'
} | sort -u > "$ALL_REPOS"

rg -i "$TERMS" "$ALL_REPOS" > "$INTERESTING_REPOS" || true

for repo in $REPOS; do
  db_name="$repo.db"
  if ! fetch "$db_name" "$BASE_URL/$repo/os/x86_64/$db_name"; then
    continue
  fi

  repo_extract="$EXTRACT_DIR/$repo"
  rm -rf "$repo_extract"
  mkdir -p "$repo_extract"

  if command -v bsdtar >/dev/null 2>&1; then
    if bsdtar -xf "$OUT_DIR/$db_name" -C "$repo_extract" 2>>"$ERROR_FILE"; then
      parse_desc_files "$repo" "$repo_extract" >> "$PACKAGES"
    else
      printf '%s\n' "failed to extract package database for $repo" >> "$ERROR_FILE"
    fi
  else
    printf '%s\n' "missing bsdtar; cannot extract package database for $repo" >> "$ERROR_FILE"
  fi
done

sort -u "$PACKAGES" -o "$PACKAGES"

{
  rg -i "$TERMS" "$PACKAGES" || true
  rg -i "$TERMS" "$INTERESTING_REPOS" || true
} > "$KEY_LINES"

printf '%s\n' \
  "Saved SteamOS mirror metadata to $OUT_DIR" \
  "Saved repository list to $ALL_REPOS" \
  "Saved package list to $PACKAGES" \
  "Saved matching lines to $KEY_LINES"
