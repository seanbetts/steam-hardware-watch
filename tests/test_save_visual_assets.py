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


PNG_BYTES = b"\x89PNG\r\n\x1a\nfake"
AVIF_BYTES = b"\x00\x00\x00\x18ftypavif\x00\x00\x00\x00mif1avif"
MP4_BYTES = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42"
SVG_BYTES = b"<svg xmlns=\"http://www.w3.org/2000/svg\"></svg>"


def media_item(
    media_id,
    slug,
    mime,
    parent,
    url,
    title,
    width="",
    height="",
    filesize=123,
):
    details = {"filesize": filesize, "sizes": {}}
    if width:
        details["width"] = width
    if height:
        details["height"] = height
    return {
        "id": media_id,
        "slug": slug,
        "mime_type": mime,
        "post": parent,
        "source_url": url,
        "title": {"rendered": title},
        "media_details": details,
    }


class SaveVisualAssetsTests(unittest.TestCase):
    def test_extracts_wordpress_media_metadata(self):
        metadata = save_visual_assets.extract_media_metadata(
            {
                "id": 433313,
                "slug": "3-in-1-2",
                "mime_type": "video/mp4",
                "post": 433326,
                "source_url": "https://komodostation.com/wp-content/uploads/2026/04/3-in-1.mp4",
                "title": {"rendered": "3 in 1"},
                "media_details": {
                    "width": 1920,
                    "height": 850,
                    "filesize": 12242748,
                    "sizes": {},
                },
            },
            "/run/api/komodo/media-parent-section-433326.json",
        )

        self.assertEqual("433313", metadata["media_id"])
        self.assertEqual("433326", metadata["parent_id"])
        self.assertEqual("3 in 1", metadata["title"])
        self.assertEqual("3-in-1-2", metadata["slug"])
        self.assertEqual("video/mp4", metadata["mime"])
        self.assertEqual(1920, metadata["width"])
        self.assertEqual(850, metadata["height"])
        self.assertEqual(12242748, metadata["filesize"])
        self.assertEqual(
            "/run/api/komodo/media-parent-section-433326.json",
            metadata["source_json"],
        )

    def test_nested_wordpress_sizes_inherit_parent_metadata(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "media.json"
            path.write_text(
                json.dumps(
                    [
                        media_item(
                            433477,
                            "spec-image",
                            "image/avif",
                            433484,
                            "https://komodostation.com/wp-content/uploads/2026/04/spec-image.avif",
                            "spec image",
                            2400,
                            1158,
                        )
                    ]
                ),
                encoding="utf-8",
            )
            data = json.loads(path.read_text(encoding="utf-8"))
            data[0]["media_details"]["sizes"] = {
                "large": {
                    "file": "spec-image-1024x494.avif",
                    "width": 1024,
                    "height": 494,
                    "filesize": 456,
                    "mime_type": "image/avif",
                    "source_url": "https://komodostation.com/wp-content/uploads/2026/04/spec-image-1024x494.avif",
                }
            }
            path.write_text(json.dumps(data), encoding="utf-8")

            hits = save_visual_assets.collect_from_json(path)
            variant = next(hit for hit in hits if hit[0].endswith("-1024x494.avif"))

            self.assertEqual("image/avif", variant[1])
            self.assertEqual(str(path), variant[2])
            self.assertEqual("433477", variant[3]["media_id"])
            self.assertEqual("433484", variant[3]["parent_id"])
            self.assertEqual("spec image", variant[3]["title"])
            self.assertEqual(1024, variant[3]["width"])
            self.assertEqual(494, variant[3]["height"])

    def test_classifies_assets_for_media_type_library(self):
        cases = [
            (
                {"mime": "video/mp4", "title": "3 in 1", "width": 1920, "height": 850},
                "https://komodostation.com/wp-content/uploads/2026/04/3-in-1.mp4",
                "videos",
            ),
            (
                {"mime": "image/svg+xml", "title": "controllerLogo", "width": "", "height": ""},
                "https://komodostation.com/wp-content/uploads/2025/11/controllerLogo.svg",
                "logos",
            ),
            (
                {"mime": "image/png", "title": "videoframe_789", "width": 1920, "height": 1080},
                "https://komodostation.com/wp-content/uploads/2026/04/videoframe_789.png",
                "poster-frames",
            ),
            (
                {"mime": "image/png", "title": "videoframe_789", "width": "", "height": ""},
                "https://komodostation.com/wp-content/uploads/2026/04/videoframe_789-150x150.png",
                "thumbnails",
            ),
            (
                {"mime": "image/png", "title": "videoframe_789", "width": "", "height": ""},
                "https://komodostation.com/wp-content/uploads/2026/04/videoframe_789-1024x576.png",
                "variants",
            ),
            (
                {"mime": "image/avif", "title": "spec image", "width": 150, "height": 150},
                "https://komodostation.com/wp-content/uploads/2026/04/d760b59ee00769c931d0fb73f498ab74-150x150.avif",
                "thumbnails",
            ),
            (
                {"mime": "image/avif", "title": "spec image", "width": 2048, "height": 988},
                "https://komodostation.com/wp-content/uploads/2026/04/d760b59ee00769c931d0fb73f498ab74-2048x988.avif",
                "variants",
            ),
            (
                {"mime": "image/avif", "title": "spec image", "width": 2048, "height": 988},
                "https://komodostation.com/wp-content/uploads/2026/04/d760b59ee00769c931d0fb73f498ab74.avif",
                "images",
            ),
        ]

        for metadata, url, expected in cases:
            with self.subTest(url=url):
                self.assertEqual(
                    expected,
                    save_visual_assets.classify_library_category(metadata, url),
                )

    def test_builds_readable_library_filename(self):
        metadata = {
            "media_id": "433313",
            "title": "3 in 1",
            "width": 1920,
            "height": 850,
        }

        self.assertEqual(
            "steam-controller_433313_3-in-1_1920x850.mp4",
            save_visual_assets.build_library_filename(
                metadata,
                "https://komodostation.com/wp-content/uploads/2026/04/3-in-1.mp4",
                "steam-controller",
            ),
        )

    def test_infers_hardware_from_source_section_without_treating_videoframe_as_frame(self):
        self.assertEqual(
            "steam-controller",
            save_visual_assets.infer_hardware(
                {"title": "videoframe_789", "slug": "videoframe_789", "parent_id": ""},
                "https://komodostation.com/wp-content/uploads/2026/04/videoframe_789-1024x576.png",
                {
                    "/Users/sean/steam_hardware_watch/2026-04-26/api/komodo/media-parent-section-433306.json"
                },
            ),
        )

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

    def test_generates_media_type_library_and_manifests(self):
        with TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "2026-04-26"
            api_dir = run_dir / "api" / "komodo"
            api_dir.mkdir(parents=True)
            items = [
                media_item(
                    433313,
                    "3-in-1-2",
                    "video/mp4",
                    433326,
                    "https://komodostation.com/wp-content/uploads/2026/04/3-in-1.mp4",
                    "3 in 1",
                    1920,
                    850,
                ),
                media_item(
                    413728,
                    "controllerlogo",
                    "image/svg+xml",
                    413763,
                    "https://komodostation.com/wp-content/uploads/2025/11/controllerLogo.svg",
                    "controller logo",
                ),
                media_item(
                    433298,
                    "videoframe_789-2",
                    "image/png",
                    433306,
                    "https://komodostation.com/wp-content/uploads/2026/04/videoframe_789.png",
                    "videoframe_789",
                    1920,
                    1080,
                ),
                media_item(
                    433299,
                    "videoframe_789-150x150",
                    "image/png",
                    433306,
                    "https://komodostation.com/wp-content/uploads/2026/04/videoframe_789-150x150.png",
                    "videoframe_789",
                    150,
                    150,
                ),
                media_item(
                    433477,
                    "spec-image",
                    "image/avif",
                    433484,
                    "https://komodostation.com/wp-content/uploads/2026/04/spec-image-2048x988.avif",
                    "spec image",
                    2048,
                    988,
                ),
            ]
            (api_dir / "media-parent-section-433326.json").write_text(
                json.dumps(items),
                encoding="utf-8",
            )

            def fake_urlopen(request, timeout=15):
                url = request.full_url
                if url.endswith(".mp4"):
                    return FakeResponse("video/mp4", MP4_BYTES)
                if url.endswith(".svg"):
                    return FakeResponse("image/svg+xml", SVG_BYTES)
                if url.endswith(".avif"):
                    return FakeResponse("image/avif", AVIF_BYTES)
                return FakeResponse("image/png", PNG_BYTES)

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
            ), patch("urllib.request.urlopen", side_effect=fake_urlopen):
                save_visual_assets.main()

            expected_paths = [
                run_dir / "assets/library/videos/steam-controller_433313_3-in-1_1920x850.mp4",
                run_dir / "assets/library/logos/steam-controller_413728_controller-logo.svg",
                run_dir / "assets/library/poster-frames/steam-controller_433298_videoframe-789_1920x1080.png",
                run_dir / "assets/library/thumbnails/steam-controller_433299_videoframe-789_150x150.png",
                run_dir / "assets/library/variants/steam-controller_433477_spec-image_2048x988.avif",
            ]
            for path in expected_paths:
                with self.subTest(path=path):
                    self.assertTrue(path.exists(), path)

            manifest_json = run_dir / "assets/manifests/asset-library.json"
            manifest_tsv = run_dir / "assets/manifests/asset-library.tsv"
            self.assertTrue(manifest_json.exists())
            self.assertTrue(manifest_tsv.exists())
            rows = json.loads(manifest_json.read_text(encoding="utf-8"))
            self.assertEqual(5, len(rows))
            video_row = next(row for row in rows if row["category"] == "videos")
            self.assertEqual("steam-controller", video_row["hardware"])
            self.assertEqual("433313", video_row["media_id"])
            self.assertEqual("433326", video_row["parent_id"])
            self.assertEqual("1920", str(video_row["width"]))
            self.assertEqual("850", str(video_row["height"]))
            self.assertEqual(
                "https://komodostation.com/wp-content/uploads/2026/04/3-in-1.mp4",
                video_row["original_url"],
            )
            self.assertIn("assets/discovered/", video_row["raw_path"])
            self.assertIn("assets/library/videos/", video_row["library_path"])
            self.assertIn("media-parent-section-433326.json", video_row["source_json"])
            self.assertIn("original_url\t", manifest_tsv.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
