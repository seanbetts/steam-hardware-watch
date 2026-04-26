# Asset Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a media-type-first asset library under each run folder so humans can browse videos, images, logos, poster frames, thumbnails, and variants without navigating source-mirrored URLs.

**Architecture:** Extend `scripts/save_visual_assets.py` after the existing raw download path. The raw `assets/discovered/` archive remains the canonical downloaded copy, and a new library layer copies retrieved files into `assets/library/` with readable filenames plus JSON/TSV manifests under `assets/manifests/`.

**Tech Stack:** Python standard library, `unittest`, existing shell/Python watch scripts.

---

### Task 1: Metadata Extraction Helpers

**Files:**
- Modify: `scripts/save_visual_assets.py`
- Test: `tests/test_save_visual_assets.py`

- [ ] **Step 1: Write failing tests**

Add tests that build a fake run with WordPress media JSON containing:

```python
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
}
```

Expected helper output:

```python
{
    "media_id": "433313",
    "parent_id": "433326",
    "title": "3 in 1",
    "width": 1920,
    "height": 850,
    "filesize": 12242748,
}
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
python3 -m unittest tests/test_save_visual_assets.py
```

Expected: failure because metadata helper functions do not exist.

- [ ] **Step 3: Implement metadata helpers**

Add small helpers in `scripts/save_visual_assets.py`:

```python
def extract_media_metadata(obj: dict, source_path: str) -> dict:
    details = obj.get("media_details") if isinstance(obj.get("media_details"), dict) else {}
    title = obj.get("title") if isinstance(obj.get("title"), dict) else {}
    return {
        "media_id": str(obj.get("id") or ""),
        "parent_id": str(obj.get("post") or ""),
        "title": title.get("rendered") or obj.get("slug") or "",
        "slug": obj.get("slug") or "",
        "mime": obj.get("mime_type") or "",
        "width": details.get("width") or "",
        "height": details.get("height") or "",
        "filesize": details.get("filesize") or "",
        "source_json": source_path,
    }
```

Update collection to store metadata alongside URL and MIME.

- [ ] **Step 4: Run tests and confirm pass**

Run:

```bash
python3 -m unittest tests/test_save_visual_assets.py
```

Expected: all tests pass.

### Task 2: Library Classification And Filenames

**Files:**
- Modify: `scripts/save_visual_assets.py`
- Test: `tests/test_save_visual_assets.py`

- [ ] **Step 1: Write failing tests**

Add tests for these classification outcomes:

```python
("video/mp4", "3-in-1.mp4", "3 in 1", 1920, 850) -> "videos"
("image/svg+xml", "controllerLogo.svg", "controllerLogo", "", "") -> "logos"
("image/png", "videoframe_789.png", "videoframe_789", 1920, 1080) -> "poster-frames"
("image/avif", "d760...-150x150.avif", "spec image", 150, 150) -> "thumbnails"
("image/avif", "d760...-2048x988.avif", "spec image", 2048, 988) -> "variants"
("image/avif", "d760....avif", "spec image", 2048, 988) -> "images"
```

Add a filename test:

```python
build_library_filename(metadata, url, "steam-controller") == "steam-controller_433313_3-in-1_1920x850.mp4"
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
python3 -m unittest tests/test_save_visual_assets.py
```

Expected: failure because classification and filename helpers do not exist.

- [ ] **Step 3: Implement helpers**

Add helpers:

- `slugify(value: str) -> str`
- `has_size_suffix(url: str) -> bool`
- `is_thumbnail_size(width, height, url) -> bool`
- `infer_hardware(metadata, url, sources) -> str`
- `classify_library_category(metadata, url) -> str`
- `build_library_filename(metadata, url, hardware) -> str`

Use `steam-controller`, `steam-machine`, `steam-frame`, and `unknown` hardware slugs.

- [ ] **Step 4: Run tests and confirm pass**

Run:

```bash
python3 -m unittest tests/test_save_visual_assets.py
```

Expected: all tests pass.

### Task 3: Generate Library Files And Manifests

**Files:**
- Modify: `scripts/save_visual_assets.py`
- Test: `tests/test_save_visual_assets.py`

- [ ] **Step 1: Write failing integration test**

Create a test fake run containing a video, logo, poster frame, thumbnail, and variant. Mock downloads with valid bytes. Run `save_visual_assets.main()` and assert:

```text
assets/library/videos/steam-controller_433313_3-in-1_1920x850.mp4
assets/library/logos/steam-controller_413728-controller-logo.svg
assets/library/poster-frames/steam-controller_433298_videoframe-789_1920x1080.png
assets/library/thumbnails/steam-controller_433298_videoframe-789_150x150.png
assets/library/variants/steam-controller_433477_spec-image_2048x988.avif
assets/manifests/asset-library.json
assets/manifests/asset-library.tsv
```

Assert manifest rows include original URL, raw path, library path, category, hardware, media ID, parent ID, dimensions, MIME, detected format, and source JSON.

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
python3 -m unittest tests/test_save_visual_assets.py
```

Expected: failure because library generation does not exist.

- [ ] **Step 3: Implement library generation**

After a download is retrieved or found cached:

1. Build metadata.
2. Choose category.
3. Build a readable filename.
4. Copy the raw downloaded file into `assets/library/<category>/`.
5. Resolve filename collisions by appending `-2`, `-3`, etc.
6. Write JSON and TSV manifests under `assets/manifests/`.

- [ ] **Step 4: Run tests and confirm pass**

Run:

```bash
python3 -m unittest tests/test_save_visual_assets.py
```

Expected: all tests pass.

### Task 4: Regenerate Current Run And Verify

**Files:**
- Runtime artifacts: `/Users/sean/steam_hardware_watch/2026-04-26/assets/library`
- Runtime artifacts: `/Users/sean/steam_hardware_watch/2026-04-26/assets/manifests`

- [ ] **Step 1: Regenerate assets**

Run:

```bash
python3 scripts/save_visual_assets.py --run-dir /Users/sean/steam_hardware_watch/2026-04-26 --base-dir /Users/sean/steam_hardware_watch
```

- [ ] **Step 2: Verify media-type folders**

Run:

```bash
find /Users/sean/steam_hardware_watch/2026-04-26/assets/library -maxdepth 2 -type f | sed 's#.*/assets/library/##' | sort | head -n 80
```

Expected: files appear under `videos/`, `images/`, `logos/`, `poster-frames/`, `thumbnails/`, and `variants/`.

- [ ] **Step 3: Verify manifests**

Run:

```bash
python3 -m json.tool /Users/sean/steam_hardware_watch/2026-04-26/assets/manifests/asset-library.json >/dev/null
test -s /Users/sean/steam_hardware_watch/2026-04-26/assets/manifests/asset-library.tsv
```

Expected: exit 0.

- [ ] **Step 4: Run final tests**

Run:

```bash
python3 -m py_compile scripts/save_visual_assets.py
python3 -m unittest tests/test_save_visual_assets.py
```

Expected: all tests pass.
