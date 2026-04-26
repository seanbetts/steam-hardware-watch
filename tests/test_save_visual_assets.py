import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "save_visual_assets", ROOT / "scripts" / "save_visual_assets.py"
)
save_visual_assets = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(save_visual_assets)


class FakeHeaders:
    def __init__(self, content_type):
        self._content_type = content_type

    def get_content_type(self):
        return self._content_type


class FakeResponse:
    status = 200

    def __init__(self, content_type, data):
        self.headers = FakeHeaders(content_type)
        self._data = data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._data


class SaveVisualAssetsTests(unittest.TestCase):
    def test_downloads_fetchable_komodo_avif_assets(self):
        with TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "2026-04-26"
            api_dir = run_dir / "api" / "komodo"
            api_dir.mkdir(parents=True)
            asset_url = (
                "https://komodostation.com/wp-content/uploads/2026/04/example.avif"
            )
            (api_dir / "media.json").write_text(
                json.dumps([{"source_url": asset_url, "mime_type": "image/avif"}]),
                encoding="utf-8",
            )
            avif_bytes = b"\x00\x00\x00\x18ftypavif\x00\x00\x00\x00mif1avif"

            with patch.object(
                sys,
                "argv",
                [
                    "save_visual_assets.py",
                    "--run-dir",
                    str(run_dir),
                    "--base-dir",
                    str(Path(tmp)),
                ],
            ), patch(
                "urllib.request.urlopen",
                return_value=FakeResponse("image/avif", avif_bytes),
            ) as urlopen:
                save_visual_assets.main()

            retrieved = run_dir / "reports" / "retrieved-visual-assets.tsv"
            blocked = run_dir / "reports" / "blocked-visual-assets.tsv"
            saved = (
                run_dir
                / "assets"
                / "discovered"
                / "komodostation.com"
                / "wp-content"
                / "uploads"
                / "2026"
                / "04"
                / "example.avif"
            )
            self.assertIn(asset_url, retrieved.read_text(encoding="utf-8"))
            self.assertEqual("", blocked.read_text(encoding="utf-8"))
            self.assertEqual(avif_bytes, saved.read_bytes())
            self.assertEqual(1, urlopen.call_count)


if __name__ == "__main__":
    unittest.main()
