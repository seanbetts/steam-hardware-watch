import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.write_frame_focus_report import build


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


class FrameFocusReportTests(unittest.TestCase):
    def make_run_dir(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        run_dir = Path(tmp.name) / "2026-06-24"
        (run_dir / "reports").mkdir(parents=True)
        return run_dir

    def write_baseline_reports(self, run_dir: Path):
        reports = run_dir / "reports"
        write(
            reports / "valve-reservation-packages.tsv",
            """
            type\tproduct\tid\tstatus\tname\trelease_or_price\tdetails
            app\tSteam Frame\t4165890\tpublic\tSteam Frame\tComing soon\tpackages=; package_groups=0; coming_soon=True; price=
            package\tSteam Frame\t1629484\tprivate\t\t\tpackagedetails success:false
            package\tSteam Frame\t1629486\tprivate\t\t\tpackagedetails success:false
            app\tSteam Machine\t4165910\tpublic\tSteam Machine\t$1,049.00\tpackages=1629447,1629458,1629446,1629460; package_groups=1; coming_soon=False; price=$1,049.00
            """,
        )
        write(
            reports / "steamkit-pics-packages.tsv",
            """
            type\tproduct\tid\tstatus\tchangenumber\tprevious_changenumber\tchanged_since_previous\tsha_hash\tonly_public\tname\trelated_ids\tdetails
            app\tSteam Frame\t4165890\tprivate_metadata_token_required\t35675573\t35675573\tno\tabc\tTrue\tSteam Frame\t\tdepots_count=0
            package\tSteam Frame\t1629484\tprivate_metadata_token_required\t35672606\t35672606\tno\t\tFalse\t\t\tapps_count=0
            package\tSteam Frame\t1629486\tprivate_metadata_token_required\t35672606\t35672606\tno\t\tFalse\t\t\tapps_count=0
            package\tSteam Machine\t1629446\tavailable\t36785426\t36756963\tyes\tdef\tFalse\t\t\tapps_count=1
            """,
        )
        write(
            reports / "steamdb-reservation-packages.tsv",
            """
            product\tpackage_id\tlast_record_update\tlast_changenumber\tpossible_apps\tstatus
            Steam Frame\t1629484\t5 May 2026 - 18:50:54 UTC\t35672606\t4165890:Steam Frame\tprivate_exists_only
            Steam Frame\t1629486\t5 May 2026 - 18:50:54 UTC\t35672606\t4165890:Steam Frame\tprivate_exists_only
            """,
        )
        write(
            reports / "komodo-product-modified.tsv",
            """
            machine\t2026-06-24T16:12:21
            frame\t2026-05-27T16:53:46
            """,
        )
        write(
            reports / "customs-shipments.md",
            """
            | arrival_date | shipper | consignee | description |
            | 2026-06-17 | TECH-FRONT | VALVE | VIRTUAL REALITY DEVICES |
            """,
        )

    def test_baseline_private_frame_reports_no_public_readiness(self):
        run_dir = self.make_run_dir()
        self.write_baseline_reports(run_dir)

        report = build(run_dir)

        self.assertIn("No public Steam Frame readiness change detected.", report)
        self.assertIn("Frame app: `4165890`", report)
        self.assertIn("Frame packages: `1629484`, `1629486`", report)
        self.assertIn("status=private", report)
        self.assertIn("product=frame; modified=2026-05-27T16:53:46", report)
        self.assertIn("Steam Machine is now a launched comparator", report)
        self.assertIn("VIRTUAL REALITY DEVICES", report)

    def test_public_frame_package_reports_public_readiness(self):
        run_dir = self.make_run_dir()
        self.write_baseline_reports(run_dir)
        write(
            run_dir / "reports" / "valve-reservation-packages.tsv",
            """
            type\tproduct\tid\tstatus\tname\trelease_or_price\tdetails
            app\tSteam Frame\t4165890\tpublic\tSteam Frame\t$499.00\tpackages=1629484; package_groups=1; coming_soon=False; price=$499.00
            package\tSteam Frame\t1629484\tpublic\tSteam Frame 256GB\t\tapps=4165890:Steam Frame
            package\tSteam Frame\t1629486\tprivate\t\t\tpackagedetails success:false
            """,
        )

        report = build(run_dir)

        self.assertIn("Steam Frame public readiness detected.", report)
        self.assertIn("package_groups=1", report)
        self.assertIn("status=public", report)


if __name__ == "__main__":
    unittest.main()
