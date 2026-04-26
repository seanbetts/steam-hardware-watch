#!/usr/bin/env python3
import argparse
import json
import os
import re
import shutil
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

VISUAL_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".avif",
    ".svg",
    ".gif",
    ".mp4",
    ".webm",
    ".mov",
    ".m4v",
}

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)

CONTROLLER_PARENT_IDS = {
    "413763",
    "413813",
    "433306",
    "433326",
    "433356",
    "433376",
    "433416",
    "433434",
    "433470",
    "433484",
}
MACHINE_PARENT_IDS = {"413772", "413808"}
FRAME_PARENT_IDS = {"413776", "413804"}


def is_visual_url(url: str) -> bool:
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in VISUAL_EXTS)


def walk_json(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for item in value:
            yield from walk_json(item)


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


def collect_from_json(path: Path):
    if path.name in {"media-spec-search.json", "media-manual-search.json", "media-video.json"}:
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    hits = []

    def append_hit(obj: dict, metadata: dict) -> None:
        url = obj.get("source_url")
        mime = obj.get("mime_type", "")
        if isinstance(url, str) and url.startswith("http"):
            if mime.startswith("image/") or mime.startswith("video/") or is_visual_url(url):
                hits.append((url, mime, str(path), metadata))

    def collect(value):
        if isinstance(value, list):
            for item in value:
                collect(item)
            return
        if not isinstance(value, dict):
            return

        url = value.get("source_url")
        mime = value.get("mime_type", "")
        is_media = isinstance(url, str) and url.startswith("http") and (
            mime.startswith("image/") or mime.startswith("video/") or is_visual_url(url)
        )
        if is_media:
            metadata = extract_media_metadata(value, str(path))
            append_hit(value, metadata)
            details = value.get("media_details") if isinstance(value.get("media_details"), dict) else {}
            sizes = details.get("sizes") if isinstance(details.get("sizes"), dict) else {}
            for size in sizes.values():
                if not isinstance(size, dict):
                    continue
                size_metadata = dict(metadata)
                size_metadata["mime"] = size.get("mime_type") or metadata.get("mime", "")
                size_metadata["width"] = size.get("width") or ""
                size_metadata["height"] = size.get("height") or ""
                size_metadata["filesize"] = size.get("filesize") or ""
                append_hit(size, size_metadata)
            return

        for child in value.values():
            collect(child)

    collect(data)
    return hits


def collect_from_seed_reports(base_dir: Path, current_run_dir: Path):
    if not base_dir.exists():
        return []

    hits = []
    patterns = (
        ("discovered-visual-assets.tsv", 0, 2),
        ("retrieved-visual-assets.tsv", 0, 2),
        ("blocked-visual-assets.tsv", None, 4),
        ("downloaded-visual-assets.tsv", 0, 2),
    )

    for report_name, mime_index, url_index in patterns:
        for report in sorted(base_dir.glob(f"????-??-??/reports/{report_name}")):
            run_dir = report.parent.parent
            if run_dir == current_run_dir:
                continue
            for raw_line in report.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) <= url_index:
                    continue
                url = parts[url_index]
                if not isinstance(url, str) or not url.startswith("http") or not is_visual_url(url):
                    continue
                mime = parts[mime_index] if mime_index is not None and len(parts) > mime_index else ""
                hits.append(
                    (
                        url,
                        mime,
                        f"seed:{run_dir.name}:{report_name}",
                        {
                            "media_id": "",
                            "parent_id": "",
                            "title": Path(urlparse(url).path).stem,
                            "slug": Path(urlparse(url).path).stem,
                            "mime": mime,
                            "width": "",
                            "height": "",
                            "filesize": "",
                            "source_json": f"seed:{run_dir.name}:{report_name}",
                        },
                    )
                )
    return hits


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return slug or "asset"


def has_size_suffix(url: str) -> bool:
    stem = Path(urlparse(url).path).stem
    return bool(re.search(r"-\d+x\d+$", stem))


