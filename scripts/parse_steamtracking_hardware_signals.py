#!/usr/bin/env python3
import argparse
import csv
import re
from pathlib import Path


SEARCH_ROOTS = (
    "ClientExtracted",
    "ClientManifest",
    "Protobufs",
    "ProtobufsWebui",
    "Random",
    "Strings",
    "c/ClientExtracted",
)

SKIP_SUFFIXES = {
    ".avif",
    ".bmp",
    ".gif",
    ".gz",
    ".jpg",
    ".jpeg",
    ".mp4",
    ".png",
    ".webm",
    ".zip",
}

HARDWARE_RE = re.compile(
    r"Steam\s*Machine|SteamMachine|k_ESteamMachine|Steam\s*Frame|SteamFrame|k_ESteamFrame|"
    r"Steam\s*Controller|Triton|Ibex|Puck|Fremont|Deckard|Roy|"
    r"4165910|4165890|1629446|1629447|1629458|1629460|1629484|1629486",
    re.IGNORECASE,
)

SIGNAL_RE = re.compile(
    r"GuidedTour|WelcomeTour|Welcome|Tour|OOBE|onboarding|first.run|reservation|reserve|"
    r"preorder|pre-order|purchase|availability|microSD|SDCard|compatibility|verified|"
    r"pair|firmware|dongle|adapter|package|manifest",
    re.IGNORECASE,
)

FRAME_RE = re.compile(r"Steam\s*Frame|SteamFrame|steamframe|FrameVerified|FrameGames", re.IGNORECASE)

FRAME_PRIORITY_RE = re.compile(
    r"WelcomeToSteamFrame|GuidedTour_SteamFrame|SteamFrameWirelessAdapterDialog|"
    r"controller_steamframe_pair|Settings_RemotePlay_WifiAPSection|"
    r"Settings_Internet_Limit_Connection_Lower_Bands|LibraryTab_FrameVerified|"
    r"steamFrameVerifiedApps|FrameGames|skip_steamframe_pairing_dialog|"
    r"k_EAppTestType_SteamFrameCompatibilityReview",
    re.IGNORECASE,
)

MACHINE_RE = re.compile(r"Steam\s*Machine|SteamMachine|steammachine", re.IGNORECASE)

MACHINE_PRIORITY_RE = re.compile(
    r"GuidedTour_SteamMachine|WelcomeToSteamMachine|GuidedTour_SDCard_Title_SteamMachine|"
    r"SteamMachine_TestResult|SteamMachineVerified|SteamMachineCompatibility",
    re.IGNORECASE,
)


def iter_files(tracking_dir: Path):
    for root in SEARCH_ROOTS:
        base = tracking_dir / root
        if not base.exists():
            continue
        if base.is_file():
            yield base
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            yield path


def classify(line: str):
    hardware = HARDWARE_RE.search(line)
    signal = SIGNAL_RE.search(line)
    if not hardware or not signal:
        return ""
    if re.search(r"GuidedTour|Welcome|Tour|OOBE|onboarding", line, re.IGNORECASE):
        return "setup-tour"
    if re.search(r"reservation|reserve|preorder|pre-order|purchase|availability|package", line, re.IGNORECASE):
        return "commerce"
    if re.search(r"pair|firmware|dongle|adapter|Triton|Ibex|Puck", line, re.IGNORECASE):
        return "controller"
    if re.search(r"compatibility|verified", line, re.IGNORECASE):
        return "compatibility"
    return "hardware"


def build_rows(tracking_dir: Path):
    rows = []
    for path in iter_files(tracking_dir):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel_path = path.relative_to(tracking_dir).as_posix()
        for line_number, line in enumerate(text.splitlines(), start=1):
            category = classify(line)
            if not category:
                continue
            rows.append(
                {
                    "category": category,
                    "path": rel_path,
                    "line": str(line_number),
                    "text": line.strip(),
                }
            )
    return rows


