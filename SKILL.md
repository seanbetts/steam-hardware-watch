---
name: steam-hardware-watch
description: Investigate rumored or upcoming Valve hardware launches, especially Steam Controller, Steam Machine, and Steam Frame. Use when the user wants recurring checks across Komodo, SteamKit/PICS, SteamDB, SteamTracking or GameTracking, Valve CDN or support endpoints, and customs or regulatory sources, with saved artifacts and an updated status ledger.
---

# Steam Hardware Watch

Use this skill for recurring evidence-gathering on Valve hardware launch status. Default focus is:

- `price`
- `release date`
- `same-time launch vs staggered launch`
- `which product is furthest along`

Keep the workflow tiered. Do the high-yield checks every run. Do slower or noisier checks when core sources move.

This skill is meant to be run by a coding agent.

- prefer agent-executed scripts and saved artifacts over manual shell steps
- only involve the human when a source requires an interactive browser challenge or similar trust/bootstrap step
- when a human step is required, keep it short, explicit, and resumable by the agent

Important scope rule:

- saved visual assets should be limited to `Steam Controller`, `Steam Machine`, and `Steam Frame`
- do not bulk-save generic `Steam Deck` marketing media unless the user explicitly asks for it

## Output Contract

Every run must:

1. Create or reuse a dated artifact folder.
2. Save raw artifacts there:
   - API responses
   - screenshots
   - downloaded media
   - extracted frames when relevant
3. Update [status/current.md](status/current.md).
4. Append material findings to [status/evidence.jsonl](status/evidence.jsonl).
5. Create or update a dated run note in [status/runs](status/runs).
6. Compare against the previous run when available and save a delta summary.
7. Save newly discovered visual assets into the run folder.
8. Generate a draft status update from the run artifacts.

Use [scripts/init_run.sh](scripts/init_run.sh) to scaffold a run folder and run note. Use [scripts/append_evidence.py](scripts/append_evidence.py) for the JSONL ledger.
Use the source helpers when available:

- [scripts/run_watch.sh](scripts/run_watch.sh)
- [scripts/check_komodo.sh](scripts/check_komodo.sh)
- [scripts/check_steamkit_pics.sh](scripts/check_steamkit_pics.sh)
- [scripts/check_steamdb.sh](scripts/check_steamdb.sh)
- [scripts/check_steamtracking.sh](scripts/check_steamtracking.sh)
- [scripts/check_steamvr_depots.sh](scripts/check_steamvr_depots.sh)
- [scripts/check_steamos_mirror.sh](scripts/check_steamos_mirror.sh)
- [scripts/check_valve_endpoints.sh](scripts/check_valve_endpoints.sh)
- [scripts/check_customs_shipments.sh](scripts/check_customs_shipments.sh)
- [scripts/compare_runs.py](scripts/compare_runs.py)
- [scripts/save_visual_assets.py](scripts/save_visual_assets.py)
- [scripts/draft_status_update.py](scripts/draft_status_update.py)

Default run artifacts live under the repo-local gitignored [runs](runs) directory. Use an explicit base directory only when the user asks to store artifacts elsewhere.

Asset discovery should be dynamic:

- discover from current-run Komodo metadata when available
- fall back to previously observed run artifacts when a later run is blocked
- never hardcode a fixed asset list into the skill itself

Default agent entry point:

- use [scripts/run_watch.sh](scripts/run_watch.sh) unless there is a specific reason to run a source helper directly
- treat the helper scripts as agent-owned implementation details
- summarize results for the human from `run-summary.md`, `status-draft.md`, and the comparison report

## Evidence Priority

Apply the rubric in [references/evidence-rubric.md](references/evidence-rubric.md).

Default source order:

1. `Komodo`
2. `SteamKit / PICS`
3. `SteamDB`
4. `SteamTracking / GameTracking`
5. `SteamVR depots`
6. `SteamOS package mirror`
7. `Valve support / store / CDN`
8. `customs / regulatory`

Treat price and exact release date as unconfirmed unless directly exposed by a primary source.

## Core Workflow

### 1. Komodo

Read [references/komodo-api-notes.md](references/komodo-api-notes.md) first.

Check:

- product records for `Steam Controller`, `Steam Machine`, `Steam Frame`
- `sections` posts and attached `media`
- public `wp-json` routes
- changes in:
  - product state
  - timestamps
  - fresh section sequences
  - fresh videos, spec art, manuals, support docs

Save useful responses under the dated run folder.

Treat Komodo as `best effort`. Cloudflare may block scripted access even when the same endpoints worked earlier.
If raw `curl` gets blocked, record the block cleanly and continue the rest of the run.
If a user needs protected Komodo media and can solve a browser challenge manually, prefer an optional Playwright profile or storage-state bootstrap over hardcoded cookies or asset manifests.

