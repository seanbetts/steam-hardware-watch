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


class CheckSteamOSMirrorTests(unittest.TestCase):
    def test_fetches_repo_metadata_and_extracts_interesting_packages(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_path = Path(tmp.name)
        run_dir = tmp_path / "run"
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()

        write_executable(
            fake_bin / "curl",
            """
            #!/bin/sh
            for arg in "$@"; do
              url="$arg"
            done
            case "$url" in
              */archlinux-mirror/)
                printf '%s\\n' '<a href="jupiter-main/">jupiter-main/</a><a href="holo-main/">holo-main/</a><a href="fremont-main/">fremont-main/</a>'
                ;;
              */archlinux-mirror/sources/)
                printf '%s\\n' '<a href="jupiter-main/">jupiter-main/</a><a href="deckard-main/">deckard-main/</a>'
                ;;
              */jupiter-main.db|*/holo-main.db)
                printf '%s\\n' 'fake db'
                ;;
              *)
                echo "unexpected url: $url" >&2
                exit 22
                ;;
            esac
            """,
        )
        write_executable(
            fake_bin / "bsdtar",
            """
            #!/bin/sh
            out=""
            while [ "$#" -gt 0 ]; do
              if [ "$1" = "-C" ]; then
                shift
                out="$1"
              fi
              shift || true
            done
            mkdir -p "$out/jupiter-hw-support-20260413.1-1" "$out/steam-frame-config-1-1"
            cat > "$out/jupiter-hw-support-20260413.1-1/desc" <<'EOF'
            %NAME%
            jupiter-hw-support
            %VERSION%
            20260413.1-1
            EOF
            cat > "$out/steam-frame-config-1-1/desc" <<'EOF'
            %NAME%
            steam-frame-config
            %VERSION%
            1-1
            EOF
            """,
        )

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fake_bin}:{env['PATH']}",
                "STEAMOS_MIRROR_REPOS": "jupiter-main holo-main",
            }
        )

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_steamos_mirror.sh"), str(run_dir)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        key_lines = (run_dir / "reports" / "steamos-mirror-key-lines.txt").read_text(
            encoding="utf-8"
        )
        repos = (run_dir / "reports" / "steamos-mirror-interesting-repos.txt").read_text(
            encoding="utf-8"
        )
        self.assertIn("steam-frame-config", key_lines)
        self.assertIn("fremont-main", repos)
        self.assertIn("deckard-main", repos)