def dimension_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def is_thumbnail_size(width, height, url: str) -> bool:
    w = dimension_int(width)
    h = dimension_int(height)
    path = urlparse(url).path.lower()
    if re.search(r"-(100x100|150x150)(?=\.[^.]+$)", path):
        return True
    return bool(w and h and w <= 200 and h <= 200)


def infer_hardware(metadata: dict, url: str, sources) -> str:
    parent_id = str(metadata.get("parent_id") or "")
    source_ids = set()
    for source in sources or []:
        source_ids.update(re.findall(r"media-parent-(?:section|product)-(\d+)", source))
    all_ids = {parent_id, *source_ids}
    if all_ids & CONTROLLER_PARENT_IDS:
        return "steam-controller"
    if all_ids & MACHINE_PARENT_IDS:
        return "steam-machine"
    if all_ids & FRAME_PARENT_IDS:
        return "steam-frame"

    haystack = " ".join(
        [
            metadata.get("title", ""),
            metadata.get("slug", ""),
            url,
            " ".join(sorted(sources)) if sources else "",
        ]
    ).lower()
    if "steam-machine" in haystack or "steam machine" in haystack:
        return "steam-machine"
    if "steam-frame" in haystack or "steam frame" in haystack:
        return "steam-frame"
    if "steam-controller" in haystack or "steam controller" in haystack or "controller" in haystack:
        return "steam-controller"
    return "unknown"


def classify_library_category(metadata: dict, url: str) -> str:
    mime = (metadata.get("mime") or "").lower()
    title = (metadata.get("title") or metadata.get("slug") or "").lower()
    extension = expected_family(url)
    if mime.startswith("video/") or extension in {"mp4", "webm"}:
        return "videos"
    if extension == "svg" or "logo" in title:
        return "logos"
    if is_thumbnail_size(metadata.get("width"), metadata.get("height"), url):
        return "thumbnails"
    if has_size_suffix(url):
        return "variants"
    if "videoframe" in Path(urlparse(url).path).stem.lower() or "video frame" in title:
        return "poster-frames"
    if mime.startswith("image/") or extension in {"png", "jpeg", "gif", "webp", "avif"}:
        return "images"
    return "unknown"


def build_library_filename(metadata: dict, url: str, hardware: str) -> str:
    media_id = metadata.get("media_id") or "no-id"
    label = slugify(metadata.get("title") or metadata.get("slug") or Path(urlparse(url).path).stem)
    width = dimension_int(metadata.get("width"))
    height = dimension_int(metadata.get("height"))
    dimensions = f"_{width}x{height}" if width and height else ""
    suffix = Path(urlparse(url).path).suffix.lower()
    return f"{hardware}_{media_id}_{label}{dimensions}{suffix}"


def resolve_unique_path(path: Path, used_paths: set[Path]) -> Path:
    candidate = path
    index = 2
    while candidate in used_paths or candidate.exists():
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        index += 1
    used_paths.add(candidate)
    return candidate


def copy_to_library(library_dir: Path, raw_path: Path, metadata: dict, url: str, sources, used_paths: set[Path]) -> tuple[str, Path]:
    hardware = infer_hardware(metadata, url, sources)
    category = classify_library_category(metadata, url)
    filename = build_library_filename(metadata, url, hardware)
    target = resolve_unique_path(library_dir / category / filename, used_paths)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(raw_path, target)
    return category, target


def destination_for(base_dir: Path, url: str) -> Path:
    parsed = urlparse(url)
    rel = (parsed.netloc + parsed.path).lstrip("/")
    return base_dir / rel


