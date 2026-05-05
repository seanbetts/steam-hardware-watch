# Customs Shipment Monitor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a repeatable customs shipment monitor that saves ImportInfo shipment artifacts, extracts relevant Valve hardware rows, and includes them in the normal watch summaries.

**Architecture:** Keep the repo's existing helper pattern: a shell script owns source fetching and run-folder paths, while a focused Python parser turns saved HTML into TSV, key lines, and a Markdown report. `run_watch.sh` calls the helper every run, and the summary/draft scripts read the generated report files.

**Tech Stack:** POSIX shell, `curl`, Python 3 standard library (`html.parser`, `csv`, `argparse`, `dataclasses`), existing `unittest` test style.

---

## File Structure

- Create `scripts/parse_importinfo_shipments.py`
  - Parse ImportInfo search-result HTML tables.
  - Filter rows to Valve hardware shipment signals.
  - Write `customs-shipments.tsv`, `customs-shipments-key-lines.txt`, and `customs-shipments.md`.
- Create `scripts/check_customs_shipments.sh`
  - Fetch ImportInfo search pages to `RUN_DIR/api/customs`.
  - Record HTTP/block failures in `customs-shipments-errors.txt`.
  - Invoke the parser with saved HTML artifacts.
- Create `tests/test_customs_shipments.py`
  - Unit tests for parser behavior and shell blocked-source behavior.
- Modify `scripts/run_watch.sh`
  - Call the customs helper after Valve endpoint checks.
- Modify `scripts/write_run_summary.py`
  - Add customs blocked status and notable customs key lines.
- Modify `scripts/draft_status_update.py`
  - Add a Customs / Shipments draft section.
- Modify `SKILL.md`
  - Promote the customs helper from manual source to normal helper.
  - Document HMRC as rejected for this use case.
- Modify `references/sources.md`
  - Add ImportInfo URLs and note NBD/ImportGenius as corroboration.

## Task 1: Parser And Unit Tests

**Files:**
- Create: `scripts/parse_importinfo_shipments.py`
- Create: `tests/test_customs_shipments.py`

- [ ] **Step 1: Write failing parser tests**

Add this initial test file:

