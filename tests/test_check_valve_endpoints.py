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


class CheckValveEndpointsTests(unittest.TestCase):
    def test_fetches_hardware_app_and_reservation_package_details(self):
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
              *appdetails*appids=4165870*)
                printf '%s\\n' '{"4165870":{"success":true,"data":{"name":"Steam Controller","release_date":{"date":"May 4, 2026"},"packages":[1558609],"price_overview":{"final_formatted":"$99.00"},"package_groups":[{"name":"default","subs":[{"packageid":1558609}]}]}}}'
                ;;
              *appdetails*appids=4165890*)
                printf '%s\\n' '{"4165890":{"success":true,"data":{"name":"Steam Frame","release_date":{"coming_soon":true,"date":"Coming soon"},"package_groups":[]}}}'
                ;;
              *appdetails*appids=4165910*)
                printf '%s\\n' '{"4165910":{"success":true,"data":{"name":"Steam Machine","release_date":{"coming_soon":true,"date":"Coming soon"},"package_groups":[]}}}'
                ;;
              *packagedetails*packageids=1558609*)
                printf '%s\\n' '{"1558609":{"success":true,"data":{"name":"Steam Controller","apps":[{"id":4165870,"name":"Steam Controller"}],"price":{"final_formatted":"$99.00"}}}}'
                ;;
              *packagedetails*packageids=*)
                package="${url##*=}"
                printf '{"%s":{"success":false}}\\n' "$package"
                ;;
              *)
                printf '%s\\n' '<html><body>Steam Frame Steam Machine Steam Controller coming soon</body></html>'
                ;;
            esac
            """,
        )

        write_executable(
            fake_bin / "rg",
            """
            #!/bin/sh
            exit 1
            """,
        )

        env = os.environ.copy()
        env.update({"PATH": f"{fake_bin}:{env['PATH']}"})

        result = subprocess.run(
            [str(ROOT / "scripts" / "check_valve_endpoints.sh"), str(run_dir)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode)

        valve_dir = run_dir / "api" / "valve"
        for appid in ("4165870", "4165890", "4165910"):
            self.assertTrue((valve_dir / f"appdetails-{appid}-us.json").exists())
        for packageid in (
            "1558609",
            "1629446",
            "1629447",
            "1629458",
            "1629460",
            "1629484",
            "1629486",
        ):
            self.assertTrue((valve_dir / f"packagedetails-{packageid}-us.json").exists())

        report = (run_dir / "reports" / "valve-reservation-packages.tsv").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "package\tSteam Controller\t1558609\tpublic\tSteam Controller\t$99.00",
            report,
        )
        self.assertIn(
            "package\tSteam Machine\t1629446\tprivate\t\t\tpackagedetails success:false",
            report,
        )
        self.assertIn(
            "package\tSteam Frame\t1629484\tprivate\t\t\tpackagedetails success:false",
            report,
        )
        self.assertIn("app\tSteam Machine\t4165910\tpublic\tSteam Machine\tComing soon", report)
        self.assertIn("app\tSteam Frame\t4165890\tpublic\tSteam Frame\tComing soon", report)

        key_lines = (run_dir / "reports" / "valve-key-lines.txt").read_text(
            encoding="utf-8"
        )
        self.assertIn("Reservation package API snapshot:", key_lines)
        self.assertIn("package\tSteam Frame\t1629486\tprivate", key_lines)


if __name__ == "__main__":
    unittest.main()
