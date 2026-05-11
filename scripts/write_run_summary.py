#!/usr/bin/env python3
import argparse
from pathlib import Path

MAX_LINE_LEN = 220
FILTER_TERMS = (
    "controller",
    "machine",
    "frame",
    "triton",
    "puck",
    "ibex",
    "unboxing",
    "coming",
    "2026",
    "pair",
    "firmware",
    "fremont",
    "deckard",
    "roy",
    "lilac",
    "xr",
    "vr",
    "dongle",
)
REJECT_TERMS = (
    "application_config",
    "data-config",
    "&quot;",
    "localized_",
)


def read_lines(path: Path):
    if not path.exists():
        return []
    return [line.rstrip("\n") for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]


def count(path: Path):
    return len(read_lines(path))


def first(path: Path, n: int):
    return read_lines(path)[:n]


def concise(line: str):
    trimmed = " ".join(line.split())
    if len(trimmed) > MAX_LINE_LEN:
        return trimmed[: MAX_LINE_LEN - 3] + "..."
    return trimmed


def filtered_first(path: Path, n: int):
    selected = []
    for line in read_lines(path):
        lowered = line.lower()
        if any(term in lowered for term in REJECT_TERMS):
            continue
        if path.name == "valve-key-lines.txt" and not any(term in lowered for term in FILTER_TERMS):
            continue
        selected.append(concise(line))
        if len(selected) >= n:
            break
    return selected


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


def count_block_reason(path: Path, reason: str):
    total = 0
    if not path.exists():
        return total
    for line in read_lines(path):
        parts = line.split("\t")
        if parts and parts[0] == reason:
            total += 1
    return total


def customs_status(reports: Path):
    key_lines = reports / "customs-shipments-key-lines.txt"
    errors = reports / "customs-shipments-errors.txt"
    report = reports / "customs-shipments.md"
    if not any(path.exists() for path in (key_lines, errors, report)):
        return "unavailable"
    if count(errors):
        return "blocked"
    return "available"


def build(run_dir: Path):
    reports = run_dir / "reports"
    compare = sorted(reports.glob("compare-vs-*.md"))
    compare_file = compare[-1] if compare else None

    discovered = count(reports / "discovered-visual-assets.tsv")
    retrieved = count(reports / "retrieved-visual-assets.tsv")
    blocked = count(reports / "blocked-visual-assets.tsv")
    session_required = count_block_reason(reports / "blocked-visual-assets.tsv", "session_required")

    lines = [
        f"# Run Summary: {run_dir.name}",
        "",
        f"Artifacts: `{run_dir}`",
        "",
        "## At A Glance",
        "",
        f"- Komodo blocked: `{'yes' if count(reports / 'komodo-errors.txt') else 'no'}`",
        f"- SteamKit/PICS blocked: `{'yes' if count(reports / 'steamkit-pics-errors.txt') else 'no'}`",
        f"- SteamDB blocked: `{'yes' if count(reports / 'steamdb-errors.txt') else 'no'}`",
        f"- SteamVR depot metadata blocked: `{'yes' if count(reports / 'steamvr-depots-errors.txt') else 'no'}`",
        f"- SteamOS mirror metadata blocked: `{'yes' if count(reports / 'steamos-mirror-errors.txt') else 'no'}`",
        f"- Valve blocked: `{'yes' if count(reports / 'valve-errors.txt') else 'no'}`",
        f"- Customs shipments status: `{customs_status(reports)}`",
        f"- Discovered visual assets: `{discovered}`",
        f"- Retrieved visual assets: `{retrieved}`",
        f"- Blocked visual assets: `{blocked}`",
        f"- Blocked assets requiring trusted session: `{session_required}`",
        "",
        "## Most Relevant Outputs",
        "",
        f"- Status draft: `{reports / 'status-draft.md'}`",
        f"- Discovered assets: `{reports / 'discovered-visual-assets.tsv'}`",
        f"- Retrieved assets: `{reports / 'retrieved-visual-assets.tsv'}`",
        f"- Blocked assets: `{reports / 'blocked-visual-assets.tsv'}`",
        f"- Manual retry URLs: `{reports / 'manual-asset-urls.txt'}`",
        f"- SteamKit/PICS packages: `{reports / 'steamkit-pics-packages.tsv'}`",
        f"- Customs shipments: `{reports / 'customs-shipments.md'}`",
    ]

    if compare_file:
        lines.append(f"- Comparison report: `{compare_file}`")

    lines.extend(["", "## Notable Lines", ""])

    notable = []
    notable.extend([f"- SteamKit/PICS: `{line}`" for line in filtered_first(reports / "steamkit-pics-key-lines.txt", 8)])
    notable.extend([f"- SteamDB: `{line}`" for line in filtered_first(reports / "steamdb-key-lines.txt", 5)])
    notable.extend([f"- SteamTracking: `{line}`" for line in filtered_first(reports / "steamtracking-pairing-focus.txt", 5)])
    notable.extend([f"- SteamVR depots: `{line}`" for line in filtered_first(reports / "steamvr-depots-key-lines.txt", 5)])
    notable.extend([f"- SteamOS mirror: `{line}`" for line in filtered_first(reports / "steamos-mirror-key-lines.txt", 5)])
    notable.extend([f"- Valve: `{line}`" for line in filtered_first(reports / "valve-key-lines.txt", 5)])
    notable.extend([f"- Customs shipments: `{line}`" for line in filtered_first(reports / "customs-shipments-key-lines.txt", 8)])
    notable.extend([f"- Asset blocked: `{line}`" for line in filtered_first(reports / "blocked-visual-assets.tsv", 5)])

    if notable:
        lines.extend(notable)
    else:
        lines.append("- No notable lines were extracted.")

    manual_urls = blocked_asset_urls(reports / "blocked-visual-assets.tsv", 10)
    lines.extend(["", "## Manual Follow-Up URLs", ""])
    if manual_urls:
        lines.extend([f"- `{url}`" for url in manual_urls])
    else:
        lines.append("- No blocked asset URLs were recorded in this run.")

    lines.extend(["", "## Next Human Step", "", "- Review this summary first, then open the detailed reports only if something changed or looks important.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Write a concise human-readable run summary.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output", help="Optional output path")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    output = Path(args.output) if args.output else run_dir / "reports" / "run-summary.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build(run_dir), encoding="utf-8")


if __name__ == "__main__":
    main()
