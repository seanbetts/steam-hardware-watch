---
name: steam-hardware-watch
description: Investigate rumored or upcoming Valve hardware launches, especially Steam Controller, Steam Machine, and Steam Frame. Use when the user wants recurring checks across Komodo, SteamDB, SteamTracking or GameTracking, Valve CDN or support endpoints, and customs or regulatory sources, with saved artifacts and an updated status ledger.
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
- [scripts/check_steamdb.sh](scripts/check_steamdb.sh)
- [scripts/check_steamtracking.sh](scripts/check_steamtracking.sh)
- [scripts/check_valve_endpoints.sh](scripts/check_valve_endpoints.sh)
- [scripts/compare_runs.py](scripts/compare_runs.py)
- [scripts/save_visual_assets.py](scripts/save_visual_assets.py)
- [scripts/draft_status_update.py](scripts/draft_status_update.py)

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
2. `SteamDB`
3. `SteamTracking / GameTracking`
4. `Valve support / store / CDN`
5. `customs / regulatory`

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

### 2. SteamDB

Check the controller app, packages, depots, and history. Prefer primary records.

Watch for:

- new apps or packages
- hidden or owner-only videos
- unboxing assets
- depot changes
- release-state changes
- CDN media or manuals linked from SteamDB

Known IDs and starting points are in [references/sources.md](references/sources.md).

The helper script saves the raw HTML pages. Summarize only material changes.

If SteamDB returns a Cloudflare challenge, `check_steamdb.sh` should record the source as blocked instead of saving the challenge HTML as a successful page. To retry with a trusted local browser session:

1. run `scripts/bootstrap_steamdb.sh`
2. complete any manual challenge in the dedicated Chrome window
3. leave the browser running
4. rerun the watch, or run `check_steamdb.sh` directly

The helper loads `.local/steamdb-env.sh` automatically and reuses the live browser over CDP when `STEAMDB_PLAYWRIGHT_FALLBACK=1`.

### 3. SteamTracking / GameTracking

Look for:

- onboarding text
- firmware update strings
- pairing flow strings
- device type names or codenames
- support or OOBE changes

Only summarize findings that materially affect launch-readiness or architecture inference.

### 4. Valve Support / Store / CDN

Run these every time if quick:

- support pages
- store app endpoints
- discoverable CDN assets
- manuals, spec sheets, legal pages, safety docs

Save any newly exposed files.

The helper script is intentionally conservative. Add extra URLs when new official pages appear.
Do not treat generic Steam Deck site media as relevant unless it is directly tied to controller, machine, or frame evidence.

### 5. Customs / Regulatory

Run when:

- Komodo gets fresh media or sections
- SteamDB gets fresh app or package movement
- SteamTracking gets materially new rollout strings
- or on a slower periodic cadence

Use for confirmation, not as the primary source of truth.

## What Counts As Meaningful

Strong examples:

- new controller-only Komodo section rollout
- new SteamDB unboxing or store media
- published price or release date
- controller-specific support or legal docs
- shipment or filing records matching the new device

Weak examples:

- cosmetic class toggles
- generic WooCommerce script presence
- reused placeholder assets
- site-wide template churn without product-specific assets

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
2. run the Komodo, SteamDB, SteamTracking, and Valve endpoint checks
3. auto-detect the previous run folder when possible
4. write a comparison report into the current run folder
5. save discovered visual assets into the current run folder
6. generate a draft status update into the current run folder

Example:

```sh
~/.codex/skills/steam-hardware-watch/scripts/run_watch.sh 2026-04-25 ~/steam_hardware_watch /tmp/SteamTracking-master
```
