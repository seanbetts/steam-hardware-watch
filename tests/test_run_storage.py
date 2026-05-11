import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RunStorageTests(unittest.TestCase):
    def test_init_run_defaults_to_gitignored_repo_runs_directory(self):
        run_date = "2099-01-02"
        run_dir = ROOT / "runs" / run_date
        run_note = ROOT / "status" / "runs" / f"{run_date}.md"
        self.addCleanup(lambda: shutil.rmtree(run_dir, ignore_errors=True))
        self.addCleanup(lambda: run_note.unlink(missing_ok=True))

        result = subprocess.run(
            [str(ROOT / "scripts" / "init_run.sh"), run_date],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)
        self.assertIn(f"RUN_DIR={run_dir}", result.stdout)
        self.assertTrue((run_dir / "api").is_dir())
        self.assertTrue((run_dir / "reports").is_dir())


if __name__ == "__main__":
    unittest.main()