```python
import csv
import subprocess
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


IMPORTINFO_HTML = """
<html>
  <body>
    <h2>Search Results</h2>
    <table>
      <thead>
        <tr>
          <th>Run Date</th><th>Master BOL</th><th>House BOL</th><th>Voyage #</th>
          <th>Bill Type</th><th>Carrier Code</th><th>IMO #</th><th>Vessel Name</th>
          <th>Arrival Date</th><th>US Port</th><th>Foreign Port</th><th>Quantity</th>
          <th>Weight</th><th>Type of Service</th><th>Shipper</th><th>Consignee</th>
          <th>Notify Party</th><th>Commodity</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>2026-05-01</td><td>EGLV142653125618</td><td>SNHBSHALAX264014</td><td>084E</td>
          <td>House Bill</td><td>SNHB</td><td>9604081</td><td>EVER LOGIC</td>
          <td>2026-05-01</td><td>LOS ANGELES, CALIFORNIA</td><td>SHANGHAI CHINA (MAINLAND)</td>
          <td>42 PKG</td><td>12,578 K</td><td>House to House</td>
          <td>TECH-FRONT (CHONGQING) COMPUTER CO</td><td>CEVA C/O VALVE CORPORATION</td>
          <td>CEVA C/O VALVE CORPORATION</td><td>GAME CONSOLE</td>
        </tr>
        <tr>
          <td>2026-04-28</td><td>CMDUCHN3170474</td><td>EXDO621128151</td><td>0XRAJ</td>
          <td>House Bill</td><td>EXDO</td><td>9436379</td><td>CMA CGM SAMSON</td>
          <td>2026-04-28</td><td>SAVANNAH, GEORGIA</td><td>SHANGHAI CHINA (MAINLAND)</td>
          <td>15 PKG</td><td>4,143 KG</td><td>Pier to Pier</td>
          <td>TECH-FRONT (CHONGQING) COMPUTER CO</td><td>PROMETHEAN INC.</td>
          <td></td><td>CHROMEBOX HTS:</td>
        </tr>
      </tbody>
    </table>
  </body>
</html>
"""


class CustomsShipmentParserTests(unittest.TestCase):
    def test_extracts_relevant_importinfo_rows(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            html = tmp_path / "ceva-valve.html"
            html.write_text(IMPORTINFO_HTML, encoding="utf-8")
            reports = tmp_path / "reports"

            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "parse_importinfo_shipments.py"),
                    "--input",
                    f"ceva-valve={html}",
                    "--report-dir",
                    str(reports),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)

            rows = list(
                csv.DictReader(
                    (reports / "customs-shipments.tsv").read_text(encoding="utf-8").splitlines(),
                    delimiter="\t",
                )
            )
            self.assertEqual(1, len(rows))
            self.assertEqual("SNHBSHALAX264014", rows[0]["house_bol"])
            self.assertEqual("GAME CONSOLE", rows[0]["commodity"])
            self.assertEqual("CEVA C/O VALVE CORPORATION", rows[0]["consignee"])

            key_lines = (reports / "customs-shipments-key-lines.txt").read_text(encoding="utf-8")
            self.assertIn("2026-05-01", key_lines)
            self.assertIn("SNHBSHALAX264014", key_lines)
            self.assertIn("GAME CONSOLE", key_lines)

            report = (reports / "customs-shipments.md").read_text(encoding="utf-8")
            self.assertIn("## Newest Relevant Shipments", report)
            self.assertIn("CEVA C/O VALVE CORPORATION", report)
            self.assertIn("TECH-FRONT (CHONGQING) COMPUTER CO", report)

    def test_preserves_distinct_same_day_bols(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            html = tmp_path / "same-day.html"
            html.write_text(
                IMPORTINFO_HTML.replace(
                    "</tbody>",
                    """
                    <tr>
                      <td>2026-05-01</td><td>EGLV142653125669</td><td>SNHBSHALAX264015</td><td>084E</td>
                      <td>House Bill</td><td>SNHB</td><td>9604081</td><td>EVER LOGIC</td>
                      <td>2026-05-01</td><td>LOS ANGELES, CALIFORNIA</td><td>SHANGHAI CHINA (MAINLAND)</td>
                      <td>42 PKG</td><td>12,596 K</td><td>House to House</td>
                      <td>TECH-FRONT (CHONGQING) COMPUTER CO</td><td>CEVA C/O VALVE CORPORATION</td>
                      <td>CEVA C/O VALVE CORPORATION</td><td>GAME CONSOLE</td>
                    </tr>
                    </tbody>
                    """,
                ),
                encoding="utf-8",
            )
            reports = tmp_path / "reports"

            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "parse_importinfo_shipments.py"),
                    "--input",
                    f"ceva-valve={html}",
                    "--report-dir",
                    str(reports),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(0, result.returncode)
            rows = list(
                csv.DictReader(
                    (reports / "customs-shipments.tsv").read_text(encoding="utf-8").splitlines(),
                    delimiter="\t",
                )
            )
            self.assertEqual(["SNHBSHALAX264014", "SNHBSHALAX264015"], [row["house_bol"] for row in rows])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the parser tests and verify failure**

Run:

```bash
python3 -m unittest tests/test_customs_shipments.py -v
```

Expected: failure because `scripts/parse_importinfo_shipments.py` does not exist.

- [ ] **Step 3: Implement the parser**

Create `scripts/parse_importinfo_shipments.py` with this structure and behavior:

```python
#!/usr/bin/env python3
import argparse
import csv
import html
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