def is_protected_komodo_asset(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    if "komodostation.com" not in host:
        return False
    return path.endswith((".mp4", ".webm", ".mov", ".m4v", ".avif"))


def detect_format(data: bytes) -> str:
    head = data[:512]
    lower = head.lower()
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if head.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    if head.startswith(b"RIFF") and b"WEBP" in head[:16]:
        return "webp"
    if head.startswith(b"\x1a\x45\xdf\xa3"):
        return "webm"
    if b"ftyp" in head[:32]:
        if b"avif" in head[:32] or b"avis" in head[:32]:
            return "avif"
        return "mp4"
    if b"<svg" in lower:
        return "svg"
    if lower.startswith(b"<!doctype html") or lower.startswith(b"<html"):
        return "html"
    return "unknown"


def expected_family(url: str) -> str:
    path = urlparse(url).path.lower()
    if path.endswith(".png"):
        return "png"
    if path.endswith((".jpg", ".jpeg")):
        return "jpeg"
    if path.endswith(".gif"):
        return "gif"
    if path.endswith(".webp"):
        return "webp"
    if path.endswith(".avif"):
        return "avif"
    if path.endswith(".svg"):
        return "svg"
    if path.endswith(".webm"):
        return "webm"
    if path.endswith((".mp4", ".mov", ".m4v")):
        return "mp4"
    return "unknown"


def is_valid_download(url: str, content_type: str, data: bytes):
    detected = detect_format(data)
    expected = expected_family(url)
    ctype = (content_type or "").lower()

    if detected == "html":
        return False, detected, expected
    if ctype.startswith("text/html"):
        return False, detected, expected
    if expected != "unknown" and detected != expected:
        return False, detected, expected
    if detected == "unknown":
        return False, detected, expected
    return True, detected, expected


def download(url: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": os.environ.get("KOMODO_USER_AGENT", DEFAULT_USER_AGENT)},
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        data = response.read()
        status = getattr(response, "status", 200)
        content_type = response.headers.get_content_type()
    ok, detected, expected = is_valid_download(url, content_type, data)
    if not ok:
        return {
            "ok": False,
            "status": str(status),
            "content_type": content_type,
            "detected": detected,
            "expected": expected,
        }
    dest.write_bytes(data)
    return {
        "ok": True,
        "status": str(status),
        "content_type": content_type,
        "detected": detected,
        "expected": expected,
    }


def main():
    parser = argparse.ArgumentParser(description="Save discovered visual assets from a run directory.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--base-dir", help="Optional base directory containing prior dated runs to seed discovery from")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    base_dir = Path(args.base_dir) if args.base_dir else run_dir.parent
    api_dir = run_dir / "api"
    asset_dir = run_dir / "assets" / "discovered"
    library_dir = run_dir / "assets" / "library"
    manifest_dir = run_dir / "assets" / "manifests"
    report_dir = run_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)
    if library_dir.exists():
        shutil.rmtree(library_dir)
    library_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir.mkdir(parents=True, exist_ok=True)

    hits = []
    for path in (api_dir / "komodo").rglob("*.json"):
        hits.extend(collect_from_json(path))
    hits.extend(collect_from_seed_reports(base_dir, run_dir))

    unique = {}
    for url, mime, source, metadata in hits:
        unique.setdefault(url, {"mime": mime, "sources": set(), "metadata": metadata})
        if mime and not unique[url]["mime"]:
            unique[url]["mime"] = mime
        unique[url]["sources"].add(source)
        if metadata.get("media_id") and not unique[url]["metadata"].get("media_id"):
            unique[url]["metadata"] = metadata

    discovered_rows = []
    retrieved_rows = []
    error_rows = []
    library_rows = []
    used_library_paths = set()
    for url in sorted(unique):
        discovered_rows.append(
            "\t".join(
                [
                    unique[url]["mime"],
                    expected_family(url),
                    url,
                    ",".join(sorted(unique[url]["sources"])),
                ]
            )
        )
        dest = destination_for(asset_dir, url)
        if dest.exists():
            data = dest.read_bytes()[:512]
            ok, detected, expected = is_valid_download(url, unique[url]["mime"], data)
            if not ok:
                dest.unlink(missing_ok=True)

        result = None
        if not dest.exists():
            try:
                result = download(url, dest)
            except urllib.error.HTTPError as err:
                result = {
                    "ok": False,
                    "status": str(err.code),
                    "content_type": getattr(err, "headers", {}).get_content_type() if getattr(err, "headers", None) else "",
                    "detected": "http_error",
                    "expected": expected_family(url),
                }
            except Exception as err:
                result = {
                    "ok": False,
                    "status": "error",
                    "content_type": "",
                    "detected": type(err).__name__,
                    "expected": expected_family(url),
                }

            if not result["ok"] and is_protected_komodo_asset(url):
                result = {
                    "ok": False,
                    "status": "session_required",
                    "content_type": result["content_type"],
                    "detected": result["detected"],
                    "expected": result["expected"],
                }
        else:
            result = {
                "ok": True,
                "status": "cached",
                "content_type": unique[url]["mime"],
                "detected": detect_format(dest.read_bytes()[:512]),
                "expected": expected_family(url),
            }

        if result["ok"]:
            metadata = unique[url]["metadata"]
            category, library_path = copy_to_library(
                library_dir,
                dest,
                metadata,
                url,
                unique[url]["sources"],
                used_library_paths,
            )
            library_rows.append(
                {
                    "original_url": url,
                    "raw_path": str(dest),
                    "library_path": str(library_path),
                    "hardware": infer_hardware(metadata, url, unique[url]["sources"]),
                    "category": category,
                    "media_id": metadata.get("media_id", ""),
                    "parent_id": metadata.get("parent_id", ""),
                    "title": metadata.get("title", ""),
                    "slug": metadata.get("slug", ""),
                    "mime_type": unique[url]["mime"],
                    "detected_format": result["detected"],
                    "width": metadata.get("width", ""),
                    "height": metadata.get("height", ""),
                    "filesize": metadata.get("filesize", ""),
                    "source_json": metadata.get("source_json", ""),
                    "sources": ",".join(sorted(unique[url]["sources"])),
                }
            )
            retrieved_rows.append(
                "\t".join(
                    [
                        unique[url]["mime"],
                        result["detected"],
                        url,
                        str(dest),
                        ",".join(sorted(unique[url]["sources"])),
                    ]
                )
            )
        else:
            dest.unlink(missing_ok=True)
            error_rows.append(
                "\t".join(
                    [
                        result["status"],
                        result["content_type"],
                        result["detected"],
                        result["expected"],
                        url,
                        ",".join(sorted(unique[url]["sources"])),
                    ]
                )
            )

    (report_dir / "discovered-visual-assets.tsv").write_text(
        "\n".join(discovered_rows) + ("\n" if discovered_rows else ""),
        encoding="utf-8",
    )
    (report_dir / "retrieved-visual-assets.tsv").write_text(
        "\n".join(retrieved_rows) + ("\n" if retrieved_rows else ""),
        encoding="utf-8",
    )
    (report_dir / "blocked-visual-assets.tsv").write_text(
        "\n".join(error_rows) + ("\n" if error_rows else ""),
        encoding="utf-8",
    )
    manual_urls = sorted({row.split("\t")[4] for row in error_rows if len(row.split("\t")) > 4})
    (report_dir / "manual-asset-urls.txt").write_text(
        "\n".join(manual_urls) + ("\n" if manual_urls else ""),
        encoding="utf-8",
    )
    # Backward-compatible alias for earlier script versions.
    (report_dir / "downloaded-visual-assets.tsv").write_text(
        "\n".join(retrieved_rows) + ("\n" if retrieved_rows else ""),
        encoding="utf-8",
    )
    library_rows.sort(key=lambda row: (row["category"], row["hardware"], row["library_path"]))
    (manifest_dir / "asset-library.json").write_text(
        json.dumps(library_rows, indent=2, ensure_ascii=True) + ("\n" if library_rows else ""),
        encoding="utf-8",
    )
    manifest_fields = [
        "original_url",
        "raw_path",
        "library_path",
        "hardware",
        "category",
        "media_id",
        "parent_id",
        "title",
        "slug",
        "mime_type",
        "detected_format",
        "width",
        "height",
        "filesize",
        "source_json",
        "sources",
    ]
    tsv_lines = ["\t".join(manifest_fields)]
    for row in library_rows:
        tsv_lines.append("\t".join(str(row.get(field, "")) for field in manifest_fields))
    (manifest_dir / "asset-library.tsv").write_text(
        "\n".join(tsv_lines) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
