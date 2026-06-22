import csv
import os
import stat
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


IMPORTGENIUS_HTML = textwrap.dedent(
    """
    <html>
      <body>
        <h1>Ingram Micro C/o Valve Corporation</h1>
        <p>Updated: 2026-05-18</p>
        <section>
          <h2>Importer Shipments</h2>
          <p>#  Bill of Lading  Product  Importer  Supplier  Arrival Date  Country of Origin  Gross Weight KGS  Quantity</p>
          <p>1  SNHBSHACHI265020  GAME CONSOLE  INGRAM MICRO C/O VALVE CORPORATION  TECH-FRONT (CHONGQING) COMPUTER CO  2026-05-18  China  14353 Kgs  42 PKG</p>
          <p>2  SNHBSHACHI264140  GAME CONSOLE  INGRAM MICRO C/O VALVE CORPORATION  TECH-FRONT (CHONGQING) COMPUTER CO  2026-05-18  China  14533 Kgs  42 PKG</p>
          <p>3  SNHBSHACHI264031  GAME CONSOLE  INGRAM MICRO C/O VALVE CORPORATION  TECH-FRONT (CHONGQING) COMPUTER CO  2026-05-08  China  12615 Kgs  42 PKG</p>
        </section>
      </body>
    </html>
    """
)


IMPORTGENIUS_CEVA_VR_HTML = textwrap.dedent(
    """
    <html>
      <body>
        <h1>CEVA C/o Valve Corporation</h1>
        <p>Updated: 2026-06-10</p>
        <section>
          <h2>Importer Shipments</h2>
          <p>#  Bill of Lading  Product  Importer  Supplier  Arrival Date  Country of Origin  Gross Weight KGS  Quantity</p>
          <p>1  SNHBSHACHI265173  VIRTUAL REALITY DEVICES  CEVA C/O VALVE CORPORATION  TECH-FRONT (CHONGQING) COMPUTER CO  2026-06-10  China  6374 Kgs  42 PKG</p>
          <p>2  SNHBSHACHI265174  VIRTUAL REALITY DEVICES  CEVA C/O VALVE CORPORATION  TECH-FRONT (CHONGQING) COMPUTER CO  2026-06-10  China  6372 Kgs  42 PKG</p>
        </section>
      </body>
    </html>
    """
)


IMPORTGENIUS_VERTICAL_CEVA_VR_HTML = textwrap.dedent(
    """
    <html>
      <body>
        <h1>CEVA C/o Valve Corporation</h1>
        <section>
          <h2>Importer Shipments</h2>
          <div>#</div><div>Bill of Lading</div><div>Product</div><div>Importer</div>
          <div>Supplier</div><div>Arrival Date</div><div>Country of Origin</div>
          <div>Gross Weight KGS</div><div>Quantity</div>
          <div>1</div>
          <div>SNHBSHACHI265173</div>
          <div>VIRTUAL REALITY DEVICES</div>
          <div>CEVA C/O VALVE CORPORATION</div>
          <div>TECH-FRONT (CHONGQING) COMPUTER CO</div>
          <div>2026-06-10</div>
          <div>China</div>
          <div>6374 Kgs</div>
          <div>42 PKG</div>
        </section>
      </body>
    </html>
    """
)


IMPORTGENIUS_CEVA_NL_VR_HTML = textwrap.dedent(
    """
    <html>
      <body>
        <h1>CEVA NL C/o Valve Corporation</h1>
        <p>Updated: 2026-06-10</p>
        <section>
          <h2>Importer Shipments</h2>
          <p>#  Bill of Lading  Product  Importer  Supplier  Arrival Date  Country of Origin  Gross Weight KGS  Quantity</p>
          <p>1  SNHBSHALAX265177  VIRTUAL REALITY DEVICES  CEVA NL C/O VALVE CORPORATION  TECH-FRONT (CHONGQING) COMPUTER CO  2026-06-10  China  6400 Kgs  42 PKG</p>
        </section>
      </body>
    </html>
    """
)