FIELD_MAP = {
    "run date": "run_date",
    "master bol": "master_bol",
    "house bol": "house_bol",
    "voyage #": "voyage",
    "bill type": "bill_type",
    "carrier code": "carrier_code",
    "imo #": "imo",
    "vessel name": "vessel_name",
    "arrival date": "arrival_date",
    "us port": "us_port",
    "foreign port": "foreign_port",
    "quantity": "quantity",
    "weight": "weight",
    "type of service": "type_of_service",
    "shipper": "shipper",
    "consignee": "consignee",
    "notify party": "notify_party",
    "commodity": "commodity",
}
OUTPUT_FIELDS = [
    "source",
    "query",
    "run_date",
    "master_bol",
    "house_bol",
    "voyage",
    "bill_type",
    "carrier_code",
    "imo",
    "vessel_name",
    "arrival_date",
    "us_port",
    "foreign_port",
    "quantity",
    "weight",
    "type_of_service",
    "shipper",
    "consignee",
    "notify_party",
    "commodity",
    "source_url",
]
PARTY_TERMS = ("VALVE", "CEVA", "INGRAM MICRO", "TECH-FRONT", "CHENG UEI")
PRODUCT_TERMS = ("GAME CONSOLE", "VR CONTROLLER", "CONTROLLER", "STEAM", "BASE STATION", "HEADSET", "DONGLE")


@dataclass
class InputSpec:
    query: str
    path: Path
    source_url: str


SOURCE_URLS = {
    "ceva-valve": "https://www.importinfo.com/search?s=CEVA%20C%2FO%20VALVE%20CORPORATION",
    "ingram-valve": "https://www.importinfo.com/search?s=INGRAM%20MICRO%20C%2FO%20VALVE%20CORPORATION",
    "tech-front-game-console": "https://www.importinfo.com/search?s=TECH-FRONT%20GAME%20CONSOLE%20VALVE",
    "valve-corporation-game-console": "https://www.importinfo.com/search?s=VALVE%20CORPORATION%20GAME%20CONSOLE",
}


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_cell = False
        self.current_cell = []
        self.current_row = []
        self.rows = []
        self.headers = []
        self.in_header_cell = False
        self.current_is_header = False

    def handle_starttag(self, tag, attrs):
        if tag in {"td", "th"}:
            self.in_cell = True
            self.current_is_header = tag == "th"
            self.current_cell = []

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell.append(data)

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.in_cell:
            value = " ".join("".join(self.current_cell).split())
            self.current_row.append(html.unescape(value))
            self.in_cell = False
            if self.current_is_header:
                self.in_header_cell = True
        elif tag == "tr":
            if self.current_row:
                if self.in_header_cell:
                    self.headers = self.current_row
                else:
                    self.rows.append(self.current_row)
            self.current_row = []
            self.in_header_cell = False


def normalize_header(value: str) -> str:
    return FIELD_MAP.get(value.strip().lower(), "")


def parse_rows(spec: InputSpec) -> list[dict[str, str]]:
    parser = TableParser()
    parser.feed(spec.path.read_text(encoding="utf-8", errors="ignore"))
    headers = [normalize_header(header) for header in parser.headers]
    parsed = []
    for row in parser.rows:
        if not headers or len(row) < 4:
            continue
        record = {field: "" for field in OUTPUT_FIELDS}
        record["source"] = "importinfo"
        record["query"] = spec.query
        record["source_url"] = spec.source_url
        for index, value in enumerate(row):
            if index < len(headers) and headers[index]:
                record[headers[index]] = value
        if is_relevant(record):
            parsed.append(record)
    return parsed


def is_relevant(record: dict[str, str]) -> bool:
    party_text = " ".join([record["shipper"], record["consignee"], record["notify_party"]]).upper()
    product_text = record["commodity"].upper()
    return any(term in party_text for term in PARTY_TERMS) and any(term in product_text for term in PRODUCT_TERMS)


def row_identity(row: dict[str, str]) -> str:
    if row["house_bol"]:
        return row["house_bol"]
    if row["master_bol"]:
        return row["master_bol"]
    return "|".join([row["arrival_date"], row["shipper"], row["consignee"], row["quantity"], row["weight"], row["commodity"]])


