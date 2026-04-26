# Asset Library Design

## Purpose

The watch run currently saves media under `assets/discovered/` using a source-mirrored path such as `komodostation.com/wp-content/uploads/YYYY/MM/...`. That preserves provenance but makes Finder browsing awkward.

Add a generated browse-first asset library that groups downloaded assets by media type while keeping the raw source mirror intact.

## Goals

- Make it easy to browse all videos, all images, all poster frames, and all logos in one place.
- Keep hardware identity visible in filenames.
- Preserve source provenance through manifests.
- Avoid duplicating or moving the raw `assets/discovered/` archive.
- Avoid flooding primary folders with generated WordPress size variants.

## Proposed Layout

```text
assets/
  discovered/
  library/
    videos/
    images/
    logos/
    poster-frames/
    thumbnails/
    variants/
    unknown/
  manifests/
    asset-library.json
    asset-library.tsv
```

## Classification

Classify each retrieved asset from WordPress metadata and source context:

- `videos`: MP4, WEBM, MOV, or M4V source assets.
- `images`: full-size or primary still images that are not logos, poster frames, thumbnails, specs, or variants.
- `logos`: SVGs or image files with logo/title branding signals.
- `poster-frames`: video stills, especially `videoframe_*` assets tied to video sections.
- `thumbnails`: small generated sizes such as `100x100`, `150x150`, or WordPress thumbnail roles.
- `variants`: generated resized derivatives such as `768x432`, `1024x576`, `2048x988`, or any size-suffixed derivative that is not a thumbnail.
- `unknown`: assets that cannot be classified confidently.

Hardware should be inferred from section/product context first, then filename/title hints, then `unknown`.

## Filenames

Library filenames should be readable and stable:

```text
steam-controller_433313_3-in-1_1920x850.mp4
steam-controller_433293_banner_1920x1080.webm
steam-controller_433477_spec-image_2048x988.avif
steam-controller_413728_controller-logo.svg
```

Use lowercase kebab-case labels. Include:

- hardware slug
- WordPress media ID when available
- short role/title label
- dimensions when available
- original extension

If a name collides, append a short hash or sequence suffix.

## Manifests

Generate both JSON and TSV manifests under `assets/manifests/`.

Each manifest row should include:

- original URL
- raw source-mirrored path
- library path
- hardware slug
- library category
- WordPress media ID
- WordPress parent post or section ID
- title or slug
- MIME type
- detected format
- width and height when available
- file size when available
- source JSON file path

The manifest is the canonical provenance record. The library folders are for browsing.

## Existing Reports

Keep the current reports:

- `discovered-visual-assets.tsv`
- `retrieved-visual-assets.tsv`
- `blocked-visual-assets.tsv`
- `downloaded-visual-assets.tsv`
- `manual-asset-urls.txt`

Add library reports only if useful, but do not replace the existing reports in the first implementation.

## Testing

Add focused tests for:

- media-type-first placement
- WordPress size suffix detection
- manifest entries preserving source URL and raw path
- stable filenames with hardware, media ID, label, and dimensions
- collision handling

The existing fetchable Komodo AVIF regression test should continue to pass.
