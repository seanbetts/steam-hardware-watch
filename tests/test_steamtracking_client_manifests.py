import csv
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


def manifest(version, hardware_file="bins_hardware_linuxarm64.zip.old", steam_file="steam_linuxarm64.zip.old"):
    return textwrap.dedent(
        f"""
        "linuxarm64"
        {{
            "version"       "{version}"
            "bins_hardware_linuxarm64"
            {{
                "file"      "{hardware_file}"
                "size"      "7590487"
                "sha2"      "hardware-sha"
            }}
            "steam_linuxarm64"
            {{
                "file"      "{steam_file}"
                "size"      "4345869"
                "sha2"      "steam-sha"
            }}
            "runtime_steamrt_linuxarm64"
            {{
                "file"      "runtime_steamrt_linuxarm64.zip.same"
                "size"      "123973554"
                "sha2"      "runtime-sha"
            }}
        }}
        """
    ).lstrip()


def read_rows(path):
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines(), delimiter="\t"))


class SteamTrackingClientManifestTests(unittest.TestCase):
    def test_manifest_report_flags_linuxarm64_beta_version_and_block_changes(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tracking = tmp_path / "tracking"
            manifests = tracking / "ClientManifest"
            manifests.mkdir(parents=True)
            (manifests / "steam_client_beta_linuxarm64").write_text(
                manifest(
                    "1779139477",
                    hardware_file="bins_hardware_linuxarm64.zip.new",
                    steam_file="steam_linuxarm64.zip.new",
                ),
                encoding="utf-8",
            )
            run_dir = tmp_path / "runs" / "2026-05-23"
            previous_reports = tmp_path / "runs" / "2026-05-22" / "reports"
            previous_reports.mkdir(parents=True)
            previous_reports.joinpath("steamtracking-client-manifests.tsv").write_text(
                "\n".join(
                    [
                        "manifest\tarch\tversion\tblock\tfile\tsize\tsha2\tchanged_since_previous\tprevious_version\tprevious_file\tprevious_size\tprevious_sha2",
                        "steam_client_beta_linuxarm64\tlinuxarm64\t1779000000\t__manifest__\t\t\t\tno\t\t\t\t",
                        "steam_client_beta_linuxarm64\tlinuxarm64\t1779000000\tbins_hardware_linuxarm64\tbins_hardware_linuxarm64.zip.old\t7590487\thardware-sha\tno\t\t\t\t",
                        "steam_client_beta_linuxarm64\tlinuxarm64\t1779000000\tsteam_linuxarm64\tsteam_linuxarm64.zip.old\t4345869\tsteam-sha\tno\t\t\t\t",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "parse_steamtracking_client_manifests.py"),
                    "--run-dir",
                    str(run_dir),
                    "--tracking-dir",
                    str(tracking),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            rows = read_rows(run_dir / "reports" / "steamtracking-client-manifests.tsv")
            manifest_row = next(
                row for row in rows if row["manifest"] == "steam_client_beta_linuxarm64" and row["block"] == "__manifest__"
            )
            hardware_row = next(
                row for row in rows if row["manifest"] == "steam_client_beta_linuxarm64" and row["block"] == "bins_hardware_linuxarm64"
            )
            self.assertEqual("1779139477", manifest_row["version"])
            self.assertEqual("yes", manifest_row["changed_since_previous"])
            self.assertEqual("yes", hardware_row["changed_since_previous"])
            self.assertEqual("bins_hardware_linuxarm64.zip.old", hardware_row["previous_file"])

            key_lines = (run_dir / "reports" / "steamtracking-client-manifests-key-lines.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("steam_client_beta_linuxarm64", key_lines)
            self.assertIn("bins_hardware_linuxarm64", key_lines)
            self.assertIn("changed=yes", key_lines)

    def test_check_steamtracking_writes_client_manifest_report(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tracking = tmp_path / "tracking"
            manifests = tracking / "ClientManifest"
            manifests.mkdir(parents=True)
            (manifests / "steam_client_beta_linuxarm64").write_text(
                manifest("1779139477", hardware_file="bins_hardware_linuxarm64.zip.new"),
                encoding="utf-8",
            )
            (tracking / "ProtobufsWebui").mkdir()
            (tracking / "ProtobufsWebui" / "service_steaminputmanager.proto").write_text(
                "message CSteamInputService_ShouldTritonPairInOobe_Request {}\n",
                encoding="utf-8",
            )
            run_dir = tmp_path / "runs" / "2026-05-23"

            result = subprocess.run(
                [str(ROOT / "scripts" / "check_steamtracking.sh"), str(run_dir), str(tracking)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            self.assertTrue((run_dir / "reports" / "steamtracking-client-manifests.tsv").exists())
            key_lines = (run_dir / "reports" / "steamtracking-client-manifests-key-lines.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("steam_client_beta_linuxarm64", key_lines)

    def test_check_steamtracking_updates_git_checkout_before_scanning(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source"
            tracking = tmp_path / "tracking"
            subprocess.run(["git", "init", str(source)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "-C", str(source), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.name", "Test User"], check=True)
            (source / "ClientManifest").mkdir()
            (source / "ClientManifest" / "steam_client_beta_linuxarm64").write_text(
                manifest("1779139477"),
                encoding="utf-8",
            )
            (source / "ClientExtracted" / "steamui" / "localization").mkdir(parents=True)
            (source / "ClientExtracted" / "steamui" / "localization" / "steamui_english.json").write_text(
                "{}\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "-C", str(source), "add", "."], check=True)
            subprocess.run(["git", "-C", str(source), "commit", "-m", "old"], check=True, stdout=subprocess.PIPE)
            subprocess.run(["git", "clone", str(source), str(tracking)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            (source / "ClientExtracted" / "steamui" / "localization" / "steamui_english.json").write_text(
                '{"GuidedTour_SteamMachine_Welcome_Title": "Welcome to Steam Machine"}\n',
                encoding="utf-8",
            )
            subprocess.run(["git", "-C", str(source), "add", "."], check=True)
            subprocess.run(["git", "-C", str(source), "commit", "-m", "new"], check=True, stdout=subprocess.PIPE)
            latest = subprocess.run(
                ["git", "-C", str(source), "rev-parse", "HEAD"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
            run_dir = tmp_path / "runs" / "2026-05-31"

            result = subprocess.run(
                [str(ROOT / "scripts" / "check_steamtracking.sh"), str(run_dir), str(tracking)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            checked = subprocess.run(
                ["git", "-C", str(tracking), "rev-parse", "HEAD"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
            self.assertEqual(latest, checked)
            key_lines = (run_dir / "reports" / "steamtracking-hardware-signals-key-lines.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("GuidedTour_SteamMachine_Welcome_Title", key_lines)

    def test_hardware_signal_report_catches_steam_machine_guided_tour(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tracking = tmp_path / "tracking"
            localization = tracking / "ClientExtracted" / "steamui" / "localization"
            localization.mkdir(parents=True)
            (localization / "steamui_english.json").write_text(
                textwrap.dedent(
                    """
                    {
                      "GuidedTour_SteamMachine_Welcome_Title": "Welcome to Steam Machine",
                      "GuidedTour_SDCard_Title_SteamMachine": "Last of all, Steam Machine is equipped with a microSD card slot"
                    }
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            run_dir = tmp_path / "runs" / "2026-05-31"

            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "parse_steamtracking_hardware_signals.py"),
                    "--run-dir",
                    str(run_dir),
                    "--tracking-dir",
                    str(tracking),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            key_lines = (run_dir / "reports" / "steamtracking-hardware-signals-key-lines.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("GuidedTour_SteamMachine_Welcome_Title", key_lines)
            self.assertIn("GuidedTour_SDCard_Title_SteamMachine", key_lines)

    def test_hardware_signal_report_writes_prioritized_steam_frame_highlights(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tracking = tmp_path / "tracking"
            localization = tracking / "ClientExtracted" / "steamui" / "localization"
            webui = tracking / "ProtobufsWebui"
            enums = tracking / "Protobufs"
            localization.mkdir(parents=True)
            webui.mkdir(parents=True)
            enums.mkdir(parents=True)
            (tracking / "ClientExtracted" / "ThirdPartyLegalNotices-Chromium.html").parent.mkdir(parents=True, exist_ok=True)
            (tracking / "ClientExtracted" / "ThirdPartyLegalNotices-Chromium.html").write_text(
                "reserves the exclusive right to collect such royalties for any\n",
                encoding="utf-8",
            )
            (localization / "steamui_english.json").write_text(
                textwrap.dedent(
                    """
                    {
                      "controller_steamframe_pair": "Steam Frame Controllers",
                      "Settings_RemotePlay_WifiAPSection": "Wireless Streaming Adapter (Steam Frame)",
                      "LibraryTab_FrameVerified": "Verified on Steam Frame",
                      "SteamFrameWirelessAdapterDialog_Header": "Pair Steam Frame Wireless Adapter",
                      "SteamFrameWirelessAdapterDialog_Description": "Pair to a Steam Frame for high performance streaming."
                    }
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (tracking / "ClientExtracted" / "steamui" / "chunk~frame.js").write_text(
                '(WelcomeToSteamFrame = 1); steamFrameVerifiedApps: f; strName: "SteamFrameWirelessAdapterDialog";\n',
                encoding="utf-8",
            )
            (webui / "common.proto").write_text(
                "optional bool skip_steamframe_pairing_dialog = 27010;\n",
                encoding="utf-8",
            )
            (enums / "enums.proto").write_text(
                "k_EAppTestType_SteamFrameCompatibilityReview = 7;\n",
                encoding="utf-8",
            )
            run_dir = tmp_path / "runs" / "2026-06-05"

            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "parse_steamtracking_hardware_signals.py"),
                    "--run-dir",
                    str(run_dir),
                    "--tracking-dir",
                    str(tracking),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            highlights = (run_dir / "reports" / "steamtracking-frame-signals-key-lines.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("WelcomeToSteamFrame", highlights)
            self.assertIn("steamFrameVerifiedApps", highlights)
            self.assertIn("SteamFrameWirelessAdapterDialog_Header", highlights)
            self.assertIn("controller_steamframe_pair", highlights)
            self.assertIn("Settings_RemotePlay_WifiAPSection", highlights)
            self.assertIn("LibraryTab_FrameVerified", highlights)
            self.assertIn("skip_steamframe_pairing_dialog", highlights)
            self.assertIn("k_EAppTestType_SteamFrameCompatibilityReview", highlights)
            self.assertNotIn("exclusive right", highlights)

    def test_hardware_signal_report_writes_prioritized_steam_machine_highlights(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tracking = tmp_path / "tracking"
            localization = tracking / "ClientExtracted" / "steamui" / "localization"
            siteserver = tracking / "ClientExtracted" / "siteserverui" / "js"
            localization.mkdir(parents=True)
            siteserver.mkdir(parents=True)
            (tracking / "ClientExtracted" / "ThirdPartyLegalNotices-Chromium.html").parent.mkdir(parents=True, exist_ok=True)
            (tracking / "ClientExtracted" / "ThirdPartyLegalNotices-Chromium.html").write_text(
                "reserves the exclusive right to collect such royalties for any\n",
                encoding="utf-8",
            )
            (localization / "steamui_english.json").write_text(
                textwrap.dedent(
                    """
                    {
                      "GuidedTour_SteamMachine_Welcome_Title": "Welcome to Steam Machine",
                      "GuidedTour_SteamMachine_SendOff_Description": "We hope you enjoy using Steam Machine.",
                      "GuidedTour_SDCard_Title_SteamMachine": "Steam Machine is equipped with a microSD card slot."
                    }
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (siteserver / "1136.json").write_text(
                textwrap.dedent(
                    """
                    {
                      "SteamMachine_TestResult_DeviceCompatibilityWarningsShown": "This game displays compatibility warnings when running on Steam Machine, but runs fine",
                      "SteamMachineVerified_DescriptionHeader_Verified": "This game is fully functional on Steam Machine.",
                      "SteamMachineCompatibility_Store_CompatSectionHeader_GamepadUI": "Steam Machine Compatibility"
                    }
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            run_dir = tmp_path / "runs" / "2026-06-05"

            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "parse_steamtracking_hardware_signals.py"),
                    "--run-dir",
                    str(run_dir),
                    "--tracking-dir",
                    str(tracking),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            highlights = (run_dir / "reports" / "steamtracking-machine-signals-key-lines.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("GuidedTour_SteamMachine_Welcome_Title", highlights)
            self.assertIn("GuidedTour_SteamMachine_SendOff_Description", highlights)
            self.assertIn("GuidedTour_SDCard_Title_SteamMachine", highlights)
            self.assertIn("SteamMachine_TestResult_DeviceCompatibilityWarningsShown", highlights)
            self.assertIn("SteamMachineVerified_DescriptionHeader_Verified", highlights)
            self.assertIn("SteamMachineCompatibility_Store_CompatSectionHeader_GamepadUI", highlights)
            self.assertNotIn("exclusive right", highlights)

    def test_compare_runs_includes_client_manifest_key_line_deltas(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            previous = tmp_path / "2026-05-22"
            current = tmp_path / "2026-05-23"
            (previous / "reports").mkdir(parents=True)
            (current / "reports").mkdir(parents=True)
            (previous / "reports" / "steamtracking-client-manifests-key-lines.txt").write_text(
                "steam_client_beta_linuxarm64 version=1779000000 arch=linuxarm64 changed=no previous=\n",
                encoding="utf-8",
            )
            (current / "reports" / "steamtracking-client-manifests-key-lines.txt").write_text(
                "steam_client_beta_linuxarm64 version=1779139477 arch=linuxarm64 changed=yes previous=1779000000\n",
                encoding="utf-8",
            )
            output = tmp_path / "compare.md"

            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "compare_runs.py"),
                    "--previous",
                    str(previous),
                    "--current",
                    str(current),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            compare = output.read_text(encoding="utf-8")
            self.assertIn("Steam client manifests added line", compare)
            self.assertIn("1779139477", compare)

    def test_compare_runs_includes_hardware_signal_key_line_deltas(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            previous = tmp_path / "2026-05-30"
            current = tmp_path / "2026-05-31"
            (previous / "reports").mkdir(parents=True)
            (current / "reports").mkdir(parents=True)
            (previous / "reports" / "steamtracking-hardware-signals-key-lines.txt").write_text("", encoding="utf-8")
            (current / "reports" / "steamtracking-hardware-signals-key-lines.txt").write_text(
                "ClientExtracted/steamui/localization/steamui_english.json:GuidedTour_SteamMachine_Welcome_Title=Welcome to Steam Machine\n",
                encoding="utf-8",
            )
            output = tmp_path / "compare.md"

            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "compare_runs.py"),
                    "--previous",
                    str(previous),
                    "--current",
                    str(current),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            compare = output.read_text(encoding="utf-8")
            self.assertIn("SteamTracking hardware signals added line", compare)
            self.assertIn("GuidedTour_SteamMachine_Welcome_Title", compare)

    def test_status_draft_and_run_summary_include_hardware_signals(self):
        with TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "2026-05-31"
            reports = run_dir / "reports"
            reports.mkdir(parents=True)
            (reports / "steamtracking-hardware-signals-key-lines.txt").write_text(
                "setup-tour\tClientExtracted/steamui/localization/steamui_english.json:8417\t"
                '"GuidedTour_SteamMachine_Welcome_Title": "Welcome to Steam Machine",\n',
                encoding="utf-8",
            )

            summary = subprocess.run(
                ["python3", str(ROOT / "scripts" / "write_run_summary.py"), "--run-dir", str(run_dir)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            draft = subprocess.run(
                ["python3", str(ROOT / "scripts" / "draft_status_update.py"), "--run-dir", str(run_dir)],
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
            self.assertIn(
                "GuidedTour_SteamMachine_Welcome_Title",
                (reports / "run-summary.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "GuidedTour_SteamMachine_Welcome_Title",
                (reports / "status-draft.md").read_text(encoding="utf-8"),
            )

    def test_status_draft_and_run_summary_prefer_steam_frame_highlights(self):
        with TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "2026-06-05"
            reports = run_dir / "reports"
            reports.mkdir(parents=True)
            (reports / "steamtracking-hardware-signals-key-lines.txt").write_text(
                "commerce\tClientExtracted/ThirdPartyLegalNotices-Chromium.html:136305\t"
                "reserves the exclusive right to collect such royalties for any\n",
                encoding="utf-8",
            )
            (reports / "steamtracking-frame-signals-key-lines.txt").write_text(
                "frame-setup\tClientExtracted/steamui/chunk~frame.js:1\tWelcomeToSteamFrame\n"
                "frame-controller\tClientExtracted/steamui/localization/steamui_english.json:2\t"
                '"controller_steamframe_pair": "Steam Frame Controllers",\n',
                encoding="utf-8",
            )

            summary = subprocess.run(
                ["python3", str(ROOT / "scripts" / "write_run_summary.py"), "--run-dir", str(run_dir)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            draft = subprocess.run(
                ["python3", str(ROOT / "scripts" / "draft_status_update.py"), "--run-dir", str(run_dir)],
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
            status_draft = (reports / "status-draft.md").read_text(encoding="utf-8")
            self.assertIn("WelcomeToSteamFrame", run_summary)
            self.assertIn("controller_steamframe_pair", run_summary)
            self.assertIn("WelcomeToSteamFrame", status_draft)
            self.assertIn("controller_steamframe_pair", status_draft)

    def test_status_draft_and_run_summary_prefer_steam_machine_highlights(self):
        with TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "2026-06-05"
            reports = run_dir / "reports"
            reports.mkdir(parents=True)
            (reports / "steamtracking-hardware-signals-key-lines.txt").write_text(
                "commerce\tClientExtracted/ThirdPartyLegalNotices-Chromium.html:136305\t"
                "reserves the exclusive right to collect such royalties for any\n",
                encoding="utf-8",
            )
            (reports / "steamtracking-machine-signals-key-lines.txt").write_text(
                "machine-setup\tClientExtracted/steamui/localization/steamui_english.json:1\t"
                '"GuidedTour_SteamMachine_Welcome_Title": "Welcome to Steam Machine",\n'
                "machine-compatibility\tClientExtracted/siteserverui/js/1136.json:1\t"
                '"SteamMachineCompatibility_Store_CompatSectionHeader_GamepadUI": "Steam Machine Compatibility",\n',
                encoding="utf-8",
            )

            summary = subprocess.run(
                ["python3", str(ROOT / "scripts" / "write_run_summary.py"), "--run-dir", str(run_dir)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            draft = subprocess.run(
                ["python3", str(ROOT / "scripts" / "draft_status_update.py"), "--run-dir", str(run_dir)],
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
            status_draft = (reports / "status-draft.md").read_text(encoding="utf-8")
            self.assertIn("GuidedTour_SteamMachine_Welcome_Title", run_summary)
            self.assertIn("SteamMachineCompatibility_Store_CompatSectionHeader_GamepadUI", run_summary)
            self.assertIn("GuidedTour_SteamMachine_Welcome_Title", status_draft)
            self.assertIn("SteamMachineCompatibility_Store_CompatSectionHeader_GamepadUI", status_draft)


if __name__ == "__main__":
    unittest.main()
