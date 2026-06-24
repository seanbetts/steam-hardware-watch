#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path

FRAME_APP_ID = "4165890"
FRAME_PACKAGE_IDS = {"1629484", "1629486"}
FRAME_KOMODO_BASELINE = "2026-05-27T16:53:46"
FRAME_STEAMDB_BASELINE_UPDATE = "5 May 2026 - 18:50:54 UTC"
MAX_LINE_LEN = 220


def read_text(path: Path):
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def read_lines(path: Path):
    return [line.rstrip("\n") for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_komodo_product_modified(path: Path):
    rows = []
    for line in read_lines(path):
        parts = line.split("\t")
        if parts[:2] == ["product", "modified"]:
            continue
        if len(parts) >= 2:
            rows.append({"product": parts[0], "modified": parts[1]})
    return rows


def concise(value: str):
    compact = " ".join((value or "").split())
    if len(compact) > MAX_LINE_LEN:
        return compact[: MAX_LINE_LEN - 3] + "..."
    return compact


def bullet_table_row(row, columns):
    values = []
    for column in columns:
        value = concise(row.get(column, ""))
        if value:
            values.append(f"{column}={value}")
    return "; ".join(values)


def frame_rows(rows, id_key="id"):
    return [
        row
        for row in rows
        if row.get("product") == "Steam Frame"
        or row.get(id_key) == FRAME_APP_ID
        or row.get(id_key) in FRAME_PACKAGE_IDS
        or row.get("package_id") in FRAME_PACKAGE_IDS
    ]


def machine_rows(rows, id_key="id"):
    return [row for row in rows if row.get("product") == "Steam Machine"]


def valve_frame_ready(rows):
    for row in frame_rows(rows):
        row_type = row.get("type")
        row_id = row.get("id")
        status = row.get("status")
        details = row.get("details", "")
        if row_type == "package" and row_id in FRAME_PACKAGE_IDS and status == "public":
            return True
        if row_type == "app" and row_id == FRAME_APP_ID:
            has_packages = "packages=" in details and "packages=;" not in details
            has_package_groups = "package_groups=0" not in details and "package_groups=" in details
            has_price = "price=" in details and not details.endswith("price=")
            if has_packages or has_package_groups or has_price:
                return True
    return False


def steamkit_frame_moved(rows):
    for row in frame_rows(rows):
        if row.get("changed_since_previous") == "yes":
            return True
        if row.get("type") == "package" and row.get("id") in FRAME_PACKAGE_IDS and row.get("status") == "available":
            return True
    return False


def steamdb_frame_moved(rows):
    for row in frame_rows(rows, id_key="package_id"):
        if row.get("status") and row.get("status") != "private_exists_only":
            return True
        if row.get("last_record_update") and row.get("last_record_update") != FRAME_STEAMDB_BASELINE_UPDATE:
            return True
    return False


def komodo_frame_moved(rows):
    for row in rows:
        if row.get("product") == "frame" and row.get("modified") and row.get("modified") != FRAME_KOMODO_BASELINE:
            return True
    return False


def key_lines(path: Path, terms, limit):
    selected = []
    for line in read_lines(path):
        lowered = line.lower()
        if any(term in lowered for term in terms):
            selected.append(concise(line))
        if len(selected) >= limit:
            break
    return selected


def customs_vr_lines(path: Path, limit):
    selected = []
    for line in read_lines(path):
        lowered = line.lower()
        if line.startswith("|") and any(term in lowered for term in ("virtual reality", "vr", "headset", "xr")):
            selected.append(concise(line))
        if len(selected) >= limit:
            break
    return selected


def latest_compare_file(reports: Path):
    compare_files = sorted(reports.glob("compare-vs-*.md"))
    if not compare_files:
        return None
    return compare_files[-1]


def build(run_dir: Path):
    reports = run_dir / "reports"
    valve_rows = read_tsv(reports / "valve-reservation-packages.tsv")
    steamkit_rows = read_tsv(reports / "steamkit-pics-packages.tsv")
    steamdb_rows = read_tsv(reports / "steamdb-reservation-packages.tsv")
    komodo_rows = read_komodo_product_modified(reports / "komodo-product-modified.tsv")

    valve_ready = valve_frame_ready(valve_rows)
    steamkit_moved = steamkit_frame_moved(steamkit_rows)
    steamdb_moved = steamdb_frame_moved(steamdb_rows)
    komodo_moved = komodo_frame_moved(komodo_rows)

    if valve_ready:
        verdict = "Steam Frame public readiness detected."
        reason = "Valve store/package data now exposes Frame package, package group, price, or purchase/reservation readiness."
    elif steamkit_moved or steamdb_moved:
        verdict = "Steam Frame backend movement detected, but public store readiness is not confirmed."
        reason = "Frame app/package metadata moved in SteamKit/PICS or SteamDB, while Valve public endpoints still need confirmation."
    elif komodo_moved:
        verdict = "Steam Frame site staging detected, but store/package readiness is not confirmed."
        reason = "Komodo Frame records moved without matching Valve package readiness."
    else:
        verdict = "No public Steam Frame readiness change detected."
        reason = "Frame app/package, public Valve endpoint, SteamDB, and Komodo checks do not show a launch-readiness move."

    lines = [
        f"# Steam Frame Focus: {run_dir.name}",
        "",
        "## Verdict",
        "",
        f"- {verdict}",
        f"- {reason}",
        "",
        "## Frame Critical Signals",
        "",
        f"- Frame app: `{FRAME_APP_ID}`",
        "- Frame packages: `1629484`, `1629486`",
        "",
        "### Valve Store / Package API",
    ]

    frame_valve_rows = frame_rows(valve_rows)
    if frame_valve_rows:
        for row in frame_valve_rows:
            lines.append(
                f"- `{bullet_table_row(row, ('type', 'product', 'id', 'status', 'name', 'release_or_price', 'details'))}`"
            )
    else:
        lines.append("- No Frame rows found in `valve-reservation-packages.tsv`.")

    lines.extend(["", "### SteamKit / PICS"])
    frame_steamkit_rows = frame_rows(steamkit_rows)
    if frame_steamkit_rows:
        for row in frame_steamkit_rows:
            lines.append(
                f"- `{bullet_table_row(row, ('type', 'product', 'id', 'status', 'changenumber', 'previous_changenumber', 'changed_since_previous', 'name', 'details'))}`"
            )
    else:
        lines.append("- No Frame rows found in `steamkit-pics-packages.tsv`.")

    lines.extend(["", "### SteamDB"])
    frame_steamdb_rows = frame_rows(steamdb_rows, id_key="package_id")
    if frame_steamdb_rows:
        for row in frame_steamdb_rows:
            lines.append(
                f"- `{bullet_table_row(row, ('product', 'package_id', 'last_record_update', 'last_changenumber', 'possible_apps', 'status'))}`"
            )
    else:
        lines.append("- No Frame rows found in `steamdb-reservation-packages.tsv`.")

    lines.extend(["", "### Komodo"])
    frame_komodo = [row for row in komodo_rows if row.get("product") == "frame"]
    if frame_komodo:
        for row in frame_komodo:
            lines.append(f"- `{bullet_table_row(row, ('product', 'modified'))}`")
    else:
        lines.append("- No Frame product timestamp row found.")
    for source in ("komodo-frame-sections.tsv", "komodo-frame-media.tsv"):
        path = reports / source
        count = len(read_lines(path))
        lines.append(f"- `{source}` rows: `{count}`")

    tracking_terms = ("frame", "deckard", "roy", "xr", "vr", "wireless adapter", "steam link")
    tracking_lines = key_lines(reports / "steamtracking-frame-signals-key-lines.txt", tracking_terms, 10)
    lines.extend(["", "### SteamTracking / GameTracking"])
    if tracking_lines:
        lines.extend([f"- `{line}`" for line in tracking_lines])
    else:
        lines.append("- No Frame-focused SteamTracking key lines found.")

    vr_terms = ("steam frame", "deckard", "roy", "wireless adapter", "steam link vr", "arm64", "linuxarm64")
    steamvr_lines = key_lines(reports / "steamvr-depots-key-lines.txt", vr_terms, 6)
    steamos_lines = key_lines(reports / "steamos-mirror-key-lines.txt", vr_terms, 6)
    lines.extend(["", "### SteamVR / SteamOS"])
    if steamvr_lines or steamos_lines:
        lines.extend([f"- SteamVR: `{line}`" for line in steamvr_lines])
        lines.extend([f"- SteamOS: `{line}`" for line in steamos_lines])
    else:
        lines.append("- No Frame-relevant SteamVR or SteamOS key lines found.")

    customs_lines = customs_vr_lines(reports / "customs-shipments.md", 6)
    lines.extend(["", "### Customs / Shipments"])
    if customs_lines:
        lines.extend([f"- `{line}`" for line in customs_lines])
    elif (reports / "customs-shipments-errors.txt").exists():
        lines.append("- Shipment check had errors; inspect `customs-shipments-errors.txt`.")
    else:
        lines.append("- No VR/XR/headset shipment rows surfaced in the shipment report.")

    lines.extend(["", "## Background Comparator Signals", ""])
    machine_valve_rows = machine_rows(valve_rows)
    machine_steamkit_rows = [
        row for row in machine_rows(steamkit_rows) if row.get("changed_since_previous") == "yes"
    ]
    if machine_valve_rows:
        lines.append("- Steam Machine is now a launched comparator, not the active target.")
        for row in machine_valve_rows[:6]:
            lines.append(
                f"- Machine Valve: `{bullet_table_row(row, ('type', 'id', 'status', 'name', 'release_or_price', 'details'))}`"
            )
    if machine_steamkit_rows:
        for row in machine_steamkit_rows[:6]:
            lines.append(
                f"- Machine SteamKit moved: `{bullet_table_row(row, ('type', 'id', 'changenumber', 'previous_changenumber', 'changed_since_previous', 'details'))}`"
            )
    if not machine_valve_rows and not machine_steamkit_rows:
        lines.append("- No Machine comparator rows were available in the saved reports.")

    compare_file = latest_compare_file(reports)
    lines.extend(["", "## Next Checks", ""])
    lines.append("- Recheck SteamKit/PICS and Valve `appdetails` / `packagedetails` first.")
    lines.append("- Treat SteamTracking or Komodo Frame movement as staging context until package/API visibility changes.")
    lines.append("- Keep monitoring VR-labelled shipment rows as corroboration, not launch confirmation.")
    if compare_file:
        lines.append(f"- Cross-check material deltas in `{compare_file}`.")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Write a Steam Frame focused report from saved watch artifacts.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output", help="Optional output path")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    output = Path(args.output) if args.output else run_dir / "reports" / "frame-focus.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build(run_dir), encoding="utf-8")


if __name__ == "__main__":
    main()