Agent behavior for Komodo fallback:

1. try the normal automated path first
2. if blocked, continue the run and report:
   - blocked source state
   - discovered vs retrieved vs blocked assets
   - manual retry URLs
3. only if protected Komodo media is important for the user’s goal, ask for or use the optional Playwright bootstrap path
4. keep any browser profile or storage-state file user-local and out of committed repo state

Preferred human-in-the-loop fallback:

- use [scripts/bootstrap_komodo.sh](scripts/bootstrap_komodo.sh) to launch a dedicated Komodo browser in the background
- let the user solve any challenge only in that isolated browser when needed
- keep that browser running while the agent reuses it over `CDP`
- use [scripts/close_komodo.sh](scripts/close_komodo.sh) when finished

### 2. SteamKit / PICS

Treat SteamKit/PICS as the primary direct Steam metadata source for apps, packages, depots, branches, and changenumber movement.

Use a narrow SteamKit2 helper when available. It should:

- use a separate low-risk Steam account, not the user's main account
- bootstrap a persistent session with `scripts/steamkit_auth.sh` before normal runs
- prefer `.local/steamkit-session.json` for routine checks so Steam Guard is not required every run
- load bootstrap credentials from `.local/steamkit-env.sh` or equivalent environment variables only when a new session is needed
- poll only watched Valve hardware app and package IDs
- save raw app/package product-info snapshots and changenumbers
- write `steamkit-pics-packages.tsv`, `steamkit-pics-key-lines.txt`, and `steamkit-pics-detail.md`
- compare snapshots against the previous run
- avoid protected depot downloads and aggressive polling

SteamKit auth handling:

- keep `.local/steamkit-env.sh` and `.local/steamkit-session.json` local and uncommitted
- prefer an interactive `scripts/steamkit_auth.sh` run for email or mobile guard challenges, because email codes are tied to the active login attempt
- use `STEAMKIT_AUTH_CODE`, `STEAMKIT_TWO_FACTOR_CODE`, or `STEAMKIT_ACCEPT_MOBILE_CONFIRMATION=1` only for non-interactive bootstrap commands
- remove one-time guard values from `.local/steamkit-env.sh` after `scripts/steamkit_auth.sh` succeeds
- if routine checks fail because the refresh token expired or was revoked, ask the user to re-run `scripts/steamkit_auth.sh` with a fresh Steam Guard approval

Primary watched IDs:

- apps: Controller `4165870`, Frame `4165890`, Machine `4165910`
- packages:
  - Controller baseline: `1558609`
  - Machine: `1629446`, `1629447`, `1629458`, `1629460`
  - Frame: `1629484`, `1629486`

Interpretation:

- SteamKit/PICS app/package changenumber or product-info movement is the earliest metadata-change signal for these package IDs.
- When package movement clusters tightly across related hardware package IDs, preserve any available per-package history timestamps and change counts. Compare against known Controller precedent: package `1558609` had a clustered change pattern plus a later follow-up before public purchase timing appeared. Treat similarity as an imminent-preorder heuristic, not confirmation.
- SteamDB package pages are corroborating/human-readable views of similar metadata, not the primary source when SteamKit data is available.
- Valve Store `appdetails` / `packagedetails` remains the public-readiness confirmation source for price, package groups, purchase/reservation state, and exact timing.
- Do not broaden this into a full SteamDB clone or general Valve game tracker unless the user explicitly changes the project scope.

### 3. SteamDB

Check the controller app, packages, depots, and history as a corroborating public view of Steam metadata. Prefer SteamKit/PICS for direct app/package metadata when available.

Reservation-package page check:

- for Machine and Frame launch readiness, check the SteamDB package pages for the known reservation package IDs
- record `Last Record Update`, `Last Changenumber`, inferred app association, and whether the page still says SteamDB has no information beyond package existence
- compare those fields against the previous run before interpreting any noisier store-page timestamp
- treat SteamDB package-page movement as high-signal corroboration of SteamKit/PICS movement; use Valve `packagedetails` and app `appdetails` to determine whether that movement has become public purchase or reservation readiness

Watch for:

- new apps or packages
- reservation-system package movement for Machine and Frame
- hidden or owner-only videos
- unboxing assets
- depot changes
- release-state changes
- CDN media or manuals linked from SteamDB

Known IDs and starting points are in [references/sources.md](references/sources.md).

Reservation package monitoring:

- check reservation-package IDs with SteamKit/PICS first when the helper is available:
  - Machine: `1629446`, `1629447`, `1629458`, `1629460`
  - Frame: `1629484`, `1629486`
  - Controller baseline: `1558609`
- then check the same IDs on SteamDB package pages for human-readable `Last Record Update` / changenumber corroboration
- then check Machine app `4165910`, Frame app `4165890`, and Controller app `4165870` through Valve `appdetails`
- treat private packages returning `packagedetails success:false` as meaningful existence evidence but not launch-ready by itself
- treat any transition to public `packagedetails`, new `appdetails.packages`, `package_groups`, price, reservation text, purchase eligibility, or exact release timing as high-signal

The helper script saves the raw HTML pages. Summarize only material changes.

If SteamDB returns a Cloudflare challenge, `check_steamdb.sh` should record the source as blocked instead of saving the challenge HTML as a successful page. To retry with a trusted local browser session:

1. run `scripts/bootstrap_steamdb.sh`
2. complete any manual challenge in the dedicated Chrome window
3. leave the browser running
4. rerun the watch, or run `check_steamdb.sh` directly

The helper loads `.local/steamdb-env.sh` automatically and reuses the live browser over CDP when `STEAMDB_PLAYWRIGHT_FALLBACK=1`.

### 4. SteamTracking / GameTracking

Use [scripts/check_steamtracking.sh](scripts/check_steamtracking.sh). When the tracking directory is a git checkout, the helper updates it with a fast-forward pull before scanning, records before/after commit metadata in `steamtracking-source.txt`, and fails loudly if the checkout is invalid or missing core extracted content.

Look for:

- onboarding text
- guided-tour and welcome-tour strings, especially `GuidedTour_SteamMachine_*` and `GuidedTour_SteamFrame_*`
- firmware update strings
- pairing flow strings
- device type names or codenames
- reservation flow allowlists and package IDs
- Steam client ARM64 beta/publicbeta manifest movement, especially `steam_client_beta_linuxarm64`
- support or OOBE changes

Hardware backend signal focus:

- Review `steamtracking-hardware-signals-key-lines.txt` every run before dismissing SteamTracking as unchanged.
- Treat setup-tour/OOBE additions as launch-readiness signals when they name Machine, Frame, SteamOS, codenames, or watched package IDs.
- Compare this report between runs; it is designed to catch semantic client/backend additions that are not visible from manifest hashes alone.

Client manifest focus:

- Treat `steam_client_beta_linuxarm64` as a high-signal Steam Machine / Fremont watch target.
- Track `steam_client_publicbeta_linuxarm64` beside it so beta-to-publicbeta movement is visible.
- Watch ARM64 hardware/runtime blocks, especially:
  - `bins_hardware_linuxarm64`
  - `bins_linuxarm64`
  - `steam_linuxarm64`
  - `runtime_steamrt_linuxarm64`
  - `bins_steamrt_linuxarm64`
- Manifest movement is a readiness heuristic only. It does not confirm product identity, preorder timing, or launch readiness without SteamKit/PICS or Valve public API movement.

Known reservation-package code baseline:

- Machine package IDs `1629446`, `1629447`, `1629458`, `1629460` and Frame package IDs `1629484`, `1629486` first appear in SteamTracking bundle snapshots at commit `334bd31a28a0` on `2026-04-28T23:46:34Z`
- the parent `4a2195407fde` does not contain those IDs
- later reservation-code commits such as `cb7ae45d7bb1` are not the first appearance; inspect diffs for behavioral changes rather than treating repeated IDs as new

Only summarize findings that materially affect launch-readiness or architecture inference.

### 5. SteamVR Depots

Check SteamVR app `250820` metadata and any local SteamVR install or downloaded depot snapshots.

Watch for:

- branch/build movement on `public`, `beta`, and `previous`
- new or changed SteamVR Linux/content depots
- dashboard, settings, driver, render model, localization, and web UI strings
- `Steam Frame`, `Frame`, `Deckard`, `Roy`, `XR`, `VR`, `Steam Link VR`, `dongle`, and controller ecosystem terms

Use [scripts/check_steamvr_depots.sh](scripts/check_steamvr_depots.sh). By default it saves public metadata and scans a local SteamVR install if one exists. Set `STEAMVR_SCAN_DIRS` to one or more local install/depot snapshot directories when deeper datamining is needed.

Treat SteamVR depot content as especially high-signal for `Steam Frame` and VR controller clues.

### 6. SteamOS Package Mirror

Check Valve's public SteamOS Arch package mirror.

Watch for:

- new top-level repo namespaces, especially product-specific repos beyond `holo` and `jupiter`
- `holo-main` versus versioned `holo-*` changes
- `jupiter-main` versus versioned `jupiter-*` changes
- source package movement under `sources/`
- `Fremont`, `Deckard`, `Steam Frame`, `Roy`, `Ibex`, `Triton`, `Lilac`, `XR`, `VR`, `dongle`, firmware, ARM, Snapdragon, or controller terms

Use [scripts/check_steamos_mirror.sh](scripts/check_steamos_mirror.sh). Treat `jupiter` as Steam Deck-specific unless a file or package explicitly mentions another codename. Treat the mirror as stronger evidence for OS/platform integration than for product naming.

### 7. Valve Support / Store / CDN

Run these every time if quick:

- support pages
- store app endpoints
- Steam hardware `appdetails` and `packagedetails` for known package IDs
- discoverable CDN assets
- manuals, spec sheets, legal pages, safety docs

Save any newly exposed files.

The helper script is intentionally conservative. Add extra URLs when new official pages appear.
Do not treat generic Steam Deck site media as relevant unless it is directly tied to controller, machine, or frame evidence.
Do not treat `rtime32_last_modified` alone as a content update; it can move with votes/comments. Prefer normalized hidden-payload hashes, `announcement_body.updatetime`, `valve_access_log.rtUpdated`, package visibility, price, package groups, reservation state, or purchase markers.

### 8. Customs / Regulatory

Use [scripts/check_customs_shipments.sh](scripts/check_customs_shipments.sh) for shipment-level customs checks.

Run customs checks every normal watch run because ImportInfo is quick and high-signal. Use customs data for confirmation, not as the primary source of truth.

Primary automated customs source:

- ImportInfo search pages for `CEVA C/O VALVE CORPORATION`, `INGRAM MICRO C/O VALVE CORPORATION`, `TECH-FRONT GAME CONSOLE VALVE`, and `VALVE CORPORATION GAME CONSOLE`
- ImportGenius public importer page for `INGRAM MICRO C/O VALVE CORPORATION`

Corroborating/manual sources:

- NBD Valve and Ingram/Valve trader pages
- ImportGenius public previews for CEVA/Valve and Tech-Front when not covered by the automated importer page

Do not use HMRC UK Trade Info for launch monitoring. It is lagged monthly trader/commodity presence, not shipment-level evidence.

## What Counts As Meaningful

Strong examples:

- new controller-only Komodo section rollout
- SteamKit/PICS app/package changenumber or product-info movement for watched Valve hardware IDs
- new SteamDB unboxing or store media
- SteamDB package-page `Last Record Update` / changenumber movement for Machine or Frame reservation packages
- published price or release date
- private Machine/Frame reservation packages becoming public or gaining price/package-group/reservation metadata
- controller-specific support or legal docs
- shipment or filing records matching the new device

Weak examples:

- cosmetic class toggles
- generic WooCommerce script presence
- reused placeholder assets
- site-wide template churn without product-specific assets
- `rtime32_last_modified` movement caused only by votes, comments, or social counters

## Run Note Format

Each dated run note should answer:

- What changed since the last run?
- Did anything change price confidence?
- Did anything change release-date confidence?
- Did anything change same-time-launch confidence?
- What remains the strongest evidence?
- What should be checked next?

Keep [status/current.md](status/current.md) short. Put narrative detail in the dated run note.
If a previous run exists, use `compare_runs.py` and fold the material deltas into the run note.

## Status Update Rules

Update `current.md` as the dashboard, not the archive.

Required sections:

- `Last updated`
- `Best current answer`
- `Source snapshot`
- `Open questions`
- `Next checks`

Append one JSON object per material finding to `evidence.jsonl`. Prefer one claim per line.

## Known Baseline

As of `2026-04-24`:

- no confirmed price leak
- no exact release date leak
- strongest controller-specific signals came from:
  - SteamDB hidden unboxing asset
  - Komodo controller-only section and media rollout
  - SteamTracking onboarding and puck/pairing flows
- Komodo still shows `Steam Machine` and `Steam Frame` as real but dormant product records with older media only

Use the seeded status files as the starting baseline rather than rediscovering this from scratch.

## Wrapper Script

Use [scripts/run_watch.sh](scripts/run_watch.sh) for the normal path.

It will:

1. initialize the run folder
2. run the Komodo, SteamKit/PICS, SteamDB, SteamTracking, SteamVR depot, SteamOS mirror, and Valve endpoint checks
3. auto-detect the previous run folder when possible
4. write a comparison report into the current run folder
5. save discovered visual assets into the current run folder
6. generate a draft status update into the current run folder

Example:

```sh
~/.codex/skills/steam-hardware-watch/scripts/run_watch.sh 2026-04-25
```