def write_tsv(rows, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("category", "path", "line", "text"), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_key_lines(rows, path: Path):
    lines = []
    seen = set()
    for row in rows:
        line = f"{row['category']}\t{row['path']}:{row['line']}\t{row['text']}"
        if line in seen:
            continue
        seen.add(line)
        lines.append(line)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def frame_category(row):
    text = row["text"]
    if not (FRAME_RE.search(text) or FRAME_RE.search(row["path"])):
        return ""
    if not FRAME_PRIORITY_RE.search(text):
        return ""
    if re.search(r"WelcomeToSteamFrame|GuidedTour_SteamFrame", text, re.IGNORECASE):
        return "frame-setup"
    if re.search(
        r"SteamFrameWirelessAdapterDialog|controller_steamframe_pair|"
        r"Settings_RemotePlay_WifiAPSection|Settings_Internet_Limit_Connection_Lower_Bands|"
        r"skip_steamframe_pairing_dialog",
        text,
        re.IGNORECASE,
    ):
        return "frame-pairing"
    if re.search(
        r"LibraryTab_FrameVerified|steamFrameVerifiedApps|FrameGames|"
        r"k_EAppTestType_SteamFrameCompatibilityReview",
        text,
        re.IGNORECASE,
    ):
        return "frame-compatibility"
    return "frame"


def write_frame_key_lines(rows, path: Path):
    priority = {
        "frame-setup": 0,
        "frame-pairing": 1,
        "frame-compatibility": 2,
        "frame": 3,
    }
    lines = []
    seen = set()
    def sort_key(row):
        return (priority.get(frame_category(row), 99), row["path"], int(row["line"]), row["text"])

    for row in sorted(rows, key=sort_key):
        category = frame_category(row)
        if not category:
            continue
        line = f"{category}\t{row['path']}:{row['line']}\t{row['text']}"
        if line in seen:
            continue
        seen.add(line)
        lines.append(line)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def machine_category(row):
    text = row["text"]
    if not (MACHINE_RE.search(text) or MACHINE_RE.search(row["path"])):
        return ""
    if not MACHINE_PRIORITY_RE.search(text):
        return ""
    if re.search(r"GuidedTour_SteamMachine|WelcomeToSteamMachine|GuidedTour_SDCard_Title_SteamMachine", text, re.IGNORECASE):
        return "machine-setup"
    if re.search(r"SteamMachine_TestResult|SteamMachineVerified|SteamMachineCompatibility", text, re.IGNORECASE):
        return "machine-compatibility"
    return "machine"


def write_machine_key_lines(rows, path: Path):
    priority = {
        "machine-setup": 0,
        "machine-compatibility": 1,
        "machine": 2,
    }
    lines = []
    seen = set()

    def sort_key(row):
        return (priority.get(machine_category(row), 99), row["path"], int(row["line"]), row["text"])

    for row in sorted(rows, key=sort_key):
        category = machine_category(row)
        if not category:
            continue
        line = f"{category}\t{row['path']}:{row['line']}\t{row['text']}"
        if line in seen:
            continue
        seen.add(line)
        lines.append(line)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_markdown(rows, path: Path):
    lines = [
        "# SteamTracking Hardware Signals",
        "",
        "Focused SteamTracking scan for Valve hardware setup, commerce, compatibility, and controller backend signals.",
        "",
        "| Category | Source | Text |",
        "| --- | --- | --- |",
    ]
    for row in rows[:200]:
        text = row["text"].replace("|", "\\|")
        lines.append(f"| {row['category']} | `{row['path']}:{row['line']}` | `{text}` |")
    if len(rows) > 200:
        lines.extend(["", f"_Truncated markdown table to first 200 of {len(rows)} matches._"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--tracking-dir", required=True, type=Path)
    args = parser.parse_args()

    reports = args.run_dir / "reports"
    rows = build_rows(args.tracking_dir)
    rows.sort(key=lambda row: (row["category"], row["path"], int(row["line"]), row["text"]))
    write_tsv(rows, reports / "steamtracking-hardware-signals.tsv")
    write_key_lines(rows, reports / "steamtracking-hardware-signals-key-lines.txt")
    write_frame_key_lines(rows, reports / "steamtracking-frame-signals-key-lines.txt")
    write_machine_key_lines(rows, reports / "steamtracking-machine-signals-key-lines.txt")
    write_markdown(rows, reports / "steamtracking-hardware-signals.md")


if __name__ == "__main__":
    main()
