#!/usr/bin/env python3
import argparse
import json
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


def collect_from_json(path: Path):
    if path.name in {"media-spec-search.json", "media-manual-search.json", "media-video.json"}:
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    hits = []
    for obj in walk_json(data):
        if not isinstance(obj, dict):
            continue
        url = obj.get("source_url")
        mime = obj.get("mime_type", "")
        if isinstance(url, str) and url.startswith("http"):
            if mime.startswith("image/") or mime.startswith("video/") or is_visual_url(url):
                hits.append((url, mime, str(path)))
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
                hits.append((url, mime, f"seed:{run_dir.name}:{report_name}"))
    return hits


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
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
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
    report_dir = run_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)

    hits = []
    for path in (api_dir / "komodo").rglob("*.json"):
        hits.extend(collect_from_json(path))
    hits.extend(collect_from_seed_reports(base_dir, run_dir))

    unique = {}
    for url, mime, source in hits:
        unique.setdefault(url, {"mime": mime, "sources": set()})
        if mime and not unique[url]["mime"]:
            unique[url]["mime"] = mime
        unique[url]["sources"].add(source)

    discovered_rows = []
    retrieved_rows = []
    error_rows = []
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
            if is_protected_komodo_asset(url):
                result = {
                    "ok": False,
                    "status": "session_required",
                    "content_type": unique[url]["mime"],
                    "detected": "protected_komodo_asset",
                    "expected": expected_family(url),
                }
            else:
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
        else:
            result = {
                "ok": True,
                "status": "cached",
                "content_type": unique[url]["mime"],
                "detected": detect_format(dest.read_bytes()[:512]),
                "expected": expected_family(url),
            }

        if result["ok"]:
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


if __name__ == "__main__":
    main()
