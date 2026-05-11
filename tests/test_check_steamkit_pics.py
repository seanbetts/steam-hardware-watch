import os
import stat
import subprocess
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


def write_executable(path, content):
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class CheckSteamKitPicsTests(unittest.TestCase):
    def test_missing_credentials_writes_nonfatal_unavailable_report(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_path = Path(tmp.name)
        run_dir = tmp_path / "run"
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()

        write_executable(
            fake_bin / "dotnet",
            """
            #!/bin/sh
            echo "dotnet should not be called without credentials" >&2
            exit 9
            """,
        )

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fake_bin}:{env['PATH']}",
                "STEAMKIT_ENV_FILE": str(tmp_path / "missing-env.sh"),
            }
        )
        env.pop("STEAMKIT_USERNAME", None)
        env.pop("STEAMKIT_PASSWORD", None)

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_steamkit_pics.sh"), str(run_dir)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        report = (run_dir / "reports" / "steamkit-pics-packages.tsv").read_text(
            encoding="utf-8"
        )
        self.assertIn("package\tSteam Frame\t1629484\tmissing_credentials", report)
        self.assertIn("app\tSteam Machine\t4165910\tmissing_credentials", report)

        key_lines = (run_dir / "reports" / "steamkit-pics-key-lines.txt").read_text(
            encoding="utf-8"
        )
        self.assertIn("SteamKit/PICS unavailable", key_lines)
        errors = (run_dir / "reports" / "steamkit-pics-errors.txt").read_text(
            encoding="utf-8"
        )
        self.assertIn("STEAMKIT_USERNAME/STEAMKIT_PASSWORD", errors)

    def test_invokes_dotnet_helper_when_credentials_are_available(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_path = Path(tmp.name)
        run_dir = tmp_path / "run"
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()
        log_path = tmp_path / "dotnet-args.log"

        write_executable(
            fake_bin / "dotnet",
            """
            #!/bin/sh
            printf '%s\\n' "$*" > "$FAKE_DOTNET_LOG"

            out_dir=""
            report=""
            key_lines=""
            markdown=""
            while [ "$#" -gt 0 ]; do
              case "$1" in
                --out-dir)
                  shift
                  out_dir="$1"
                  ;;
                --report)
                  shift
                  report="$1"
                  ;;
                --key-lines)
                  shift
                  key_lines="$1"
                  ;;
                --markdown-report)
                  shift
                  markdown="$1"
                  ;;
              esac
              shift || true
            done

            mkdir -p "$out_dir" "$(dirname "$report")" "$(dirname "$key_lines")" "$(dirname "$markdown")"
            printf '%s\\n' '{"packages":{"1629484":{"change_number":35500001}}}' > "$out_dir/pics-product-info.json"
            {
              printf '%s\\n' 'type	product	id	status	changenumber	previous_changenumber	changed_since_previous	sha_hash	only_public	name	related_ids	details'
              printf '%s\\n' 'package	Steam Frame	1629484	available	35500001	35500000	yes	abc123	False		4165890	apps=4165890:Steam Frame'
            } > "$report"
            {
              printf '%s\\n' 'SteamKit/PICS package snapshot:'
              printf '%s\\n' 'package	Steam Frame	1629484	available	35500001	35500000	yes	abc123	False		4165890	apps=4165890:Steam Frame'
            } > "$key_lines"
            printf '%s\\n' '# SteamKit / PICS Detail' > "$markdown"
            """,
        )

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fake_bin}:{env['PATH']}",
                "STEAMKIT_ENV_FILE": str(tmp_path / "missing-env.sh"),
                "STEAMKIT_USERNAME": "watcher",
                "STEAMKIT_PASSWORD": "secret",
                "FAKE_DOTNET_LOG": str(log_path),
            }
        )

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_steamkit_pics.sh"), str(run_dir)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        dotnet_args = log_path.read_text(encoding="utf-8")
        self.assertIn("run --project", dotnet_args)
        self.assertIn("tools/steamkit-pics", dotnet_args)
        self.assertIn("--markdown-report", dotnet_args)

        report = (run_dir / "reports" / "steamkit-pics-packages.tsv").read_text(
            encoding="utf-8"
        )
        self.assertIn("previous_changenumber\tchanged_since_previous", report)
        self.assertIn("package\tSteam Frame\t1629484\tavailable\t35500001\t35500000\tyes", report)
        self.assertTrue(
            (run_dir / "api" / "steamkit" / "pics-product-info.json").exists()
        )
        self.assertTrue((run_dir / "reports" / "steamkit-pics-detail.md").exists())

    def test_passes_previous_report_when_prior_run_exists(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_path = Path(tmp.name)
        previous_run = tmp_path / "2026-05-10"
        run_dir = tmp_path / "2026-05-11"
        previous_reports = previous_run / "reports"
        previous_reports.mkdir(parents=True)
        previous_report = previous_reports / "steamkit-pics-packages.tsv"
        previous_report.write_text(
            "type\tproduct\tid\tstatus\tchangenumber\tprevious_changenumber\tchanged_since_previous\tsha_hash\tonly_public\tname\trelated_ids\tdetails\n"
            "package\tSteam Frame\t1629484\tprivate_metadata_token_required\t35500000\t\t\tabc122\tFalse\t\t\tapps=\n",
            encoding="utf-8",
        )
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()
        log_path = tmp_path / "dotnet-args.log"

        write_executable(
            fake_bin / "dotnet",
            """
            #!/bin/sh
            printf '%s\\n' "$*" > "$FAKE_DOTNET_LOG"
            previous=""
            report=""
            key_lines=""
            markdown=""
            out_dir=""
            while [ "$#" -gt 0 ]; do
              case "$1" in
                --previous-report)
                  shift
                  previous="$1"
                  ;;
                --out-dir)
                  shift
                  out_dir="$1"
                  ;;
                --report)
                  shift
                  report="$1"
                  ;;
                --key-lines)
                  shift
                  key_lines="$1"
                  ;;
                --markdown-report)
                  shift
                  markdown="$1"
                  ;;
              esac
              shift || true
            done
            test -s "$previous" || exit 11
            mkdir -p "$out_dir" "$(dirname "$report")" "$(dirname "$key_lines")" "$(dirname "$markdown")"
            printf '%s\\n' '{}' > "$out_dir/pics-product-info.json"
            printf '%s\\n' 'type	product	id	status	changenumber	previous_changenumber	changed_since_previous	sha_hash	only_public	name	related_ids	details' > "$report"
            printf '%s\\n' 'SteamKit/PICS package snapshot:' > "$key_lines"
            printf '%s\\n' '# SteamKit / PICS Detail' > "$markdown"
            """,
        )

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fake_bin}:{env['PATH']}",
                "STEAMKIT_ENV_FILE": str(tmp_path / "missing-env.sh"),
                "STEAMKIT_USERNAME": "watcher",
                "STEAMKIT_PASSWORD": "secret",
                "FAKE_DOTNET_LOG": str(log_path),
            }
        )

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_steamkit_pics.sh"), str(run_dir)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        dotnet_args = log_path.read_text(encoding="utf-8")
        self.assertIn("--previous-report", dotnet_args)
        self.assertIn(str(previous_report), dotnet_args)

    def test_exports_credentials_loaded_from_local_env_file_to_dotnet_helper(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_path = Path(tmp.name)
        run_dir = tmp_path / "run"
        env_file = tmp_path / "steamkit-env.sh"
        env_file.write_text(
            "STEAMKIT_USERNAME='watcher-from-file'\n"
            "STEAMKIT_PASSWORD='secret-from-file'\n",
            encoding="utf-8",
        )
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()

        write_executable(
            fake_bin / "dotnet",
            """
            #!/bin/sh
            if [ "$STEAMKIT_USERNAME" != "watcher-from-file" ]; then
              echo "missing username export" >&2
              exit 7
            fi
            if [ "$STEAMKIT_PASSWORD" != "secret-from-file" ]; then
              echo "missing password export" >&2
              exit 8
            fi

            out_dir=""
            report=""
            key_lines=""
            markdown=""
            while [ "$#" -gt 0 ]; do
              case "$1" in
                --out-dir)
                  shift
                  out_dir="$1"
                  ;;
                --report)
                  shift
                  report="$1"
                  ;;
                --key-lines)
                  shift
                  key_lines="$1"
                  ;;
                --markdown-report)
                  shift
                  markdown="$1"
                  ;;
              esac
              shift || true
            done

            mkdir -p "$out_dir" "$(dirname "$report")" "$(dirname "$key_lines")" "$(dirname "$markdown")"
            printf '%s\\n' '{}' > "$out_dir/pics-product-info.json"
            printf '%s\\n' 'type	product	id	status	changenumber	related_ids	details' > "$report"
            printf '%s\\n' 'SteamKit/PICS package snapshot:' > "$key_lines"
            printf '%s\\n' '# SteamKit / PICS Detail' > "$markdown"
            """,
        )

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fake_bin}:{env['PATH']}",
                "STEAMKIT_ENV_FILE": str(env_file),
            }
        )
        env.pop("STEAMKIT_USERNAME", None)
        env.pop("STEAMKIT_PASSWORD", None)

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_steamkit_pics.sh"), str(run_dir)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        errors = (run_dir / "reports" / "steamkit-pics-errors.txt").read_text(
            encoding="utf-8"
        )
        self.assertEqual("", errors)


