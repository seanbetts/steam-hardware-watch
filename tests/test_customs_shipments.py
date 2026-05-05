import csv
import subprocess
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


IMPORTINFO_HTML = textwrap.dedent(
    """
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
)


def run_parser(args, reports):
    return subprocess.run(
        [
            "python3",
            str(ROOT / "scripts" / "parse_importinfo_shipments.py"),
            *args,
            "--report-dir",
            str(reports),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def read_rows(reports):
    return list(
        csv.DictReader(
            (reports / "customs-shipments.tsv").read_text(encoding="utf-8").splitlines(),
            delimiter="\t",
        )
    )


class CustomsShipmentParserTests(unittest.TestCase):
    def test_extracts_relevant_importinfo_rows(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            html = tmp_path / "ceva-valve.html"
            html.write_text(IMPORTINFO_HTML, encoding="utf-8")
            reports = tmp_path / "reports"

            result = run_parser(["--input", f"ceva-valve={html}"], reports)

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)

            rows = read_rows(reports)
            self.assertEqual(1, len(rows))
            self.assertEqual("SNHBSHALAX264014", rows[0]["house_bol"])
            self.assertEqual("GAME CONSOLE", rows[0]["commodity"])
            self.assertEqual("CEVA C/O VALVE CORPORATION", rows[0]["consignee"])

            key_lines = (reports / "customs-shipments-key-lines.txt").read_text(
                encoding="utf-8"
            )
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
                    textwrap.dedent(
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
                        """
                    ),
                ),
                encoding="utf-8",
            )
            reports = tmp_path / "reports"

            result = run_parser(["--input", f"ceva-valve={html}"], reports)

            self.assertEqual(0, result.returncode)
            rows = read_rows(reports)
            self.assertEqual(
                ["SNHBSHALAX264014", "SNHBSHALAX264015"],
                [row["house_bol"] for row in rows],
            )

    def test_ignores_later_unrelated_table_headers(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            html = tmp_path / "extra-table.html"
            html.write_text(
                IMPORTINFO_HTML.replace(
                    "</body>",
                    textwrap.dedent(
                        """
                        <table>
                          <tr><th>Name</th><th>Description</th></tr>
                          <tr><td>PROMETHEAN INC.</td><td>CHROMEBOX HTS:</td></tr>
                        </table>
                        </body>
                        """
                    ),
                ),
                encoding="utf-8",
            )
            reports = tmp_path / "reports"

            result = run_parser(["--input", f"ceva-valve={html}"], reports)

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            rows = read_rows(reports)
            self.assertEqual(["SNHBSHALAX264014"], [row["house_bol"] for row in rows])

    def test_matches_relevance_terms_split_by_inline_markup(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            html = tmp_path / "split-cells.html"
            html.write_text(
                IMPORTINFO_HTML.replace(
                    "CEVA C/O VALVE CORPORATION</td><td>GAME CONSOLE",
                    "CEVA C/O <span>VALVE</span> CORPORATION</td><td>GAME<br>CONSOLE",
                ),
                encoding="utf-8",
            )
            reports = tmp_path / "reports"

            result = run_parser(["--input", f"ceva-valve={html}"], reports)

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            rows = read_rows(reports)
            self.assertEqual(1, len(rows))
            self.assertEqual("CEVA C/O VALVE CORPORATION", rows[0]["consignee"])
            self.assertEqual("GAME CONSOLE", rows[0]["commodity"])

    def test_manifest_inputs_dedupe_duplicate_bols(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            first = tmp_path / "first.html"
            second = tmp_path / "second.html"
            manifest = tmp_path / "manifest.tsv"
            first.write_text(IMPORTINFO_HTML, encoding="utf-8")
            second.write_text(IMPORTINFO_HTML, encoding="utf-8")
            manifest.write_text(
                "\n".join(
                    (
                        "slug\tsource_url\thtml_path",
                        f"ceva-valve\thttps://example.test/ceva\t{first}",
                        f"ceva-valve\thttps://example.test/ceva\t{second}",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            reports = tmp_path / "reports"

            result = run_parser(["--manifest", str(manifest)], reports)

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            rows = read_rows(reports)
            self.assertEqual(["SNHBSHALAX264014"], [row["house_bol"] for row in rows])
            self.assertEqual("https://example.test/ceva", rows[0]["source_url"])


if __name__ == "__main__":
    unittest.main()
