#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
    echo "usage: $0 RUN_DIR" >&2
    exit 1
fi

RUN_DIR=$1
OUT_DIR=$RUN_DIR/api/customs
REPORT_DIR=$RUN_DIR/reports
SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)

mkdir -p "$OUT_DIR" "$REPORT_DIR"

ERROR_FILE=$REPORT_DIR/customs-shipments-errors.txt
: > "$ERROR_FILE"

IMPORTINFO_USER_AGENT=${IMPORTINFO_USER_AGENT:-"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

MANIFEST=$OUT_DIR/importinfo-inputs.tsv
: > "$MANIFEST"

looks_like_importinfo_shipment_table() {
    path=$1
    for header in "Master BOL" "House BOL" "Arrival Date" "Commodity"; do
        if ! grep -qi "$header" "$path"; then
            return 1
        fi
    done
    return 0
}

looks_like_importgenius_shipment_page() {
    path=$1
    for marker in "Bill of Lading" "VALVE CORPORATION"; do
        if ! grep -qi "$marker" "$path"; then
            return 1
        fi
    done
    if ! grep -Eqi "GAME CONSOLE|VIRTUAL REALITY|WIRELESS PC CONTROLLER|VR CONTROLLER|HEADSET" "$path"; then
        return 1
    fi
    return 0
}

fetch_importinfo() {
    slug=$1
    query=$2
    url=$3
    tmp=$OUT_DIR/$slug.html.tmp
    out=$OUT_DIR/$slug.html

    if curl \
        -A "$IMPORTINFO_USER_AGENT" \
        -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
        -H "Accept-Language: en-US,en;q=0.9" \
        --retry 2 \
        --retry-delay 2 \
        --max-time 45 \
        -fsSL "$url" > "$tmp" 2>/dev/null
    then
        if ! looks_like_importinfo_shipment_table "$tmp"; then
            rm -f "$tmp" "$out"
            printf 'unexpected or blocked content from %s\n' "$url" >> "$ERROR_FILE"
            return 0
        fi
        mv "$tmp" "$out"
        printf '%s\t%s\t%s\n' "$query" "$url" "$out" >> "$MANIFEST"
        return 0
    fi

    rm -f "$tmp" "$out"
    printf 'failed to fetch %s\n' "$url" >> "$ERROR_FILE"
    return 1
}

fetch_importgenius() {
    slug=$1
    query=$2
    url=$3
    tmp=$OUT_DIR/$slug.html.tmp
    out=$OUT_DIR/$slug.html

    if curl \
        -A "$IMPORTINFO_USER_AGENT" \
        -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
        -H "Accept-Language: en-US,en;q=0.9" \
        --retry 2 \
        --retry-delay 2 \
        --max-time 45 \
        -fsSL "$url" > "$tmp" 2>/dev/null
    then
        if ! looks_like_importgenius_shipment_page "$tmp"; then
            rm -f "$tmp" "$out"
            printf 'unexpected or blocked content from %s\n' "$url" >> "$ERROR_FILE"
            return 0
        fi
        mv "$tmp" "$out"
        printf '%s\t%s\t%s\n' "$query" "$url" "$out" >> "$MANIFEST"
        return 0
    fi

    rm -f "$tmp" "$out"
    printf 'failed to fetch %s\n' "$url" >> "$ERROR_FILE"
    return 1
}

fetch_importinfo \
    "importinfo-ceva-valve" \
    "ceva-valve" \
    "https://www.importinfo.com/search?s=CEVA%20C%2FO%20VALVE%20CORPORATION" || true
fetch_importinfo \
    "importinfo-ingram-valve" \
    "ingram-valve" \
    "https://www.importinfo.com/search?s=INGRAM%20MICRO%20C%2FO%20VALVE%20CORPORATION" || true
fetch_importinfo \
    "importinfo-tech-front-game-console" \
    "tech-front-game-console" \
    "https://www.importinfo.com/search?s=TECH-FRONT%20GAME%20CONSOLE%20VALVE" || true
fetch_importinfo \
    "importinfo-valve-corporation" \
    "valve-corporation-game-console" \
    "https://www.importinfo.com/search?s=VALVE%20CORPORATION%20GAME%20CONSOLE" || true
fetch_importgenius \
    "importgenius-ingram-valve" \
    "importgenius-ingram-valve" \
    "https://www.importgenius.com/importers/ingram-micro-c-o-valve-corporation" || true
fetch_importgenius \
    "importgenius-ceva-valve" \
    "importgenius-ceva-valve" \
    "https://www.importgenius.com/importers/ceva-c-o-valve-corporation" || true
fetch_importgenius \
    "importgenius-ceva-nl-valve" \
    "importgenius-ceva-nl-valve" \
    "https://www.importgenius.com/importers/ceva-nl-c-o-valve-corporation" || true
fetch_importgenius \
    "importgenius-valve-corp" \
    "importgenius-valve-corp" \
    "https://www.importgenius.com/importers/valve-corp" || true

python3 "$SCRIPT_DIR/parse_importinfo_shipments.py" \
    --manifest "$MANIFEST" \
    --report-dir "$REPORT_DIR"

echo "Saved customs shipment pages to $OUT_DIR"
echo "Saved customs shipment report to $REPORT_DIR/customs-shipments.md"
