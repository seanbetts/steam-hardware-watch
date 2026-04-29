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
