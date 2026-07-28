import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RunWatchCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.scripts = self.repo / "scripts"
        self.scripts.mkdir()
        (self.repo / "status" / "runs").mkdir(parents=True)
        self.log = self.repo / "calls.log"

        os.symlink(ROOT / "scripts" / "run_watch.sh", self.scripts / "run_watch.sh")
        os.symlink(ROOT / "scripts" / "run_frame_watch.sh", self.scripts / "run_frame_watch.sh")

        self._write_script(
            "init_run.sh",
            """
            #!/bin/sh
            set -eu
            run_date="$1"
            base_dir="$2"
            run_dir="$base_dir/$run_date"
            mkdir -p "$run_dir/reports" "$run_dir/api"
            run_note="$PWD/status/runs/$run_date.md"
            printf 'init_run %s %s\\n' "$run_date" "$base_dir" >> "$CALL_LOG"
            printf 'RUN_DIR=%s\\nRUN_NOTE=%s\\n' "$run_dir" "$run_note"
            """,
        )
        self._write_script(
            "check_komodo.sh",
            """
            #!/bin/sh
            set -eu
            printf 'check_komodo %s\\n' "$1" >> "$CALL_LOG"
            mkdir -p "$1/reports"
            {
              printf 'controller\\t%s\\n' "${KOMODO_CONTROLLER_MODIFIED:-2026-07-27T15:46:17}"
              printf 'machine\\t%s\\n' "${KOMODO_MACHINE_MODIFIED:-2026-07-27T15:39:56}"
              printf 'frame\\t%s\\n' "${KOMODO_FRAME_MODIFIED:-2026-07-03T15:56:30}"
            } > "$1/reports/komodo-product-modified.tsv"
            {
              printf '413804\\timage/png\\thttps://komodostation.com/wp-content/uploads/2025/11/Frame_BG.png\\n'
              printf '456489\\timage/jpeg\\thttps://komodostation.com/wp-content/uploads/2025/11/source_SF_headsetControllers_front_2.jpg\\n'
              if [ -n "${KOMODO_EXTRA_ASSET_URL:-}" ]; then
                printf '999999\\timage/jpeg\\t%s\\n' "$KOMODO_EXTRA_ASSET_URL"
              fi
            } > "$1/reports/komodo-visual-assets.tsv"
            """,
        )
        self._write_python(
            "write_run_summary.py",
            """
            import sys
            from pathlib import Path
            Path(__import__("os").environ["CALL_LOG"]).open("a").write("write_run_summary " + " ".join(sys.argv[1:]) + "\\n")
            output = Path(sys.argv[sys.argv.index("--output") + 1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text("# Summary\\n", encoding="utf-8")
            """,
        )

        for name in [
            "check_steamkit_pics.sh",
            "check_steamdb.sh",
            "check_steamtracking.sh",
            "check_steamvr_depots.sh",
            "check_steamos_mirror.sh",
            "check_valve_endpoints.sh",
            "check_customs_shipments.sh",
            "save_visual_assets.py",
            "compare_runs.py",
            "write_frame_focus_report.py",
            "draft_status_update.py",
        ]:
            if name.endswith(".py"):
                self._write_python(name, f"raise SystemExit('unexpected {name}')\n")
            else:
                self._write_script(
                    name,
                    f"""
                    #!/bin/sh
                    echo 'unexpected {name}' >&2
                    exit 42
                    """,
                )

    def _write_script(self, name, body):
        path = self.scripts / name
        path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
        path.chmod(0o755)

    def _write_python(self, name, body):
        path = self.scripts / name
        path.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
        path.chmod(0o755)

    def run_script(self, *args):
        env = os.environ.copy()
        env["CALL_LOG"] = str(self.log)
        return subprocess.run(
            list(args),
            cwd=self.repo,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def write_previous_komodo_report(
        self,
        run_date,
        frame_modified,
        controller_modified="2026-07-27T15:46:17",
        machine_modified="2026-07-27T15:39:56",
    ):
        report = self.repo / "runs" / run_date / "reports" / "komodo-product-modified.tsv"
        report.parent.mkdir(parents=True)
        report.write_text(
            "\n".join(
                [
                    f"controller\t{controller_modified}",
                    f"machine\t{machine_modified}",
                    f"frame\t{frame_modified}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def write_previous_komodo_assets(self, run_date, extra_urls=None):
        report = self.repo / "runs" / run_date / "reports" / "komodo-visual-assets.tsv"
        report.parent.mkdir(parents=True, exist_ok=True)
        rows = [
            "413804\timage/png\thttps://komodostation.com/wp-content/uploads/2025/11/Frame_BG.png",
            "456489\timage/jpeg\thttps://komodostation.com/wp-content/uploads/2025/11/source_SF_headsetControllers_front_2.jpg",
        ]
        for index, url in enumerate(extra_urls or [], start=1):
            rows.append(f"99999{index}\timage/jpeg\t{url}")
        report.write_text("\n".join(rows + [""]), encoding="utf-8")

    def test_run_watch_komodo_only_runs_komodo_and_skips_other_sources(self):
        base_dir = self.repo / "runs"
        self.write_previous_komodo_report("2099-01-01", "2026-07-03T15:56:30")
        self.write_previous_komodo_assets("2099-01-01")

        result = self.run_script(
            str(self.scripts / "run_watch.sh"),
            "--komodo-only",
            "2099-01-02",
            str(base_dir),
            "/tmp/not-used",
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        self.assertIn(f"Run dir: {base_dir / '2099-01-02'}", result.stdout)
        self.assertIn("Komodo updated: no (matches previous run 2099-01-01)", result.stdout)
        self.assertIn(
            "Komodo timestamps: controller=2026-07-27T15:46:17, machine=2026-07-27T15:39:56, frame=2026-07-03T15:56:30",
            result.stdout,
        )
        self.assertIn("Komodo new assets: no (2 current, matches previous run 2099-01-01)", result.stdout)
        self.assertIn("Komodo-only run complete.", result.stdout)
        calls = self.log.read_text(encoding="utf-8")
        self.assertIn("check_komodo", calls)
        self.assertIn("write_run_summary", calls)
        self.assertNotIn("unexpected", calls)

    def test_run_frame_watch_komodo_only_does_not_write_frame_focus_report(self):
        base_dir = self.repo / "runs"

        result = self.run_script(
            str(self.scripts / "run_frame_watch.sh"),
            "--komodo-only",
            "2099-01-03",
            str(base_dir),
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        self.assertIn("Komodo-only run complete.", result.stdout)
        calls = self.log.read_text(encoding="utf-8")
        self.assertIn("check_komodo", calls)
        self.assertNotIn("write_frame_focus_report", calls)

    def test_run_watch_komodo_only_reports_when_komodo_changed(self):
        base_dir = self.repo / "runs"
        self.write_previous_komodo_report("2099-01-03", "2026-07-03T15:56:30")
        self.write_previous_komodo_assets("2099-01-03")
        os.environ["KOMODO_FRAME_MODIFIED"] = "2026-07-28T10:11:12"
        self.addCleanup(lambda: os.environ.pop("KOMODO_FRAME_MODIFIED", None))

        result = self.run_script(
            str(self.scripts / "run_watch.sh"),
            "--komodo-only",
            "2099-01-04",
            str(base_dir),
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        self.assertIn("Komodo updated: yes (changed since previous run 2099-01-03)", result.stdout)
        self.assertIn("Komodo changes:", result.stdout)
        self.assertIn("- frame: 2026-07-03T15:56:30 -> 2026-07-28T10:11:12", result.stdout)
        self.assertIn(
            "Komodo timestamps: controller=2026-07-27T15:46:17, machine=2026-07-27T15:39:56, frame=2026-07-28T10:11:12",
            result.stdout,
        )

    def test_run_watch_komodo_only_reports_new_asset_urls(self):
        base_dir = self.repo / "runs"
        self.write_previous_komodo_report("2099-01-05", "2026-07-03T15:56:30")
        self.write_previous_komodo_assets("2099-01-05")
        new_url = "https://komodostation.com/wp-content/uploads/2026/07/new-frame-asset.jpg"
        os.environ["KOMODO_EXTRA_ASSET_URL"] = new_url
        self.addCleanup(lambda: os.environ.pop("KOMODO_EXTRA_ASSET_URL", None))

        result = self.run_script(
            str(self.scripts / "run_watch.sh"),
            "--komodo-only",
            "2099-01-06",
            str(base_dir),
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        self.assertIn("Komodo new assets: yes (1 new, 3 current, since previous run 2099-01-05)", result.stdout)
        self.assertIn("Komodo new asset URLs:", result.stdout)
        self.assertIn(f"- {new_url}", result.stdout)


if __name__ == "__main__":
    unittest.main()