def dedupe(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen = set()
    output = []
    for row in rows:
        identity = row_identity(row)
        if identity in seen:
            continue
        seen.add(identity)
        output.append(row)
    return output


def write_tsv(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def key_line(row: dict[str, str]) -> str:
    bol = row["house_bol"] or row["master_bol"]
    return "\t".join([row["arrival_date"], row["consignee"], row["shipper"], row["commodity"], row["quantity"], row["weight"], bol])


def write_key_lines(rows: list[dict[str, str]], output: Path) -> None:
    output.write_text("\n".join(key_line(row) for row in rows) + ("\n" if rows else ""), encoding="utf-8")


def write_report(rows: list[dict[str, str]], output: Path) -> None:
    lines = [
        "# Customs Shipments",
        "",
        f"Relevant shipments: `{len(rows)}`",
        "",
        "## Newest Relevant Shipments",
        "",
    ]
    if rows:
        lines.append("| Arrival | Consignee | Shipper | Commodity | Quantity | Weight | BOL |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for row in rows[:25]:
            bol = row["house_bol"] or row["master_bol"]
            lines.append(
                f"| `{row['arrival_date']}` | `{row['consignee']}` | `{row['shipper']}` | `{row['commodity']}` | `{row['quantity']}` | `{row['weight']}` | `{bol}` |"
            )
    else:
        lines.append("- No relevant customs shipment rows extracted.")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Customs records corroborate logistics activity but do not prove retail product identity, price, or exact availability.",
            "- Generic `GAME CONSOLE` descriptions should remain medium confidence unless another source identifies the device.",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")


def parse_input(value: str) -> InputSpec:
    query, path = value.split("=", 1)
    return InputSpec(query=query, path=Path(path), source_url=SOURCE_URLS.get(query, ""))


def parse_manifest(path: Path) -> list[InputSpec]:
    specs = []
    if not path.exists():
        return specs
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        query, source_url, html_path = raw_line.split("\t", 2)
        specs.append(InputSpec(query=query, source_url=source_url, path=Path(html_path)))
    return specs


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse ImportInfo shipment pages into run reports.")
    parser.add_argument("--input", action="append", default=[], help="Stable query slug and HTML path as slug=path")
    parser.add_argument("--manifest", action="append", default=[], help="TSV manifest with slug, source URL, and HTML path")
    parser.add_argument("--report-dir", required=True)
    args = parser.parse_args()

    rows = []
    specs = [parse_input(item) for item in args.input]
    for manifest in args.manifest:
        specs.extend(parse_manifest(Path(manifest)))
    for spec in specs:
        if spec.path.exists():
            rows.extend(parse_rows(spec))
    rows = sorted(dedupe(rows), key=lambda row: (row["arrival_date"], row["run_date"], row_identity(row)), reverse=True)

    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(rows, report_dir / "customs-shipments.tsv")
    write_key_lines(rows, report_dir / "customs-shipments-key-lines.txt")
    write_report(rows, report_dir / "customs-shipments.md")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the parser tests and verify pass**

Run:

```bash
python3 -m unittest tests/test_customs_shipments.py -v
```

Expected: both tests pass.

- [ ] **Step 5: Commit parser and tests**

Run:

```bash
git add scripts/parse_importinfo_shipments.py tests/test_customs_shipments.py
git commit -m "Add ImportInfo customs shipment parser"
```

## Task 2: Shell Helper And Blocked-Source Tests

**Files:**
- Create: `scripts/check_customs_shipments.sh`
- Modify: `tests/test_customs_shipments.py`

- [ ] **Step 1: Add shell helper tests**

Append these tests to `tests/test_customs_shipments.py` before the `if __name__ == "__main__"` block:

```python
import os
import stat


def write_executable(path, content):
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class CheckCustomsShipmentsShellTests(unittest.TestCase):
    def test_fetches_pages_and_runs_parser(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = tmp_path / "run"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            write_executable(
                fake_bin / "curl",
                """
                #!/bin/sh
                printf '%s\\n' '<html><table><tr><th>Run Date</th><th>Master BOL</th><th>House BOL</th><th>Voyage #</th><th>Bill Type</th><th>Carrier Code</th><th>IMO #</th><th>Vessel Name</th><th>Arrival Date</th><th>US Port</th><th>Foreign Port</th><th>Quantity</th><th>Weight</th><th>Type of Service</th><th>Shipper</th><th>Consignee</th><th>Notify Party</th><th>Commodity</th></tr><tr><td>2026-05-01</td><td>EGLV142653125618</td><td>SNHBSHALAX264014</td><td>084E</td><td>House Bill</td><td>SNHB</td><td>9604081</td><td>EVER LOGIC</td><td>2026-05-01</td><td>LOS ANGELES, CALIFORNIA</td><td>SHANGHAI CHINA (MAINLAND)</td><td>42 PKG</td><td>12,578 K</td><td>House to House</td><td>TECH-FRONT (CHONGQING) COMPUTER CO</td><td>CEVA C/O VALVE CORPORATION</td><td>CEVA C/O VALVE CORPORATION</td><td>GAME CONSOLE</td></tr></table></html>'
                """
            )
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}:{env['PATH']}"

            result = subprocess.run(
                [str(ROOT / "scripts" / "check_customs_shipments.sh"), str(run_dir)],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            self.assertTrue((run_dir / "api" / "customs" / "importinfo-ceva-valve.html").exists())
            key_lines = (run_dir / "reports" / "customs-shipments-key-lines.txt").read_text(encoding="utf-8")
            self.assertIn("SNHBSHALAX264014", key_lines)

    def test_records_blocked_fetches_without_failing_run(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = tmp_path / "run"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            write_executable(
                fake_bin / "curl",
                """
                #!/bin/sh
                exit 22
                """
            )
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}:{env['PATH']}"

            result = subprocess.run(
                [str(ROOT / "scripts" / "check_customs_shipments.sh"), str(run_dir)],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            errors = (run_dir / "reports" / "customs-shipments-errors.txt").read_text(encoding="utf-8")
            self.assertIn("failed to fetch", errors)
```

- [ ] **Step 2: Run the shell tests and verify failure**

Run:

```bash
python3 -m unittest tests/test_customs_shipments.py -v
```

Expected: shell tests fail because `scripts/check_customs_shipments.sh` does not exist.

- [ ] **Step 3: Implement the shell helper**

Create `scripts/check_customs_shipments.sh`:

```sh
#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 RUN_DIR" >&2
  exit 1
fi

RUN_DIR="$1"
OUT_DIR="$RUN_DIR/api/customs"
REPORT_DIR="$RUN_DIR/reports"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
mkdir -p "$OUT_DIR" "$REPORT_DIR"

ERROR_FILE="$REPORT_DIR/customs-shipments-errors.txt"
: > "$ERROR_FILE"

IMPORTINFO_USER_AGENT="${IMPORTINFO_USER_AGENT:-Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36}"

MANIFEST="$OUT_DIR/importinfo-inputs.tsv"
: > "$MANIFEST"

fetch_importinfo() {
  slug="$1"
  query="$2"
  url="$3"
  tmp="$OUT_DIR/$slug.html.tmp"
  out="$OUT_DIR/$slug.html"

  if curl -A "$IMPORTINFO_USER_AGENT" \
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
    -H 'Accept-Language: en-US,en;q=0.9' \
    --retry 2 --retry-delay 2 --max-time 45 -fsSL "$url" > "$tmp" 2>/dev/null; then
    mv "$tmp" "$out"
    printf '%s\t%s\t%s\n' "$query" "$url" "$out" >> "$MANIFEST"
    return 0
  fi

  rm -f "$tmp" "$out"
  printf '%s\n' "failed to fetch $url" >> "$ERROR_FILE"
  return 1
}

fetch_importinfo "importinfo-ceva-valve" "ceva-valve" "https://www.importinfo.com/search?s=CEVA%20C%2FO%20VALVE%20CORPORATION" || true
fetch_importinfo "importinfo-ingram-valve" "ingram-valve" "https://www.importinfo.com/search?s=INGRAM%20MICRO%20C%2FO%20VALVE%20CORPORATION" || true
fetch_importinfo "importinfo-tech-front-game-console" "tech-front-game-console" "https://www.importinfo.com/search?s=TECH-FRONT%20GAME%20CONSOLE%20VALVE" || true
fetch_importinfo "importinfo-valve-corporation" "valve-corporation-game-console" "https://www.importinfo.com/search?s=VALVE%20CORPORATION%20GAME%20CONSOLE" || true

python3 "$SCRIPT_DIR/parse_importinfo_shipments.py" --manifest "$MANIFEST" --report-dir "$REPORT_DIR"

printf '%s\n' \
  "Saved customs shipment pages to $OUT_DIR" \
  "Saved customs shipment report to $REPORT_DIR/customs-shipments.md"
```

Make it executable:

```bash
chmod +x scripts/check_customs_shipments.sh
```

- [ ] **Step 4: Run the shell tests and verify pass**

Run:

```bash
python3 -m unittest tests/test_customs_shipments.py -v
```

Expected: all customs tests pass.

- [ ] **Step 5: Commit shell helper**

Run:

```bash
git add scripts/check_customs_shipments.sh tests/test_customs_shipments.py
git commit -m "Add customs shipment source helper"
```

## Task 3: Runner And Summary Integration

**Files:**
- Modify: `scripts/run_watch.sh`
- Modify: `scripts/write_run_summary.py`
- Modify: `scripts/draft_status_update.py`
- Test: `tests/test_customs_shipments.py`

- [ ] **Step 1: Add summary integration test**

Append this test before the final `if __name__ == "__main__"` block:

```python
class CustomsSummaryIntegrationTests(unittest.TestCase):
    def test_run_summary_and_status_draft_include_customs_lines(self):
        with TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "2026-05-05"
            reports = run_dir / "reports"
            reports.mkdir(parents=True)
            (reports / "customs-shipments-key-lines.txt").write_text(
                "2026-05-01\\tCEVA C/O VALVE CORPORATION\\tTECH-FRONT (CHONGQING) COMPUTER CO\\tGAME CONSOLE\\t42 PKG\\t12596 Kgs\\tSNHBSHALAX264015\\n",
                encoding="utf-8",
            )
            (reports / "customs-shipments-errors.txt").write_text("", encoding="utf-8")

            summary = subprocess.run(
                ["python3", str(ROOT / "scripts" / "write_run_summary.py"), "--run-dir", str(run_dir)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            draft = subprocess.run(
                ["python3", str(ROOT / "scripts" / "draft_status_update.py"), "--run-dir", str(run_dir)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(0, summary.returncode)
            self.assertEqual(0, draft.returncode)
            self.assertIn("Customs shipments", (reports / "run-summary.md").read_text(encoding="utf-8"))
            self.assertIn("SNHBSHALAX264015", (reports / "run-summary.md").read_text(encoding="utf-8"))
            self.assertIn("Customs / Shipments", (reports / "status-draft.md").read_text(encoding="utf-8"))
            self.assertIn("GAME CONSOLE", (reports / "status-draft.md").read_text(encoding="utf-8"))
```

- [ ] **Step 2: Run integration test and verify failure**

Run:

```bash
python3 -m unittest tests/test_customs_shipments.py -v
```

Expected: summary integration test fails because the summary scripts do not read customs report files yet.

- [ ] **Step 3: Integrate helper into `run_watch.sh`**

Add this line after `check_valve_endpoints.sh`:

```sh
"$SCRIPT_DIR/check_customs_shipments.sh" "$RUN_DIR"
```

- [ ] **Step 4: Update `write_run_summary.py`**

Add a customs blocked line in the At A Glance block:

```python
f"- Customs shipments blocked: `{'yes' if count(reports / 'customs-shipments-errors.txt') else 'no'}`",
```

Add customs to Most Relevant Outputs:

```python
f"- Customs shipments: `{reports / 'customs-shipments.md'}`",
```

Add customs notable lines after Valve:

```python
notable.extend([f"- Customs shipments: `{line}`" for line in filtered_first(reports / "customs-shipments-key-lines.txt", 8)])
```

- [ ] **Step 5: Update `draft_status_update.py`**

Read customs data near the other source lines:

```python
customs_lines = first_n_nonempty(reports / "customs-shipments-key-lines.txt", 8)
customs_blocked = has_nonempty(reports / "customs-shipments-errors.txt")
```

Add this section after Valve Support / CDN:

```python
lines.extend(["", "#### Customs / Shipments"])
if customs_blocked:
    lines.append("- Customs shipment fetches failed or were partially blocked in this run. See `customs-shipments-errors.txt`.")
if customs_lines:
    lines.extend([f"- `{line}`" for line in customs_lines])
elif not customs_blocked:
    lines.append("- No relevant customs shipment rows found.")
```

Add the report path to Suggested Run Note Additions:

```python
f"- Customs shipments: `{reports / 'customs-shipments.md'}`",
```

- [ ] **Step 6: Run integration tests and verify pass**

Run:

```bash
python3 -m unittest tests/test_customs_shipments.py -v
```

Expected: all customs tests pass.

- [ ] **Step 7: Commit runner and summary integration**

Run:

```bash
git add scripts/run_watch.sh scripts/write_run_summary.py scripts/draft_status_update.py tests/test_customs_shipments.py
git commit -m "Integrate customs shipments into watch summaries"
```

## Task 4: Skill And Source Documentation

**Files:**
- Modify: `SKILL.md`
- Modify: `references/sources.md`
- Test: full targeted suite

- [ ] **Step 1: Update `SKILL.md` helper list**

Add `scripts/check_customs_shipments.sh` to the source helper list in the Output Contract section:

```markdown
- [scripts/check_customs_shipments.sh](scripts/check_customs_shipments.sh)
```

- [ ] **Step 2: Update Customs / Regulatory section in `SKILL.md`**

Replace the short customs section with:

```markdown
Use [scripts/check_customs_shipments.sh](scripts/check_customs_shipments.sh) for shipment-level customs checks.

Run customs checks every normal watch run because ImportInfo is quick and high-signal. Use customs data for confirmation, not as the primary source of truth.

Primary automated customs source:

- ImportInfo search pages for `CEVA C/O VALVE CORPORATION`, `INGRAM MICRO C/O VALVE CORPORATION`, `TECH-FRONT GAME CONSOLE VALVE`, and `VALVE CORPORATION GAME CONSOLE`

Corroborating/manual sources:

- NBD Valve and Ingram/Valve trader pages
- ImportGenius public previews for CEVA/Valve, Ingram/Valve, and Tech-Front

Do not use HMRC UK Trade Info for launch monitoring. It is lagged monthly trader/commodity presence, not shipment-level evidence.
```

- [ ] **Step 3: Update `references/sources.md`**

Under Customs / Regulatory, add:

```markdown
- ImportInfo search for CEVA/Valve: `https://www.importinfo.com/search?s=CEVA%20C%2FO%20VALVE%20CORPORATION`
- ImportInfo search for Ingram/Valve: `https://www.importinfo.com/search?s=INGRAM%20MICRO%20C%2FO%20VALVE%20CORPORATION`
- ImportInfo Tech-Front supplier page: `https://www.importinfo.com/tech-front-chongqing-computer-co`
- ImportInfo Valve Corporation page: `https://www.importinfo.com/valve-corporation`
- HMRC UK Trade Info: rejected for this workflow because it is lagged monthly aggregate/trader data rather than shipment-level data.
```

- [ ] **Step 4: Run targeted tests**

Run:

```bash
python3 -m unittest tests/test_customs_shipments.py tests/test_check_steamdb.py tests/test_new_sources.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Run one customs helper smoke test against live ImportInfo**

Run:

```bash
tmp_run="$(mktemp -d)"
scripts/check_customs_shipments.sh "$tmp_run"
sed -n '1,40p' "$tmp_run/reports/customs-shipments-key-lines.txt"
```

Expected: command exits 0. If ImportInfo is reachable, key lines include recent `GAME CONSOLE` rows. If ImportInfo blocks, `customs-shipments-errors.txt` records blocked fetches and the command still exits 0.

- [ ] **Step 6: Commit documentation**

Run:

```bash
git add SKILL.md references/sources.md
git commit -m "Document customs shipment monitoring sources"
```

## Task 5: Final Verification

**Files:**
- No new edits expected.

- [ ] **Step 1: Run the full test suite**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Check git status**

Run:

```bash
git status --short
```

Expected: no uncommitted changes, unless live smoke-test artifacts were created outside the repo.

- [ ] **Step 3: Summarize implementation**

Report:

- New helper and parser paths.
- Whether live ImportInfo smoke test reached the source.
- Any remaining limitation around UK shipment-level source discovery.
