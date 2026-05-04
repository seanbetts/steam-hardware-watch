#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_lines(path: Path):
    if not path.exists():
        return []
    return [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines()]


def compare_products(prev_dir: Path, curr_dir: Path):
    results = []
    for label, name in [
        ("controller", "product-controller-jpy.json"),
        ("machine", "product-machine-jpy.json"),
        ("frame", "product-frame-jpy.json"),
    ]:
        prev = read_json(prev_dir / "api" / "komodo" / name)
        curr = read_json(curr_dir / "api" / "komodo" / name)
        if not prev or not curr:
            continue
        prev_mod = prev.get("modified")
        curr_mod = curr.get("modified")
        if prev_mod != curr_mod:
            results.append(f"- Komodo {label} product modified changed: `{prev_mod}` -> `{curr_mod}`")
    return results


def parse_section_tsv(path: Path):
    rows = {}
    for line in read_lines(path):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 5:
            continue
        sid, date, modified, slug, title = parts[:5]
        rows[sid] = {
            "date": date,
            "modified": modified,
            "slug": slug,
            "title": title,
        }
    return rows


def compare_sections(prev_dir: Path, curr_dir: Path, label: str, filename: str):
    prev = parse_section_tsv(prev_dir / "reports" / filename)
    curr = parse_section_tsv(curr_dir / "reports" / filename)
    lines = []

    added_ids = sorted(set(curr) - set(prev), key=int)
    removed_ids = sorted(set(prev) - set(curr), key=int)
    shared_ids = sorted(set(curr) & set(prev), key=int)

    for sid in added_ids:
        row = curr[sid]
        lines.append(f"- {label} section added: `{sid}` `{row['slug']}` modified `{row['modified']}`")
    for sid in removed_ids:
        row = prev[sid]
        lines.append(f"- {label} section removed: `{sid}` `{row['slug']}`")
    for sid in shared_ids:
        if prev[sid]["modified"] != curr[sid]["modified"]:
            lines.append(
                f"- {label} section updated: `{sid}` `{curr[sid]['slug']}` `{prev[sid]['modified']}` -> `{curr[sid]['modified']}`"
            )
    return lines


def parse_tsv_set(path: Path):
    return {line for line in read_lines(path) if line.strip()}


def compare_report_sets(prev_dir: Path, curr_dir: Path, label: str, filename: str):
    prev = parse_tsv_set(prev_dir / "reports" / filename)
    curr = parse_tsv_set(curr_dir / "reports" / filename)
    lines = []
    for line in sorted(curr - prev):
        lines.append(f"- {label} added: `{line}`")
    for line in sorted(prev - curr):
        lines.append(f"- {label} removed: `{line}`")
    return lines


def compare_text_lines(prev_dir: Path, curr_dir: Path, label: str, filename: str, limit: int = 20):
    prev = parse_tsv_set(prev_dir / "reports" / filename)
    curr = parse_tsv_set(curr_dir / "reports" / filename)
    added = sorted(curr - prev)[:limit]
    removed = sorted(prev - curr)[:limit]
    lines = []
    for line in added:
        lines.append(f"- {label} added line: `{line}`")
    for line in removed:
        lines.append(f"- {label} removed line: `{line}`")
    return lines


def build_summary(prev_dir: Path, curr_dir: Path):
    lines = [
        "# Run Comparison",
        "",
        f"Previous: `{prev_dir}`",
        f"Current: `{curr_dir}`",
        "",
        "## Material Deltas",
        "",
    ]

    deltas = []
    deltas.extend(compare_products(prev_dir, curr_dir))
    deltas.extend(compare_sections(prev_dir, curr_dir, "Komodo controller", "komodo-controller-sections.tsv"))
    deltas.extend(compare_sections(prev_dir, curr_dir, "Komodo machine", "komodo-machine-sections.tsv"))
    deltas.extend(compare_sections(prev_dir, curr_dir, "Komodo frame", "komodo-frame-sections.tsv"))
    deltas.extend(compare_report_sets(prev_dir, curr_dir, "Komodo controller media", "komodo-controller-media-interesting.tsv"))
    deltas.extend(compare_report_sets(prev_dir, curr_dir, "Komodo machine media", "komodo-machine-media.tsv"))
    deltas.extend(compare_report_sets(prev_dir, curr_dir, "Komodo frame media", "komodo-frame-media.tsv"))
    deltas.extend(compare_text_lines(prev_dir, curr_dir, "SteamDB", "steamdb-key-lines.txt"))
    deltas.extend(compare_text_lines(prev_dir, curr_dir, "SteamVR depots", "steamvr-depots-key-lines.txt"))
    deltas.extend(compare_text_lines(prev_dir, curr_dir, "SteamOS mirror", "steamos-mirror-key-lines.txt"))
    deltas.extend(compare_text_lines(prev_dir, curr_dir, "Valve endpoint", "valve-key-lines.txt"))

    if deltas:
        lines.extend(deltas)
    else:
        lines.append("- No material deltas detected in the compared reports.")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This comparison is intentionally conservative.",
            "- It only covers artifacts produced by the helper scripts.",
            "- Review raw files when a line item looks ambiguous or noisy.",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Compare two Steam hardware watch run directories.")
    parser.add_argument("--previous", required=True, help="Previous run directory")
    parser.add_argument("--current", required=True, help="Current run directory")
    parser.add_argument("--output", required=True, help="Path to write markdown summary")
    args = parser.parse_args()

    prev_dir = Path(args.previous)
    curr_dir = Path(args.current)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_summary(prev_dir, curr_dir), encoding="utf-8")


if __name__ == "__main__":
    main()