class CheckSteamVRDepotsTests(unittest.TestCase):
    def test_rejects_challenge_pages_and_scans_local_snapshots(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_path = Path(tmp.name)
        run_dir = tmp_path / "run"
        snapshot_dir = tmp_path / "steamvr"
        dashboard_dir = snapshot_dir / "resources" / "webinterface"
        dashboard_dir.mkdir(parents=True)
        (dashboard_dir / "dashboard.js").write_text(
            "const activeFrame = 'Steam Frame'; const codename = 'Deckard';",
            encoding="utf-8",
        )

        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()
        write_executable(
            fake_bin / "curl",
            """
            #!/bin/sh
            for arg in "$@"; do
              url="$arg"
            done
            case "$url" in
              *steamdb.info*)
                printf '%s\\n' '<html><title>Just a moment...</title><body>Checking your browser Cloudflare</body></html>'
                ;;
              *ISteamNews*)
                printf '%s\\n' '{"appnews":{"appid":250820,"newsitems":[{"title":"SteamVR Beta Updated - 2.13.1","contents":"Frame dashboard update"}]}}'
                ;;
              *)
                echo "unexpected url: $url" >&2
                exit 22
                ;;
            esac
            """,
        )

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fake_bin}:{env['PATH']}",
                "STEAMVR_SCAN_DIRS": str(snapshot_dir),
            }
        )

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_steamvr_depots.sh"), str(run_dir)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        self.assertFalse((run_dir / "api" / "steamvr-depots" / "steamdb-depots.html").exists())
        errors = (run_dir / "reports" / "steamvr-depots-errors.txt").read_text(
            encoding="utf-8"
        )
        key_lines = (run_dir / "reports" / "steamvr-depots-key-lines.txt").read_text(
            encoding="utf-8"
        )
        self.assertIn("blocked or challenge page", errors)
        self.assertIn("Steam Frame", key_lines)
        self.assertIn("Deckard", key_lines)

    def test_uses_steamdb_playwright_fallback_for_depot_page(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_path = Path(tmp.name)
        run_dir = tmp_path / "run"
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()
        log_dir = tmp_path / "logs"
        log_dir.mkdir()

        write_executable(
            fake_bin / "curl",
            """
            #!/bin/sh
            for arg in "$@"; do
              url="$arg"
            done
            case "$url" in
              *steamdb.info*)
                printf '%s\\n' '<html><title>Just a moment...</title><body>Checking your browser Cloudflare</body></html>'
                ;;
              *ISteamNews*)
                printf '%s\\n' '{"appnews":{"appid":250820,"newsitems":[]}}'
                ;;
              *)
                echo "unexpected url: $url" >&2
                exit 22
                ;;
            esac
            """,
        )
        write_executable(
            fake_bin / "node",
            """
            #!/bin/sh
            printf '%s\\n' "$*" >> "$FAKE_LOG_DIR/node-args.log"
            output=""
            for arg in "$@"; do
              output="$arg"
            done
            printf '%s\\n' '<html><body><table><tr><td>250823</td><td>Linux OpenVR Linux</td></tr><tr><td>Build ID</td><td>123</td></tr><tr><td>public</td><td>Steam Frame depot note</td></tr></table></body></html>' > "$output"
            """,
        )

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fake_bin}:{env['PATH']}",
                "FAKE_LOG_DIR": str(log_dir),
                "STEAMDB_PLAYWRIGHT_FALLBACK": "1",
                "STEAMDB_AUTO_BOOTSTRAP": "0",
            }
        )

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_steamvr_depots.sh"), str(run_dir)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        self.assertTrue((log_dir / "node-args.log").exists())
        self.assertTrue((run_dir / "api" / "steamvr-depots" / "steamdb-depots.html").exists())
        errors = (run_dir / "reports" / "steamvr-depots-errors.txt").read_text(
            encoding="utf-8"
        )
        key_lines = (run_dir / "reports" / "steamvr-depots-key-lines.txt").read_text(
            encoding="utf-8"
        )
        self.assertEqual("", errors)
        self.assertIn("Steam Frame", key_lines)

    def test_steamdb_playwright_fallback_bootstraps_when_cdp_is_stale(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_path = Path(tmp.name)
        run_dir = tmp_path / "run"
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        env_file = tmp_path / "steamdb-env.sh"
        bootstrap_log = tmp_path / "bootstrap.log"

        env_file.write_text(
            "\n".join(
                [
                    "export STEAMDB_PLAYWRIGHT_FALLBACK=1",
                    f'export STEAMDB_PROFILE_DIR="{tmp_path / "profile"}"',
                    'export STEAMDB_CDP_ENDPOINT="http://127.0.0.1:9"',
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        write_executable(
            fake_bin / "curl",
            """
            #!/bin/sh
            case "$*" in
              *127.0.0.1:9/json/version*)
                exit 7
                ;;
              *steamdb.info*)
                printf '%s\\n' '<html><title>Just a moment...</title><body>Checking your browser Cloudflare</body></html>'
                ;;
              *ISteamNews*)
                printf '%s\\n' '{"appnews":{"appid":250820,"newsitems":[]}}'
                ;;
              *)
                echo "unexpected args: $*" >&2
                exit 22
                ;;
            esac
            """,
        )
        write_executable(
            fake_bin / "node",
            """
            #!/bin/sh
            printf '%s\\n' "$*" >> "$FAKE_LOG_DIR/node-args.log"
            output=""
            for arg in "$@"; do
              output="$arg"
            done
            printf '%s\\n' '<html><body><table><tr><td>public</td><td>Steam Frame depot note</td></tr></table></body></html>' > "$output"
            """,
        )
        write_executable(
            tmp_path / "bootstrap-steamdb.sh",
            f"#!/bin/sh\nprintf '%s\\n' bootstrap >> '{bootstrap_log}'\ncat > '{env_file}' <<'EOF'\nexport STEAMDB_PLAYWRIGHT_FALLBACK=1\nexport STEAMDB_PROFILE_DIR=\"{tmp_path / 'profile'}\"\nexport STEAMDB_CDP_ENDPOINT=\"http://127.0.0.1:55685\"\nEOF\n",
        )

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fake_bin}:{env['PATH']}",
                "FAKE_LOG_DIR": str(log_dir),
                "STEAMDB_ENV_FILE": str(env_file),
                "STEAMDB_BOOTSTRAP_CMD": str(tmp_path / "bootstrap-steamdb.sh"),
            }
        )

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_steamvr_depots.sh"), str(run_dir)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        self.assertTrue(bootstrap_log.exists())
        self.assertTrue((log_dir / "node-args.log").exists())


if __name__ == "__main__":
    unittest.main()