class SteamKitSummaryTests(unittest.TestCase):
    def test_status_draft_and_run_summary_include_steamkit_outputs(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        run_dir = Path(tmp.name) / "2026-05-11"
        reports = run_dir / "reports"
        reports.mkdir(parents=True)
        (reports / "steamkit-pics-key-lines.txt").write_text(
            "SteamKit/PICS package snapshot:\n"
            "package\tSteam Frame\t1629484\tprivate_metadata_token_required\t35500001\t35500000\tyes\tabc123\tFalse\t\t4165890\tapps=4165890:Steam Frame\n",
            encoding="utf-8",
        )
        (reports / "steamkit-pics-errors.txt").write_text("", encoding="utf-8")

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

        self.assertEqual("", summary.stderr)
        self.assertEqual(0, summary.returncode)
        self.assertEqual("", draft.stderr)
        self.assertEqual(0, draft.returncode)

        run_summary = (reports / "run-summary.md").read_text(encoding="utf-8")
        self.assertIn("- SteamKit/PICS blocked: `no`", run_summary)
        self.assertIn("- SteamKit/PICS: `package Steam Frame 1629484", run_summary)

        status_draft = (reports / "status-draft.md").read_text(encoding="utf-8")
        self.assertIn("#### SteamKit / PICS", status_draft)
        self.assertIn("- `package\tSteam Frame\t1629484", status_draft)


if __name__ == "__main__":
    unittest.main()
