# Komodo API Notes

## Useful Endpoints

- `/wp-json/`
- `/wp-json/wp/v2/product`
- `/wp-json/wp/v2/sections`
- `/wp-json/wp/v2/media`

## What Worked

- product lookups by ID or slug
- section searches
- media searches
- media by `parent`

## What To Look For

- `publish` vs hidden states
- `product-type-simple` or other type changes
- `outofstock`
- `wishlist-only`
- new `sections` posts
- fresh `2026/..` uploads
- videos, spec art, manuals, safety docs

## Important Pitfalls

- Raw `curl` can hit Cloudflare or DNS/sandbox issues.
- As of clean packaging tests, Cloudflare can block both `curl` and browser automation paths.
- Treat Komodo automation as `best effort`, not guaranteed.
- If protected media matters, use an optional Playwright bootstrap path instead of hardcoding cookies:
  - launch a persistent browser profile
  - solve the challenge manually once
  - save storage state or reuse the profile on later runs
  - if storage state is not enough, attach to the still-running trusted browser over CDP
- A low-disruption background flow is preferred:
  - launch a dedicated Komodo Chrome instance in the background
  - leave it running
  - let the agent reuse it over CDP
  - close it when the run is done
- Frontend CSS class toggles were low-yield. The public JSON endpoints were much more useful than DOM manipulation.
- Fresh media attached to `sections` posts mattered more than old product-page HTML.
- If Komodo is blocked on a given run, keep the rest of the pipeline going and record the block in the reports.

## Optional Playwright Bootstrap

Use only as a fallback when Komodo blocks normal automation and you need to recover protected media or JSON.

Repeatable pattern:

1. `playwright-cli open --persistent --profile /path/to/profile https://komodostation.com/product/steam-controller_jpy/`
2. Solve any Cloudflare challenge manually in that browser.
3. Optionally save storage state:
   - `playwright-cli state-save /path/to/komodo-state.json`
4. Reuse in helper scripts with environment variables:
   - `PLAYWRIGHT_PROFILE_DIR=/path/to/profile`
   - or `PLAYWRIGHT_STORAGE_STATE=/path/to/komodo-state.json`
   - optional `PLAYWRIGHT_REFERER=https://komodostation.com/product/steam-controller_jpy/`

If the saved storage state still gets blocked, use the stronger live-session path:

1. Keep the trusted Playwright browser running on the same profile.
2. Find the local `--remote-debugging-port` for that profile with `ps`.
3. Set:
   - `PLAYWRIGHT_CDP_ENDPOINT=http://127.0.0.1:PORT`
   - `KOMODO_PLAYWRIGHT_FALLBACK=1`
4. Run the helper scripts again.

`check_komodo.sh` will try to auto-detect a CDP endpoint from the running profile when `PLAYWRIGHT_PROFILE_DIR` is set.

This keeps the repo reusable: the bootstrap is optional, user-local, and not committed.

## Known Baseline On 2026-04-24

- Controller had a fresh same-day section/media rollout.
- Machine and Frame only exposed old wishlist sections and older assets.
- Product records for all three were real published WooCommerce entries in the same held state.
