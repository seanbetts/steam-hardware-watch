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


if __name__ == "__main__":
    unittest.main()
