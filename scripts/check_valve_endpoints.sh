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
: > "$REPORT_DIR/valve-reservation-packages.tsv"

fetch_page() {
  name="$1"
  url="$2"
  if ! curl -A 'Mozilla/5.0' --retry 2 --retry-delay 2 --max-time 45 -fsSL "$url" > "$OUT_DIR/$name.html" 2>/dev/null; then
    printf '%s\n' "failed to fetch $url" >> "$ERROR_FILE"
    rm -f "$OUT_DIR/$name.html"
    return 1
  fi
}

fetch_json() {
  name="$1"
  url="$2"
  if ! curl -A 'Mozilla/5.0' --retry 2 --retry-delay 2 --max-time 45 -fsSL "$url" > "$OUT_DIR/$name.json" 2>/dev/null; then
    printf '%s\n' "failed to fetch $url" >> "$ERROR_FILE"
    rm -f "$OUT_DIR/$name.json"
    return 1
  fi
}

fetch_page "steamdeck-site" "https://www.steamdeck.com/" || true
fetch_page "steam-support-deck" "https://help.steampowered.com/en/wizard/HelpWithSteamDeck" || true
fetch_page "steam-controller-store" "https://store.steampowered.com/app/4165870/" || true
fetch_page "steam-hardware-root" "https://steampowered.com/hardware" || true

for appid in 4165870 4165890 4165910; do
  fetch_json "appdetails-$appid-us" "https://store.steampowered.com/api/appdetails?appids=$appid&cc=us&l=en" || true
done

for packageid in 1558609 1629446 1629447 1629458 1629460 1629484 1629486; do
  fetch_json "packagedetails-$packageid-us" "https://store.steampowered.com/api/packagedetails?packageids=$packageid&cc=us&l=en" || true
done

python3 - "$OUT_DIR" "$REPORT_DIR/valve-reservation-packages.tsv" <<'PY'
import json
import sys
from pathlib import Path


out_dir = Path(sys.argv[1])
report_path = Path(sys.argv[2])

apps = {
    "4165870": "Steam Controller",
    "4165890": "Steam Frame",
    "4165910": "Steam Machine",
}
packages = {
    "1558609": "Steam Controller",
    "1629446": "Steam Machine",
    "1629447": "Steam Machine",
    "1629458": "Steam Machine",
    "1629460": "Steam Machine",
    "1629484": "Steam Frame",
    "1629486": "Steam Frame",
}


def clean(value):
    if value is None:
        return ""
    return str(value).replace("\t", " ").replace("\n", " ").strip()


def read_json(path):
    if not path.exists():
        return None, "missing"
    try:
        return json.loads(path.read_text(encoding="utf-8")), ""
    except Exception as exc:
        return None, f"invalid json: {exc}"


rows = [["type", "product", "id", "status", "name", "release_or_price", "details"]]

for appid, product in apps.items():
    payload, error = read_json(out_dir / f"appdetails-{appid}-us.json")
    entry = payload.get(appid, {}) if isinstance(payload, dict) else {}
    success = entry.get("success") is True
    data = entry.get("data") if isinstance(entry.get("data"), dict) else {}
    status = "public" if success else "unavailable"
    if error:
        status = error
    name = data.get("name", "")
    price = ""
    price_overview = data.get("price_overview")
    if isinstance(price_overview, dict):
        price = price_overview.get("final_formatted", "")
    release_date = data.get("release_date")
    release_or_price = price
    coming_soon = ""
    if isinstance(release_date, dict):
        release_or_price = release_or_price or release_date.get("date", "")
        coming_soon = release_date.get("coming_soon", "")
    package_ids = data.get("packages") if isinstance(data.get("packages"), list) else []
    package_groups = data.get("package_groups") if isinstance(data.get("package_groups"), list) else []
    details = (
        f"packages={','.join(str(package_id) for package_id in package_ids)}; "
        f"package_groups={len(package_groups)}; "
        f"coming_soon={coming_soon}; "
        f"price={price}"
    )
    rows.append(["app", product, appid, status, name, release_or_price, details])

for packageid, product in packages.items():
    payload, error = read_json(out_dir / f"packagedetails-{packageid}-us.json")
    entry = payload.get(packageid, {}) if isinstance(payload, dict) else {}
    success = entry.get("success") is True
    status = "public" if success else "private"
    if error:
        status = error
    data = entry.get("data") if isinstance(entry.get("data"), dict) else {}
    name = data.get("name", "")
    price = ""
    package_price = data.get("price")
    if isinstance(package_price, dict):
        price = package_price.get("final_formatted", "")
    apps_detail = []
    for app in data.get("apps", []) if isinstance(data.get("apps"), list) else []:
        if isinstance(app, dict):
            app_id = app.get("id", "")
            app_name = app.get("name", "")
            apps_detail.append(f"{app_id}:{app_name}")
    details = f"apps={','.join(apps_detail)}" if success else "packagedetails success:false"
    rows.append(["package", product, packageid, status, name, price, details])

report_path.write_text(
    "\n".join("\t".join(clean(value) for value in row) for row in rows) + "\n",
    encoding="utf-8",
)
PY

{
  printf '%s\n' "Reservation package API snapshot:"
  sed -n '1,40p' "$REPORT_DIR/valve-reservation-packages.tsv"
  printf '\n%s\n' "HTML key matches:"
} > "$REPORT_DIR/valve-key-lines.txt"

rg -n -o -g '*.html' "Steam Controller|Steam Machine|Steam Frame|coming soon|manual|safety|warranty|preorder|release" \
  "$OUT_DIR" | sort -u \
  >> "$REPORT_DIR/valve-key-lines.txt" || true

printf '%s\n' \
  "Saved Valve pages to $OUT_DIR" \
  "Saved matching lines to $REPORT_DIR/valve-key-lines.txt" \
  "Saved reservation package report to $REPORT_DIR/valve-reservation-packages.tsv"
