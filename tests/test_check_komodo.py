import os
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


def write_executable(path, content):
    path.write_text(content.strip() + "\n", encoding="utf-8")
    path.chmod(0o755)


class CheckKomodoTests(unittest.TestCase):
    def test_optional_machine_and_frame_fetch_failures_do_not_abort(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_path = Path(tmp.name)
        run_dir = tmp_path / "run"
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()

        write_executable(
            fake_bin / "curl",
            r"""
            #!/bin/sh
            for arg do
              url="$arg"
            done
            case "$url" in
              *wp-json/wp/v2/product/413763*)
                printf '%s\n' '{"modified":"2026-05-14T12:00:00","title":{"rendered":"Steam Controller"}}'
                ;;
              *wp-json/wp/v2/sections?search=Steam%20Controller*)
                printf '%s\n' '[{"id":433306,"date":"2026-04-01T00:00:00","modified":"2026-05-14T12:00:00","slug":"steam-controller-01-banner","title":{"rendered":"Steam Controller Banner"}}]'
                ;;
              *wp-json/wp/v2/media?search=Steam%20Controller*)
                printf '%s\n' '[]'
                ;;
              *wp-json/wp/v2/media?parent=*)
                printf '%s\n' '[]'
                ;;
              *wp-json/wp/v2/product/413772*|*wp-json/wp/v2/product/413776*|*wp-json/wp/v2/sections?search=Steam%20Machine*|*wp-json/wp/v2/sections?search=Steam%20Frame*)
                exit 22
                ;;
              *wp-json/*)
                printf '%s\n' '{"name":"Komodo"}'
                ;;
              *)
                exit 22
                ;;
            esac
            """,
        )

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fake_bin}:{env['PATH']}",
                "KOMODO_ENV_FILE": str(tmp_path / "missing-komodo-env.sh"),
            }
        )

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_komodo.sh"), str(run_dir)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        self.assertIn("Saved Komodo API responses", result.stdout)
        self.assertIn(
            "controller\t2026-05-14T12:00:00",
            (run_dir / "reports" / "komodo-product-modified.tsv").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            "",
            (run_dir / "reports" / "komodo-machine-sections.tsv").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            "",
            (run_dir / "reports" / "komodo-frame-sections.tsv").read_text(encoding="utf-8"),
        )

    def test_optional_machine_and_frame_fetches_use_playwright_fallback(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_path = Path(tmp.name)
        run_dir = tmp_path / "run"
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()

        write_executable(
            fake_bin / "curl",
            r"""
            #!/bin/sh
            for arg do
              url="$arg"
            done
            case "$url" in
              *wp-json/wp/v2/product/413763*)
                printf '%s\n' '{"modified":"2026-05-14T12:00:00","title":{"rendered":"Steam Controller"}}'
                ;;
              *wp-json/wp/v2/sections?search=Steam%20Controller*|*wp-json/wp/v2/media?search=Steam%20Controller*|*wp-json/wp/v2/media?parent=*)
                printf '%s\n' '[]'
                ;;
              *wp-json/wp/v2/product/413772*|*wp-json/wp/v2/product/413776*|*wp-json/wp/v2/sections?search=Steam%20Machine*|*wp-json/wp/v2/sections?search=Steam%20Frame*)
                exit 22
                ;;
              *wp-json/*)
                printf '%s\n' '{"name":"Komodo"}'
                ;;
              *)
                exit 22
                ;;
            esac
            """,
        )
        write_executable(
            fake_bin / "playwright-cli",
            "#!/bin/sh\nexit 0",
        )
        write_executable(
            fake_bin / "node",
            r"""
            #!/bin/sh
            url="$2"
            output="$3"
            case "$url" in
              *wp-json/wp/v2/product/413772*)
                printf '%s\n' '{"modified":"2026-04-24T14:32:54","title":{"rendered":"Steam Machine"}}' > "$output"
                ;;
              *wp-json/wp/v2/product/413776*)
                printf '%s\n' '{"modified":"2026-04-24T14:33:36","title":{"rendered":"Steam Frame"}}' > "$output"
                ;;
              *wp-json/wp/v2/sections?search=Steam%20Machine*)
                printf '%s\n' '[{"id":413808,"date":"2025-11-12T14:04:51","modified":"2026-03-03T16:01:51","slug":"en-steam-machine-wishlist","title":{"rendered":"JA &#8211; Steam Machine Wishlist"}}]' > "$output"
                ;;
              *wp-json/wp/v2/sections?search=Steam%20Frame*)
                printf '%s\n' '[{"id":413804,"date":"2025-11-12T14:06:55","modified":"2025-11-12T14:09:51","slug":"413801","title":{"rendered":"JA &#8211; Steam Frame Wishlist"}}]' > "$output"
                ;;
              *)
                exit 22
                ;;
            esac
            """,
        )

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fake_bin}:{env['PATH']}",
                "KOMODO_ENV_FILE": str(tmp_path / "missing-komodo-env.sh"),
                "KOMODO_PLAYWRIGHT_FALLBACK": "1",
                "KOMODO_AUTO_BOOTSTRAP": "0",
            }
        )

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_komodo.sh"), str(run_dir)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        product_modified = (run_dir / "reports" / "komodo-product-modified.tsv").read_text(
            encoding="utf-8"
        )
        self.assertIn("machine\t2026-04-24T14:32:54", product_modified)
        self.assertIn("frame\t2026-04-24T14:33:36", product_modified)
        self.assertIn(
            "en-steam-machine-wishlist",
            (run_dir / "reports" / "komodo-machine-sections.tsv").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "Steam Frame Wishlist",
            (run_dir / "reports" / "komodo-frame-sections.tsv").read_text(encoding="utf-8"),
        )

    def test_playwright_fallback_bootstraps_dedicated_browser_when_cdp_is_stale(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        tmp_path = Path(tmp.name)
        run_dir = tmp_path / "run"
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()
        env_file = tmp_path / "komodo-env.sh"
        bootstrap_log = tmp_path / "bootstrap.log"

        env_file.write_text(
            "\n".join(
                [
                    "export KOMODO_PLAYWRIGHT_FALLBACK=1",
                    f'export PLAYWRIGHT_PROFILE_DIR="{tmp_path / "profile"}"',
                    'export PLAYWRIGHT_CDP_ENDPOINT="http://127.0.0.1:9"',
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        write_executable(
            fake_bin / "curl",
            r"""
            #!/bin/sh
            for arg do
              url="$arg"
            done
            case "$url" in
              http://127.0.0.1:9/json/version)
                exit 7
                ;;
              *wp-json/wp/v2/product/413763*)
                printf '%s\n' '{"modified":"2026-05-14T12:00:00","title":{"rendered":"Steam Controller"}}'
                ;;
              *wp-json/wp/v2/sections?search=Steam%20Controller*|*wp-json/wp/v2/media?search=Steam%20Controller*|*wp-json/wp/v2/media?parent=*)
                printf '%s\n' '[]'
                ;;
              *wp-json/wp/v2/product/413772*|*wp-json/wp/v2/product/413776*|*wp-json/wp/v2/sections?search=Steam%20Machine*|*wp-json/wp/v2/sections?search=Steam%20Frame*)
                exit 22
                ;;
              *wp-json/*)
                printf '%s\n' '{"name":"Komodo"}'
                ;;
              *)
                exit 22
                ;;
            esac
            """,
        )
        write_executable(fake_bin / "playwright-cli", "#!/bin/sh\nexit 0")
        write_executable(
            fake_bin / "node",
            r"""
            #!/bin/sh
            url="$2"
            output="$3"
            case "$url" in
              *wp-json/wp/v2/product/413772*)
                printf '%s\n' '{"modified":"2026-05-14T12:00:00","title":{"rendered":"Steam Machine"}}' > "$output"
                ;;
              *wp-json/wp/v2/product/413776*)
                printf '%s\n' '{"modified":"2026-05-14T12:00:00","title":{"rendered":"Steam Frame"}}' > "$output"
                ;;
              *)
                printf '%s\n' '[]' > "$output"
                ;;
            esac
            """,
        )
        write_executable(
            tmp_path / "bootstrap-komodo.sh",
            f"#!/bin/sh\nprintf '%s\\n' bootstrap >> '{bootstrap_log}'\ncat > '{env_file}' <<'EOF'\nexport KOMODO_PLAYWRIGHT_FALLBACK=1\nexport PLAYWRIGHT_PROFILE_DIR=\"{tmp_path / 'profile'}\"\nexport PLAYWRIGHT_CDP_ENDPOINT=\"http://127.0.0.1:55684\"\nEOF\n",
        )

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fake_bin}:{env['PATH']}",
                "KOMODO_ENV_FILE": str(env_file),
                "KOMODO_BOOTSTRAP_CMD": str(tmp_path / "bootstrap-komodo.sh"),
            }
        )

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_komodo.sh"), str(run_dir)],
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


if __name__ == "__main__":
    unittest.main()