IMPORTGENIUS_VALVE_CONTROLLER_HTML = textwrap.dedent(
    """
    <html>
      <body>
        <h1>Valve Corporation</h1>
        <p>Updated: 2026-06-10</p>
        <section>
          <h2>Importer Shipments</h2>
          <p>#  Bill of Lading  Product  Importer  Supplier  Arrival Date  Country of Origin  Gross Weight KGS  Quantity</p>
          <p>1  SNHBHKGLBG266011  WIRELESS PC CONTROLLER  VALVE CORPORATION  CHENG UEI PRECISION IND. CO LTD  2026-06-10  Hong Kong  9727 Kgs  30 PKG</p>
          <p>4  DSVFMIL0341656  PNEUMATIC ACTUATOR VALVE 48 LLC L.P.S. SRL PER CONTO BIFFI ITALIA S  2026-05-16  Italy  1830 Kgs  1 CAS</p>
          <p>5  SNHBHKGLBG265013  WIRELESS PC CONTROLLER  VALVE CORPORATION  CHENG UEI PRECISION IND. CO LTD  2026-05-12  Hong Kong  12970 Kgs  40 PKG</p>
        </section>
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


def write_executable(path, content):
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


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

    def test_filters_generic_logistics_product_rows_without_valve_signal(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            html = tmp_path / "generic-logistics.html"
            html.write_text(
                IMPORTINFO_HTML.replace("CEVA C/O VALVE CORPORATION", "CEVA LOGISTICS US INC."),
                encoding="utf-8",
            )
            reports = tmp_path / "reports"

            result = run_parser(["--input", f"tech-front-game-console={html}"], reports)

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            self.assertEqual([], read_rows(reports))

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

    def test_extracts_relevant_importgenius_rows(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            html = tmp_path / "importgenius-ingram.html"
            html.write_text(IMPORTGENIUS_HTML, encoding="utf-8")
            reports = tmp_path / "reports"

            result = run_parser(["--input", f"importgenius-ingram-valve={html}"], reports)

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            rows = read_rows(reports)
            self.assertEqual(
                ["SNHBSHACHI265020", "SNHBSHACHI264140", "SNHBSHACHI264031"],
                [row["house_bol"] for row in rows],
            )
            self.assertEqual("GAME CONSOLE", rows[0]["commodity"])
            self.assertEqual("INGRAM MICRO C/O VALVE CORPORATION", rows[0]["consignee"])
            self.assertEqual("TECH-FRONT (CHONGQING) COMPUTER CO", rows[0]["shipper"])
            self.assertEqual("2026-05-18", rows[0]["arrival_date"])
            self.assertEqual("14353 Kgs", rows[0]["weight"])

            key_lines = (reports / "customs-shipments-key-lines.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("SNHBSHACHI265020", key_lines)
            self.assertIn("2026-05-18", key_lines)

    def test_extracts_importgenius_virtual_reality_device_rows(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ceva = tmp_path / "importgenius-ceva.html"
            ceva_nl = tmp_path / "importgenius-ceva-nl.html"
            ceva.write_text(IMPORTGENIUS_CEVA_VR_HTML, encoding="utf-8")
            ceva_nl.write_text(IMPORTGENIUS_CEVA_NL_VR_HTML, encoding="utf-8")
            reports = tmp_path / "reports"

            result = run_parser(
                [
                    "--input",
                    f"importgenius-ceva-valve={ceva}",
                    "--input",
                    f"importgenius-ceva-nl-valve={ceva_nl}",
                ],
                reports,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            rows = read_rows(reports)
            self.assertEqual(
                ["SNHBSHACHI265173", "SNHBSHACHI265174", "SNHBSHALAX265177"],
                [row["house_bol"] for row in rows],
            )
            self.assertTrue(
                all(row["commodity"] == "VIRTUAL REALITY DEVICES" for row in rows)
            )
            self.assertEqual("CEVA C/O VALVE CORPORATION", rows[0]["consignee"])
            self.assertEqual("CEVA NL C/O VALVE CORPORATION", rows[2]["consignee"])

    def test_extracts_importgenius_vertical_table_rows(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            html = tmp_path / "importgenius-ceva-vertical.html"
            html.write_text(IMPORTGENIUS_VERTICAL_CEVA_VR_HTML, encoding="utf-8")
            reports = tmp_path / "reports"

            result = run_parser(["--input", f"importgenius-ceva-valve={html}"], reports)

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            rows = read_rows(reports)
            self.assertEqual(["SNHBSHACHI265173"], [row["house_bol"] for row in rows])
            self.assertEqual("VIRTUAL REALITY DEVICES", rows[0]["commodity"])
            self.assertEqual("6374 Kgs", rows[0]["weight"])

    def test_extracts_importgenius_wireless_pc_controller_rows(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            html = tmp_path / "importgenius-valve-corp.html"
            html.write_text(IMPORTGENIUS_VALVE_CONTROLLER_HTML, encoding="utf-8")
            reports = tmp_path / "reports"

            result = run_parser(["--input", f"importgenius-valve-corp={html}"], reports)

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            rows = read_rows(reports)
            self.assertEqual(
                ["SNHBHKGLBG266011", "SNHBHKGLBG265013"],
                [row["house_bol"] for row in rows],
            )
            self.assertEqual("WIRELESS PC CONTROLLER", rows[0]["commodity"])
            self.assertEqual("VALVE CORPORATION", rows[0]["consignee"])
            self.assertEqual("CHENG UEI PRECISION IND. CO LTD", rows[0]["shipper"])


class CheckCustomsShipmentsShellTests(unittest.TestCase):
    def test_fetches_pages_and_runs_parser(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = tmp_path / "run"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            write_executable(
                fake_bin / "curl",
                f"""
                #!/bin/sh
                cat <<'HTML'
                {IMPORTINFO_HTML}
                HTML
                """,
            )
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"

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
            self.assertTrue(
                (run_dir / "api" / "customs" / "importinfo-ceva-valve.html").exists()
            )
            key_lines = (
                run_dir / "reports" / "customs-shipments-key-lines.txt"
            ).read_text(encoding="utf-8")
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
                """,
            )
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"

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
            errors = (run_dir / "reports" / "customs-shipments-errors.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("failed to fetch", errors)

    def test_records_200_challenge_page_without_key_lines(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = tmp_path / "run"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            write_executable(
                fake_bin / "curl",
                """
                #!/bin/sh
                cat <<'HTML'
                <html><body><h1>Checking your browser</h1><p>Please verify you are human.</p></body></html>
                HTML
                """,
            )
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"

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
            errors = (run_dir / "reports" / "customs-shipments-errors.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("unexpected or blocked content from", errors)
            self.assertFalse(
                (run_dir / "api" / "customs" / "importinfo-ceva-valve.html").exists()
            )
            key_lines = (
                run_dir / "reports" / "customs-shipments-key-lines.txt"
            ).read_text(encoding="utf-8")
            self.assertEqual("", key_lines)

    def test_fetches_importgenius_public_importer_page(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = tmp_path / "run"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            (tmp_path / "importgenius-fixture.html").write_text(
                IMPORTGENIUS_HTML, encoding="utf-8"
            )
            write_executable(
                fake_bin / "curl",
                f"""
                #!/bin/sh
                for arg do
                  url="$arg"
                done
                case "$url" in
                  *importgenius.com/importers/ingram-micro-c-o-valve-corporation)
                    cat "{tmp_path / "importgenius-fixture.html"}"
                    ;;
                  *)
                    exit 22
                    ;;
                esac
                """,
            )
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"

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
            self.assertTrue(
                (
                    run_dir
                    / "api"
                    / "customs"
                    / "importgenius-ingram-valve.html"
                ).exists()
            )
            key_lines = (
                run_dir / "reports" / "customs-shipments-key-lines.txt"
            ).read_text(encoding="utf-8")
            self.assertIn("SNHBSHACHI265020", key_lines)

    def test_fetches_additional_importgenius_valve_importer_pages(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = tmp_path / "run"
            fake_bin = tmp_path / "bin"
            fake_bin.mkdir()
            (tmp_path / "importgenius-ingram-fixture.html").write_text(
                IMPORTGENIUS_HTML, encoding="utf-8"
            )
            (tmp_path / "importgenius-ceva-fixture.html").write_text(
                IMPORTGENIUS_CEVA_VR_HTML, encoding="utf-8"
            )
            (tmp_path / "importgenius-ceva-nl-fixture.html").write_text(
                IMPORTGENIUS_CEVA_NL_VR_HTML, encoding="utf-8"
            )
            (tmp_path / "importgenius-valve-corp-fixture.html").write_text(
                IMPORTGENIUS_VALVE_CONTROLLER_HTML, encoding="utf-8"
            )
            write_executable(
                fake_bin / "curl",
                f"""
                #!/bin/sh
                for arg do
                  url="$arg"
                done
                case "$url" in
                  *importgenius.com/importers/ingram-micro-c-o-valve-corporation)
                    cat "{tmp_path / "importgenius-ingram-fixture.html"}"
                    ;;
                  *importgenius.com/importers/ceva-c-o-valve-corporation)
                    cat "{tmp_path / "importgenius-ceva-fixture.html"}"
                    ;;
                  *importgenius.com/importers/ceva-nl-c-o-valve-corporation)
                    cat "{tmp_path / "importgenius-ceva-nl-fixture.html"}"
                    ;;
                  *importgenius.com/importers/valve-corp)
                    cat "{tmp_path / "importgenius-valve-corp-fixture.html"}"
                    ;;
                  *)
                    exit 22
                    ;;
                esac
                """,
            )
            env = os.environ.copy()
            env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"

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
            customs_dir = run_dir / "api" / "customs"
            self.assertTrue((customs_dir / "importgenius-ceva-valve.html").exists())
            self.assertTrue((customs_dir / "importgenius-ceva-nl-valve.html").exists())
            self.assertTrue((customs_dir / "importgenius-valve-corp.html").exists())
            key_lines = (
                run_dir / "reports" / "customs-shipments-key-lines.txt"
            ).read_text(encoding="utf-8")
            self.assertIn("SNHBSHACHI265173", key_lines)
            self.assertIn("SNHBSHALAX265177", key_lines)
            self.assertIn("SNHBHKGLBG266011", key_lines)


class CustomsSummaryIntegrationTests(unittest.TestCase):
    def test_run_summary_and_status_draft_include_customs_lines(self):
        with TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "2026-05-05"
            reports = run_dir / "reports"
            reports.mkdir(parents=True)
            (reports / "customs-shipments-key-lines.txt").write_text(
                "2026-05-01\tCEVA C/O VALVE CORPORATION\tTECH-FRONT (CHONGQING) COMPUTER CO\tGAME CONSOLE\t42 PKG\t12596 Kgs\tSNHBSHALAX264015\n",
                encoding="utf-8",
            )
            (reports / "customs-shipments-errors.txt").write_text("", encoding="utf-8")

            summary = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "write_run_summary.py"),
                    "--run-dir",
                    str(run_dir),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            draft = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "draft_status_update.py"),
                    "--run-dir",
                    str(run_dir),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(0, summary.returncode)
            self.assertEqual(0, draft.returncode)
            run_summary = (reports / "run-summary.md").read_text(encoding="utf-8")
            status_draft = (reports / "status-draft.md").read_text(encoding="utf-8")
            self.assertIn("Customs shipments", run_summary)
            self.assertIn("SNHBSHALAX264015", run_summary)
            self.assertIn("Customs / Shipments", status_draft)
            self.assertIn("GAME CONSOLE", status_draft)

    def test_customs_rows_with_source_errors_are_reported_as_partial(self):
        with TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "2026-05-22"
            reports = run_dir / "reports"
            reports.mkdir(parents=True)
            (reports / "customs-shipments-key-lines.txt").write_text(
                "2026-05-18\tINGRAM MICRO C/O VALVE CORPORATION\tTECH-FRONT (CHONGQING) COMPUTER CO\tGAME CONSOLE\t42 PKG\t14353 Kgs\tSNHBSHACHI265020\n",
                encoding="utf-8",
            )
            (reports / "customs-shipments-errors.txt").write_text(
                "failed to fetch https://www.importinfo.com/search?s=CEVA%20C%2FO%20VALVE%20CORPORATION\n",
                encoding="utf-8",
            )
            (reports / "customs-shipments.md").write_text(
                "# Customs Shipments\n\nRelevant shipment count: 1\n",
                encoding="utf-8",
            )

            summary = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "write_run_summary.py"),
                    "--run-dir",
                    str(run_dir),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            draft = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "draft_status_update.py"),
                    "--run-dir",
                    str(run_dir),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(0, summary.returncode)
            self.assertEqual(0, draft.returncode)
            run_summary = (reports / "run-summary.md").read_text(encoding="utf-8")
            status_draft = (reports / "status-draft.md").read_text(encoding="utf-8")
            self.assertIn("Customs shipments status: `partial`", run_summary)
            self.assertIn("Customs shipment rows were captured", status_draft)
            self.assertIn("SNHBSHACHI265020", status_draft)

    def test_status_draft_reports_missing_customs_outputs_as_unavailable(self):
        with TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "2026-05-05"
            reports = run_dir / "reports"
            reports.mkdir(parents=True)

            draft = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "draft_status_update.py"),
                    "--run-dir",
                    str(run_dir),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            summary = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "write_run_summary.py"),
                    "--run-dir",
                    str(run_dir),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(0, draft.returncode)
            self.assertEqual(0, summary.returncode)
            status_draft = (reports / "status-draft.md").read_text(encoding="utf-8")
            run_summary = (reports / "run-summary.md").read_text(encoding="utf-8")
            self.assertIn("Customs / Shipments", status_draft)
            self.assertIn("not generated", status_draft)
            self.assertNotIn("No relevant customs shipment rows found.", status_draft)
            self.assertIn("Customs shipments status: `unavailable`", run_summary)


if __name__ == "__main__":
    unittest.main()
