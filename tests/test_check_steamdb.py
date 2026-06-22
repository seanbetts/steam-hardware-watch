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


class CheckSteamDBTests(unittest.TestCase):
    def run_check(self, curl_mode, node_mode="success"):
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
            printf '%s\\n' "$*" >> "$FAKE_LOG_DIR/curl-args.log"
            case "$FAKE_CURL_MODE" in
              success)
                printf '%s\\n' '<html><title>Steam Controller AppID: 4165870</title><body>Coming soon prerelease</body></html>'
                ;;
              challenge)
                printf '%s\\n' '<html><title>Just a moment...</title><body><h1>Checking your browser...</h1> Cloudflare</body></html>'
                ;;
              fail)
                exit 22
                ;;
              *)
                echo "unknown FAKE_CURL_MODE: $FAKE_CURL_MODE" >&2
                exit 2
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
            case "$FAKE_NODE_MODE" in
              success)
                printf '%s\\n' '<html><title>Steam Controller AppID: 4165870</title><body>Coming soon prerelease</body></html>' > "$output"
                ;;
              challenge)
                printf '%s\\n' '<html><title>Just a moment...</title><body>Checking your browser... Cloudflare</body></html>' > "$output"
                ;;
              fail)
                exit 1
                ;;
              *)
                echo "unknown FAKE_NODE_MODE: $FAKE_NODE_MODE" >&2
                exit 2
                ;;
            esac
            """,
        )

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fake_bin}:{env['PATH']}",
                "FAKE_CURL_MODE": curl_mode,
                "FAKE_NODE_MODE": node_mode,
                "FAKE_LOG_DIR": str(log_dir),
                "STEAMDB_PLAYWRIGHT_FALLBACK": "1",
                "STEAMDB_AUTO_BOOTSTRAP": "0",
            }
        )

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_steamdb.sh"), str(run_dir)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return result, run_dir, log_dir

    def test_uses_realistic_chrome_user_agent_by_default(self):
        result, run_dir, log_dir = self.run_check("success")

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        curl_args = (log_dir / "curl-args.log").read_text(encoding="utf-8")
        self.assertIn("Chrome/123.0.0.0", curl_args)
        self.assertNotIn("-A Mozilla/5.0 --retry", curl_args)
        self.assertTrue((run_dir / "api" / "steamdb" / "controller-app.html").exists())

    def test_treats_cloudflare_challenge_html_as_blocked(self):
        result, run_dir, _ = self.run_check("challenge", node_mode="fail")

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        self.assertFalse((run_dir / "api" / "steamdb" / "controller-app.html").exists())
        errors = (run_dir / "reports" / "steamdb-errors.txt").read_text(encoding="utf-8")
        self.assertIn("blocked or challenge page", errors)

    def test_uses_playwright_fallback_after_challenge_page(self):
        result, run_dir, log_dir = self.run_check("challenge", node_mode="success")

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        self.assertTrue((log_dir / "node-args.log").exists())
        html = (run_dir / "api" / "steamdb" / "controller-app.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("Steam Controller", html)
        self.assertIn("Coming soon", html)
        errors = (run_dir / "reports" / "steamdb-errors.txt").read_text(encoding="utf-8")
        self.assertEqual("", errors)

    def test_playwright_fallback_bootstraps_dedicated_browser_when_cdp_is_stale(self):
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
              *)
                printf '%s\\n' '<html><title>Just a moment...</title><body>Checking your browser... Cloudflare</body></html>'
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
            printf '%s\\n' '<html><title>Steam Controller AppID: 4165870</title><body>Coming soon prerelease</body></html>' > "$output"
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
            [str(ROOT / "scripts" / "check_steamdb.sh"), str(run_dir)],
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
        self.assertIn("bootstrap", bootstrap_log.read_text(encoding="utf-8"))

    def test_records_reservation_package_update_baseline(self):
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
              *sub/1629446*)
                printf '%s\\n' '<html><body><h1>Steam Sub 1629446</h1><table><tr><td>Last Record Update</td><td>27 April 2026 &#8211; 18:22:46 UTC</td></tr><tr><td>Last Changenumber</td><td>35499151</td></tr></table><p>We have no information about this package besides the fact that it exists.</p><h2>Possible apps in this package</h2><table><tr><td>4165910</td><td>Game</td><td>Steam Machine</td><td>35499151</td></tr></table></body></html>'
                ;;
              *sub/1629484*)
                printf '%s\\n' '<html><body><h1>Steam Sub 1629484</h1><table><tr><td>Last Record Update</td><td>27 April 2026 &#8211; 18:21:50 UTC</td></tr><tr><td>Last Changenumber</td><td>35499157</td></tr></table><p>We have no information about this package besides the fact that it exists.</p><h2>Possible apps in this package</h2><table><tr><td>4165890</td><td>Game</td><td>Steam Frame</td><td>35499151</td></tr></table></body></html>'
                ;;
              *sub/*)
                package="${url%/}"
                package="${package##*/}"
                printf '<html><body><h1>Steam Sub %s</h1><table><tr><td>Last Record Update</td><td>27 April 2026 &#8211; 18:20:00 UTC</td></tr><tr><td>Last Changenumber</td><td>35499000</td></tr></table><p>We have no information about this package besides the fact that it exists.</p></body></html>\\n' "$package"
                ;;
              *)
                printf '%s\\n' '<html><title>Steam Controller AppID: 4165870</title><body>Coming soon prerelease</body></html>'
                ;;
            esac
            """,
        )

        env = os.environ.copy()
        env.update({"PATH": f"{fake_bin}:{env['PATH']}"})

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_steamdb.sh"), str(run_dir)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)

        steamdb_dir = run_dir / "api" / "steamdb"
        self.assertTrue((steamdb_dir / "package-1629446.html").exists())
        self.assertTrue((steamdb_dir / "package-1629484.html").exists())

        report = (run_dir / "reports" / "steamdb-reservation-packages.tsv").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Steam Machine\t1629446\t27 April 2026 - 18:22:46 UTC\t35499151\t4165910:Steam Machine\tprivate_exists_only",
            report,
        )
        self.assertIn(
            "Steam Frame\t1629484\t27 April 2026 - 18:21:50 UTC\t35499157\t4165890:Steam Frame\tprivate_exists_only",
            report,
        )

        key_lines = (run_dir / "reports" / "steamdb-key-lines.txt").read_text(
            encoding="utf-8"
        )
        self.assertTrue(key_lines.startswith("Reservation package SteamDB snapshot:"))
        self.assertIn("Steam Machine\t1629446", key_lines)
