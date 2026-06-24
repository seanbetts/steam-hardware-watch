#!/usr/bin/env python3
import argparse
from pathlib import Path


def read_lines(path: Path):
    if not path.exists():
        return []
    return [line.rstrip("\n") for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()]


def first_n_nonempty(path: Path, n: int):
    return [line for line in read_lines(path) if line.strip()][:n]


def count_lines(path: Path):
    return len([line for line in read_lines(path) if line.strip()])


def has_nonempty(path: Path):
    return count_lines(path) > 0


def blocked_asset_urls(path: Path, n: int):
    urls = []
    if not path.exists():
        return urls
    for line in read_lines(path):
        parts = line.split("\t")
        if len(parts) > 4 and parts[4].startswith("http"):
            urls.append(parts[4])
        if len(urls) >= n:
            break
    return urls


def build_draft(run_dir: Path):
    reports = run_dir / "reports"
    run_date = run_dir.name

    compare_files = sorted(reports.glob("compare-vs-*.md"))
    compare_file = compare_files[-1] if compare_files else None

    compare_lines = []
    if compare_file:
        compare_lines = [line for line in read_lines(compare_file) if line.startswith("- ")][:12]

    frame_focus_lines = first_n_nonempty(reports / "frame-focus.md", 12)
    komodo_mods = first_n_nonempty(reports / "komodo-product-modified.tsv", 10)
    steamkit_lines = first_n_nonempty(reports / "steamkit-pics-key-lines.txt", 10)
    steamdb_lines = first_n_nonempty(reports / "steamdb-key-lines.txt", 8)
    valve_lines = first_n_nonempty(reports / "valve-key-lines.txt", 8)
    tracking_lines = first_n_nonempty(reports / "steamtracking-pairing-focus.txt", 8)
    hardware_signal_lines = first_n_nonempty(
        reports / "steamtracking-hardware-signals-key-lines.txt", 8
    )
    frame_signal_lines = first_n_nonempty(
        reports / "steamtracking-frame-signals-key-lines.txt", 12
    )
    machine_signal_lines = first_n_nonempty(
        reports / "steamtracking-machine-signals-key-lines.txt", 12
    )
    client_manifest_lines = first_n_nonempty(
        reports / "steamtracking-client-manifests-key-lines.txt", 8
    )
    steamvr_lines = first_n_nonempty(reports / "steamvr-depots-key-lines.txt", 8)
    steamos_lines = first_n_nonempty(reports / "steamos-mirror-key-lines.txt", 8)
    customs_key_lines_path = reports / "customs-shipments-key-lines.txt"
    customs_errors_path = reports / "customs-shipments-errors.txt"
    customs_report_path = reports / "customs-shipments.md"
    customs_lines = first_n_nonempty(customs_key_lines_path, 8)
    customs_outputs_available = any(
        path.exists()
        for path in (customs_key_lines_path, customs_errors_path, customs_report_path)
    )
    discovered_count = count_lines(reports / "discovered-visual-assets.tsv")
    retrieved_count = count_lines(reports / "retrieved-visual-assets.tsv")
    blocked_count = count_lines(reports / "blocked-visual-assets.tsv")
    manual_urls = blocked_asset_urls(reports / "blocked-visual-assets.tsv", 10)
    komodo_blocked = has_nonempty(reports / "komodo-errors.txt")
    steamkit_blocked = has_nonempty(reports / "steamkit-pics-errors.txt")
    steamdb_blocked = has_nonempty(reports / "steamdb-errors.txt")
    steamvr_blocked = has_nonempty(reports / "steamvr-depots-errors.txt")
    steamos_blocked = has_nonempty(reports / "steamos-mirror-errors.txt")
    valve_blocked = has_nonempty(reports / "valve-errors.txt")
    customs_blocked = has_nonempty(customs_errors_path)

    lines = [
        f"# Status Draft: {run_date}",
        "",
        "## Suggested `status/current.md` Update",
        "",
        f"Last updated: `{run_date}`",
        "",
        "### Observed Changes Since Previous Run",
        "",
    ]

    if compare_lines:
        lines.extend(compare_lines)
    else:
        lines.append("- No comparison report was available.")

    lines.extend(
        [
            "",
            "### Source Snapshot Draft",
            "",
            "#### Steam Frame Focus",
        ]
    )
    if frame_focus_lines:
        lines.extend([f"- `{line}`" for line in frame_focus_lines])
    else:
        lines.append("- No Steam Frame focused report found.")

    lines.extend(
        [
            "",
            "#### Komodo",
        ]
    )
    if komodo_blocked:
        lines.append("- Komodo was blocked or partially unavailable in this run. See `komodo-errors.txt`.")
    elif komodo_mods:
        lines.extend([f"- `{line}`" for line in komodo_mods])
    else:
        lines.append("- No Komodo product summary found.")
    lines.append(f"- Discovered visual assets: `{discovered_count}`")
    lines.append(f"- Retrieved visual assets: `{retrieved_count}`")
    lines.append(f"- Blocked visual assets: `{blocked_count}`")

    lines.extend(["", "#### SteamKit / PICS"])
    if steamkit_blocked:
        lines.append("- SteamKit/PICS was unavailable or failed in this run. See `steamkit-pics-errors.txt`.")
    if steamkit_lines:
        lines.extend([f"- `{line}`" for line in steamkit_lines])
    elif not steamkit_blocked:
        lines.append("- No SteamKit/PICS key-line report found.")

    lines.extend(["", "#### SteamDB"])
    if steamdb_blocked:
        lines.append("- SteamDB had blocked or failed fetches in this run. See `steamdb-errors.txt`.")
    elif steamdb_lines:
        lines.extend([f"- `{line}`" for line in steamdb_lines])
    else:
        lines.append("- No SteamDB key-line report found.")

    lines.extend(["", "#### SteamTracking / GameTracking"])
    if tracking_lines:
        lines.extend([f"- `{line}`" for line in tracking_lines])
    else:
        lines.append("- No focused SteamTracking report found.")
    if frame_signal_lines:
        lines.extend(["", "Steam Frame client signal focus:"])
        lines.extend([f"- `{line}`" for line in frame_signal_lines])
    if machine_signal_lines:
        lines.extend(["", "Steam Machine client signal focus:"])
        lines.extend([f"- `{line}`" for line in machine_signal_lines])
    if hardware_signal_lines:
        lines.extend(["", "Steam hardware backend signal focus:"])
        lines.extend([f"- `{line}`" for line in hardware_signal_lines])
    if client_manifest_lines:
        lines.extend(["", "Steam client manifest focus:"])
        lines.extend([f"- `{line}`" for line in client_manifest_lines])

    lines.extend(["", "#### SteamVR Depots"])
    if steamvr_blocked:
        lines.append("- SteamVR depot metadata was blocked or partially unavailable in this run. See `steamvr-depots-errors.txt`.")
    if steamvr_lines:
        lines.extend([f"- `{line}`" for line in steamvr_lines])
    elif not steamvr_blocked:
        lines.append("- No SteamVR depot key-line report found.")

    lines.extend(["", "#### SteamOS Package Mirror"])
    if steamos_blocked:
        lines.append("- SteamOS package mirror metadata was blocked or partially unavailable in this run. See `steamos-mirror-errors.txt`.")
    if steamos_lines:
        lines.extend([f"- `{line}`" for line in steamos_lines])
    elif not steamos_blocked:
        lines.append("- No SteamOS mirror key-line report found.")

    lines.extend(["", "#### Valve Support / CDN"])
    if valve_blocked:
        lines.append("- Some Valve endpoint fetches failed in this run. See `valve-errors.txt`.")
    elif valve_lines:
        lines.extend([f"- `{line}`" for line in valve_lines])
    else:
        lines.append("- No Valve key-line report found.")

    lines.extend(["", "#### Customs / Shipments"])
    if not customs_outputs_available:
        lines.append("- Customs shipment outputs were not generated or are unavailable for this run.")
    elif customs_blocked and customs_lines:
        lines.append("- Customs shipment rows were captured, but some source fetches failed or were blocked. See `customs-shipments-errors.txt`.")
    elif customs_blocked:
        lines.append("- Customs shipment fetches failed or were partially blocked in this run. See `customs-shipments-errors.txt`.")
    if customs_lines:
        lines.extend([f"- `{line}`" for line in customs_lines])
    elif customs_outputs_available and not customs_blocked:
        lines.append("- No relevant customs shipment rows found.")

    lines.extend(
        [
            "",
            "### Analyst Judgment Needed",
            "",
            "- Price confidence:",
            "- Release date confidence:",
            "- Same-time launch confidence:",
            "",
            "## Suggested Run Note Additions",
            "",
            f"- Artifacts live in `{run_dir}`",
            f"- Discovered visual assets: `{reports / 'discovered-visual-assets.tsv'}`",
            f"- Retrieved visual assets: `{reports / 'retrieved-visual-assets.tsv'}`",
            f"- Blocked visual assets: `{reports / 'blocked-visual-assets.tsv'}`",
            f"- Manual retry URLs: `{reports / 'manual-asset-urls.txt'}`",
            f"- Customs shipments: `{reports / 'customs-shipments.md'}`",
        ]
    )

    if compare_file:
        lines.append(f"- Comparison report: `{compare_file}`")

    if manual_urls:
        lines.extend(["", "- Manual retry candidates:"])
        lines.extend([f"- `{url}`" for url in manual_urls])

    lines.extend(
        [
            "",
            "- Summarize only material deltas from the comparison report.",
            "- If new visual assets were downloaded, call out the most meaningful ones explicitly.",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Draft a status update from a run directory.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output", help="Optional output path")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    output = Path(args.output) if args.output else run_dir / "reports" / "status-draft.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_draft(run_dir), encoding="utf-8")


if __name__ == "__main__":
    main()
