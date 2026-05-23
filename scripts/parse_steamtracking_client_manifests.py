#!/usr/bin/env python3
import argparse
import csv
import re
import shutil
from pathlib import Path


WATCHED_MANIFESTS = (
    "steam_client_beta_linuxarm64",
    "steam_client_publicbeta_linuxarm64",
    "steam_client_publicbeta_ubuntu12",
    "steam_client_publicbeta_win64",
    "steam_client_publicbeta_osx",
    "steamdeck_publicbeta",
    "steam_client_win64",
    "steam_client_ubuntu12",
    "steam_client_osx",
    "steamdeck_stable",
)

FOCUS_BLOCKS = (
    "bins_hardware_linuxarm64",
    "bins_linuxarm64",
    "steam_linuxarm64",
    "runtime_steamrt_linuxarm64",
    "bins_steamrt_linuxarm64",
    "bins_codecs_linuxarm64",
    "bins_misc_linuxarm64",
    "webkit_linuxarm64",
    "sdl3_linuxarm64",
    "bins_hardware_all",
)

OUTPUT_FIELDS = (
    "manifest",
    "arch",
    "version",
    "block",
    "file",
    "size",
    "sha2",
    "changed_since_previous",
    "previous_version",
    "previous_file",
    "previous_size",
    "previous_sha2",
)


def parse_manifest(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    arch_match = re.match(r'\s*"([^"]+)"', text)
    version_match = re.search(r'"version"\s+"([^"]+)"', text)
    blocks = {}
    current = None
    for line in text.splitlines():
        block_match = re.match(r'\s*"([^"]+)"\s*$', line)
        if block_match:
            current = block_match.group(1)
            blocks[current] = {}
            continue
        if current:
            field_match = re.match(r'\s*"([^"]+)"\s+"([^"]*)"', line)
            if field_match:
                blocks[current][field_match.group(1)] = field_match.group(2)
    return {
        "arch": arch_match.group(1) if arch_match else "",
        "version": version_match.group(1) if version_match else "",
        "blocks": blocks,
    }


def find_previous_report(run_dir: Path):
    parent = run_dir.parent
    if not parent.exists():
        return None
    previous = None
    for candidate in sorted(parent.glob("????-??-??")):
        if candidate == run_dir:
            continue
        if candidate.name < run_dir.name:
            previous = candidate
    if not previous:
        return None
    path = previous / "reports" / "steamtracking-client-manifests.tsv"
    return path if path.exists() else None


def load_previous(path: Path | None):
    if not path or not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return {(row["manifest"], row["block"]): row for row in reader}


def changed(row, previous):
    prior = previous.get((row["manifest"], row["block"]))
    if not prior:
        return "new"
    if row["block"] == "__manifest__":
        return "yes" if row["version"] != prior.get("version", "") else "no"
    for field in ("file", "size", "sha2"):
        if row[field] != prior.get(field, ""):
            return "yes"
    return "no"


def build_rows(tracking_dir: Path, previous):
    manifest_dir = tracking_dir / "ClientManifest"
    rows = []
    for manifest in WATCHED_MANIFESTS:
        path = manifest_dir / manifest
        if not path.exists():
            continue
        parsed = parse_manifest(path)
        manifest_row = {
            "manifest": manifest,
            "arch": parsed["arch"],
            "version": parsed["version"],
            "block": "__manifest__",
            "file": "",
            "size": "",
            "sha2": "",
            "changed_since_previous": "",
            "previous_version": "",
            "previous_file": "",
            "previous_size": "",
            "previous_sha2": "",
        }
        prior = previous.get((manifest, "__manifest__"), {})
        manifest_row["previous_version"] = prior.get("version", "")
        manifest_row["changed_since_previous"] = changed(manifest_row, previous)
        rows.append(manifest_row)

        for block in FOCUS_BLOCKS:
            values = parsed["blocks"].get(block)
            if not values:
                continue
            row = {
                "manifest": manifest,
                "arch": parsed["arch"],
                "version": parsed["version"],
                "block": block,
                "file": values.get("file", ""),
                "size": values.get("size", ""),
                "sha2": values.get("sha2", ""),
                "changed_since_previous": "",
                "previous_version": "",
                "previous_file": "",
                "previous_size": "",
                "previous_sha2": "",
            }
            prior = previous.get((manifest, block), {})
            row["previous_version"] = prior.get("version", "")
            row["previous_file"] = prior.get("file", "")
            row["previous_size"] = prior.get("size", "")
            row["previous_sha2"] = prior.get("sha2", "")
            row["changed_since_previous"] = changed(row, previous)
            rows.append(row)
    return rows


def write_tsv(rows, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_key_lines(rows, path: Path):
    focus_manifests = {"steam_client_beta_linuxarm64", "steam_client_publicbeta_linuxarm64"}
    focus_blocks = {"__manifest__", "bins_hardware_linuxarm64", "bins_linuxarm64", "steam_linuxarm64", "runtime_steamrt_linuxarm64"}
    lines = []
    for row in rows:
        if row["manifest"] not in focus_manifests or row["block"] not in focus_blocks:
            continue
        if row["block"] == "__manifest__":
            lines.append(
                f"{row['manifest']} version={row['version']} arch={row['arch']} changed={row['changed_since_previous']} previous={row['previous_version']}"
            )
        else:
            lines.append(
                f"{row['manifest']} block={row['block']} version={row['version']} file={row['file']} size={row['size']} changed={row['changed_since_previous']} previous_file={row['previous_file']}"
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_markdown(rows, path: Path):
    lines = [
        "# SteamTracking Client Manifests",
        "",
        "Focused Steam client channel manifest snapshot for ARM64 and hardware package movement.",
        "",
        "| Manifest | Arch | Version | Block | File | Size | Changed |",
        "| --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        if row["manifest"] not in ("steam_client_beta_linuxarm64", "steam_client_publicbeta_linuxarm64"):
            continue
        lines.append(
            "| "
            + " | ".join(
                (
                    row["manifest"],
                    row["arch"],
                    row["version"],
                    row["block"],
                    row["file"],
                    row["size"],
                    row["changed_since_previous"],
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `steam_client_beta_linuxarm64` is high signal for possible ARM64 Steam hardware monitoring.",
            "- `bins_hardware_linuxarm64`, `steam_linuxarm64`, and Steam Runtime ARM64 blocks are the highest-value fields.",
            "- Manifest movement is not launch confirmation without Valve store/package readiness.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def copy_raw_manifests(tracking_dir: Path, output_dir: Path):
    source_dir = tracking_dir / "ClientManifest"
    output_dir.mkdir(parents=True, exist_ok=True)
    for manifest in WATCHED_MANIFESTS:
        source = source_dir / manifest
        if source.exists():
            shutil.copyfile(source, output_dir / manifest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--tracking-dir", required=True, type=Path)
    parser.add_argument("--previous-report", type=Path)
    args = parser.parse_args()

    reports = args.run_dir / "reports"
    raw_dir = args.run_dir / "api" / "steamtracking" / "client-manifests"
    previous = load_previous(args.previous_report or find_previous_report(args.run_dir))
    rows = build_rows(args.tracking_dir, previous)
    copy_raw_manifests(args.tracking_dir, raw_dir)
    write_tsv(rows, reports / "steamtracking-client-manifests.tsv")
    write_key_lines(rows, reports / "steamtracking-client-manifests-key-lines.txt")
    write_markdown(rows, reports / "steamtracking-client-manifests.md")


if __name__ == "__main__":
    main()
