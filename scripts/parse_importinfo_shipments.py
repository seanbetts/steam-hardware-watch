#!/usr/bin/env python3
import argparse
import csv
import html
import re
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
PRODUCT_TERMS = (
    "GAME CONSOLE",
    "VR CONTROLLER",
    "CONTROLLER",
    "STEAM",
    "BASE STATION",
    "HEADSET",
    "DONGLE",
)

SOURCE_URLS = {
    "ceva-valve": "https://www.importinfo.com/search?s=CEVA%20C%2FO%20VALVE%20CORPORATION",
    "ingram-valve": "https://www.importinfo.com/search?s=INGRAM%20MICRO%20C%2FO%20VALVE%20CORPORATION",
    "tech-front-game-console": "https://www.importinfo.com/search?s=TECH-FRONT%20GAME%20CONSOLE%20VALVE",
    "valve-corporation-game-console": "https://www.importinfo.com/search?s=VALVE%20CORPORATION%20GAME%20CONSOLE",
    "importgenius-ingram-valve": "https://www.importgenius.com/importers/ingram-micro-c-o-valve-corporation",
}


@dataclass
class InputSpec:
    query: str
    path: Path
    source_url: str


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self._current_headers = []
        self._in_row = False
        self._in_cell = False
        self._cell_tag = ""
        self._current_cells = []
        self._current_cell_parts = []
        self._row_has_header = False
        self._row_has_data = False

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._in_row = True
            self._current_cells = []
            self._row_has_header = False
            self._row_has_data = False
        elif self._in_row and tag in ("th", "td"):
            self._in_cell = True
            self._cell_tag = tag
            self._current_cell_parts = []
            if tag == "th":
                self._row_has_header = True
            else:
                self._row_has_data = True
        elif self._in_cell and tag == "br":
            self._current_cell_parts.append(" ")

    def handle_endtag(self, tag):
        if self._in_cell and tag == self._cell_tag:
            value = html.unescape(" ".join(self._current_cell_parts))
            self._current_cells.append(" ".join(value.split()))
            self._in_cell = False
            self._cell_tag = ""
            self._current_cell_parts = []
        elif self._in_row and tag == "tr":
            if self._row_has_header and self._current_cells:
                self._current_headers = self._current_cells
            elif self._row_has_data and self._current_cells:
                self.rows.append((list(self._current_headers), self._current_cells))
            self._in_row = False

    def handle_data(self, data):
        if self._in_cell:
            self._current_cell_parts.append(data)


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("br", "p", "tr", "li", "h1", "h2", "h3", "section"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("p", "tr", "li", "h1", "h2", "h3", "section"):
            self.parts.append("\n")

    def handle_data(self, data):
        self.parts.append(data)

    def text(self):
        return html.unescape(" ".join("".join(self.parts).split()))


def normalize_header(value):
    return FIELD_MAP.get(value.strip().lower(), "")


def parse_rows(spec):
    if spec.query.startswith("importgenius-"):
        return parse_importgenius_rows(spec)

    parser = TableParser()
    parser.feed(spec.path.read_text(encoding="utf-8", errors="ignore"))
    rows = []
    for headers, parsed_row in parser.rows:
        fields = [normalize_header(header) for header in headers]
        record = {field: "" for field in OUTPUT_FIELDS}
        record["source"] = "importinfo"
        record["query"] = spec.query
        record["source_url"] = spec.source_url
        for index, field in enumerate(fields):
            if field and index < len(parsed_row):
                record[field] = parsed_row[index]
        if is_relevant(record):
            rows.append(record)
    return rows


def parse_importgenius_rows(spec):
    parser = TextParser()
    parser.feed(spec.path.read_text(encoding="utf-8", errors="ignore"))
    text = parser.text()
    pattern = re.compile(
        r"(?:^|\s)(?P<rank>\d+)\s+"
        r"(?P<bol>[A-Z0-9]+)\s+"
        r"(?P<product>GAME\s+CONSOLE\s*\.?)\s+"
        r"(?P<importer>(?:INGRAM\s+MICRO|CEVA)\s+C/O\s+VALVE\s+CORPORATION)\s+"
        r"(?P<supplier>TECH-?FRONT\s+\(CHONGQING\)\s+COMPUTER\s+CO)\s+"
        r"(?P<arrival>\d{4}-\d{2}-\d{2})\s+"
        r"(?P<country>[A-Za-z ]+?)\s+"
        r"(?P<weight>[\d,]+\s+Kgs)\s+"
        r"(?P<quantity>\d+\s+PKG)",
        re.IGNORECASE,
    )
    rows = []
    for match in pattern.finditer(text):
        record = {field: "" for field in OUTPUT_FIELDS}
        record["source"] = "importgenius"
        record["query"] = spec.query
        record["house_bol"] = match.group("bol").upper()
        record["arrival_date"] = match.group("arrival")
        record["foreign_port"] = match.group("country").strip()
        record["quantity"] = " ".join(match.group("quantity").split())
        record["weight"] = " ".join(match.group("weight").split())
        record["shipper"] = normalize_company(match.group("supplier"))
        record["consignee"] = normalize_company(match.group("importer"))
        record["notify_party"] = record["consignee"]
        record["commodity"] = " ".join(match.group("product").upper().split())
        record["source_url"] = spec.source_url
        if is_relevant(record):
            rows.append(record)
    return rows


def normalize_company(value):
    return " ".join(value.upper().replace("TECH FRONT", "TECH-FRONT").split())


def is_relevant(record):
    party_text = " ".join(
        (
            record["shipper"],
            record["consignee"],
            record["notify_party"],
        )
    ).upper()
    record_text = " ".join(
        (
            record["query"],
            record["run_date"],
            record["master_bol"],
            record["house_bol"],
            record["voyage"],
            record["bill_type"],
            record["carrier_code"],
            record["imo"],
            record["vessel_name"],
            record["arrival_date"],
            record["us_port"],
            record["foreign_port"],
            record["quantity"],
            record["weight"],
            record["type_of_service"],
            record["commodity"],
        )
    ).upper()
    commodity_text = record["commodity"].upper()
    has_valve_signal = "VALVE" in party_text or "VALVE CORPORATION" in record_text
    return has_valve_signal and any(term in party_text for term in PARTY_TERMS) and any(
        term in commodity_text for term in PRODUCT_TERMS
    )


def row_identity(row):
    if row["house_bol"]:
        return row["house_bol"]
    if row["master_bol"]:
        return row["master_bol"]
    return "\t".join(
        (
            row["arrival_date"],
            row["shipper"],
            row["consignee"],
            row["quantity"],
            row["weight"],
            row["commodity"],
        )
    )


def dedupe(rows):
    seen = set()
    output = []
    for row in rows:
        identity = row_identity(row)
        if identity in seen:
            continue
        seen.add(identity)
        output.append(row)
    return output


def write_tsv(rows, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def key_line(row):
    bol = row["house_bol"] or row["master_bol"]
    return "\t".join(
        (
            row["arrival_date"],
            row["consignee"],
            row["shipper"],
            row["commodity"],
            row["quantity"],
            row["weight"],
            bol,
        )
    )


def write_key_lines(rows, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(key_line(row) for row in rows)
    if rows:
        content += "\n"
    output.write_text(content, encoding="utf-8")


def write_report(rows, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Customs Shipments",
        "",
        f"Relevant shipment count: {len(rows)}",
        "",
        "## Newest Relevant Shipments",
        "",
    ]
    if rows:
        lines.extend(
            [
                "| Arrival Date | Consignee | Shipper | Commodity | Quantity | Weight | BOL |",
                "| --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in rows[:25]:
            lines.append(
                "| "
                + " | ".join(
                    (
                        row["arrival_date"],
                        row["consignee"],
                        row["shipper"],
                        row["commodity"],
                        row["quantity"],
                        row["weight"],
                        row["house_bol"] or row["master_bol"],
                    )
                )
                + " |"
            )
    else:
        lines.append("No relevant ImportInfo shipment rows found.")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "Customs data is corroborating evidence, not a standalone confirmation. "
            "GAME CONSOLE descriptions are medium confidence without other identifiers.",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")


def parse_input(value):
    slug, separator, path = value.partition("=")
    if not separator or not slug or not path:
        raise argparse.ArgumentTypeError("--input values must use slug=path")
    return InputSpec(slug, Path(path), SOURCE_URLS.get(slug, ""))


def parse_manifest(path):
    specs = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for row in reader:
            if not row or not any(cell.strip() for cell in row):
                continue
            if row[0].strip().lower() == "slug":
                continue
            if len(row) < 3:
                continue
            slug = row[0].strip()
            source_url = row[1].strip() or SOURCE_URLS.get(slug, "")
            html_path = row[2].strip()
            if not slug or not html_path:
                continue
            specs.append(InputSpec(slug, Path(html_path), source_url))
    return specs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", default=[], type=parse_input)
    parser.add_argument("--manifest", action="append", default=[], type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    args = parser.parse_args()

    specs = list(args.input)
    for manifest in args.manifest:
        if manifest.exists():
            specs.extend(parse_manifest(manifest))

    rows = []
    for spec in specs:
        if spec.path.exists():
            rows.extend(parse_rows(spec))

    rows = sorted(
        dedupe(rows),
        key=lambda row: (row["arrival_date"], row["run_date"]),
        reverse=True,
    )

    report_dir = args.report_dir
    write_tsv(rows, report_dir / "customs-shipments.tsv")
    write_key_lines(rows, report_dir / "customs-shipments-key-lines.txt")
    write_report(rows, report_dir / "customs-shipments.md")


if __name__ == "__main__":
    main()
