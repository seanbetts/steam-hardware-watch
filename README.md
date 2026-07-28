# Steam Hardware Watch

Agent-oriented monitoring workflow for rumored or upcoming Valve hardware. The current default focus is Steam Frame launch readiness, with launched hardware retained as comparator context:

- active target: `Steam Frame`
- comparators: `Steam Controller`, `Steam Machine`

It is designed to be run by a coding agent through the included `SKILL.md`, with scripts that:

- check `Komodo`, `SteamKit/PICS`, `SteamDB`, `SteamTracking`, and Valve endpoints
- check `SteamVR` depot metadata and the public SteamOS package mirror
- save raw artifacts for each run
- compare against the previous run
- draft a human-readable status update
- track visual assets as `discovered`, `retrieved`, or `blocked`

## What This Is

This repo is not a generic scraper.

It is a repeatable evidence-gathering workflow for answering a narrow set of questions:

- did anything change?
- is there a price leak?
- is there a release-date leak?
- has Steam Frame gained package, price, release-date, site, client, or shipment evidence?
- are there new media assets or support documents?

The normal Frame-focused entry point is:

```sh
scripts/run_frame_watch.sh YYYY-MM-DD
```

By default this writes ignored artifacts under `runs/YYYY-MM-DD` in this repo and uses `/tmp/SteamTracking-master`.
Pass explicit paths only when you want to override those defaults:

```sh
scripts/run_frame_watch.sh YYYY-MM-DD /custom/run-base /path/to/SteamTracking
```

Use `scripts/run_watch.sh` when you explicitly want the broader all-hardware view or when debugging an individual source helper.

For a quick Komodo-only recheck, use:

```sh
scripts/run_frame_watch.sh --komodo-only YYYY-MM-DD
```

This initializes the dated run folder, runs `check_komodo.sh`, prints whether Komodo product timestamps changed since the previous run, reports any newly discovered Komodo asset URLs, writes `run-summary.md`, and skips SteamKit/PICS, SteamDB, SteamTracking, SteamVR, SteamOS, Valve endpoint, customs, comparison, and status-draft steps.

Example output:

```text
Run dir: /Users/sean/Coding/steam-hardware-watch/runs/2026-07-28
Run note: /Users/sean/Coding/steam-hardware-watch/status/runs/2026-07-28.md
Saved Komodo API responses to /Users/sean/Coding/steam-hardware-watch/runs/2026-07-28/api/komodo
Saved Komodo summaries to /Users/sean/Coding/steam-hardware-watch/runs/2026-07-28/reports
Komodo updated: yes (changed since previous run 2026-07-27)
Komodo changes:
- frame: 2026-07-03T15:56:30 -> 2026-07-28T10:11:12
Komodo timestamps: controller=2026-07-27T15:46:17, machine=2026-07-27T15:39:56, frame=2026-07-28T10:11:12
Komodo new assets: yes (1 new, 3 current, since previous run 2026-07-27)
Komodo new asset URLs:
- https://komodostation.com/wp-content/uploads/2026/07/new-frame-asset.jpg
Run summary: /Users/sean/Coding/steam-hardware-watch/runs/2026-07-28/reports/run-summary.md
Komodo-only run complete.
```

If nothing changed, the key lines should read:

```text
Komodo updated: no (matches previous run 2026-07-27)
Komodo new assets: no (2 current, matches previous run 2026-07-27)
```

## Repository Layout

```text
steam-hardware-watch/
├── SKILL.md
├── README.md
├── .gitignore
├── agents/
├── references/
├── scripts/
└── status/
```

Important directories:

- `scripts/`: the runnable checks and report builders
- `references/`: source map, Komodo notes, evidence rubric
- `status/`: seeded baseline answer and run notes
- `runs/`: local gitignored run artifacts

## Dependencies

Required:

- `bash` or `sh`
- `curl`
- `jq`
- `python3`
- `node`
- `rg`

Recommended:

- `.NET SDK 10` for the SteamKit/PICS helper
- `playwright-cli`
- Google Chrome or Chromium available to Playwright
- macOS `open` command with Google Chrome installed for the Komodo background bootstrap helper

Optional:

- `ffmpeg` for frame extraction or manual media inspection

## Quick Start

1. Clone the repo.
2. Make the scripts executable if needed:

```sh
chmod +x scripts/*.sh
```

3. Ensure `SteamTracking` is available locally as a git checkout, for example at:

```text
/tmp/SteamTracking-master
```

`scripts/check_steamtracking.sh` fast-forwards this checkout before scanning and records the before/after commit in each run.

4. Run a Frame-focused watch pass:

```sh
scripts/run_frame_watch.sh 2026-07-28
```

This creates a dated run folder under `runs/2026-07-28`.

### Common Path

For the least disruptive Komodo flow, use the dedicated background browser bootstrap:

```sh
scripts/bootstrap_komodo.sh
scripts/run_frame_watch.sh 2026-07-28
scripts/close_komodo.sh
```

That keeps Komodo access isolated from your normal Chrome profile and gives the agent a reusable trusted browser session when Komodo blocks normal automation.

For a focused Komodo recheck, use the same bootstrap with the Komodo-only flag:

```sh
scripts/bootstrap_komodo.sh
scripts/run_frame_watch.sh --komodo-only 2026-07-28
scripts/close_komodo.sh
```

SteamDB can require the same live-browser treatment:

```sh
scripts/bootstrap_steamdb.sh
scripts/run_frame_watch.sh 2026-07-28
scripts/close_steamdb.sh
```

If both sources are blocked, bootstrap both before the run.

## Optional SteamKit/PICS Account Setup

SteamKit/PICS is the primary direct Steam metadata source for watched app and package movement. It requires a low-risk Steam account because the helper logs into Steam like a normal client and requests metadata only.

Install requirement:

```sh
dotnet restore tools/steamkit-pics/SteamHardwarePics.csproj
```

Create a local-only env file:

```sh
mkdir -p .local
cat > .local/steamkit-env.sh <<'EOF'
STEAMKIT_USERNAME='your-watch-account'
STEAMKIT_PASSWORD='your-watch-account-password'
# Usually leave these unset and enter the code when scripts/steamkit_auth.sh prompts.
# For non-interactive use, set one of these only when Steam Guard asks for it:
# STEAMKIT_AUTH_CODE='email-code'
# STEAMKIT_TWO_FACTOR_CODE='authenticator-code'
# Or approve the mobile prompt manually, then set:
# STEAMKIT_ACCEPT_MOBILE_CONFIRMATION='1'
EOF
chmod 600 .local/steamkit-env.sh
```

Bootstrap a persistent local session:

```sh
scripts/steamkit_auth.sh
```

This writes `.local/steamkit-session.json` with a Steam refresh token and guard data. The file is gitignored, should stay local, and is sensitive. After it is created, remove any one-time `STEAMKIT_AUTH_CODE`, `STEAMKIT_TWO_FACTOR_CODE`, or `STEAMKIT_ACCEPT_MOBILE_CONFIRMATION` line from `.local/steamkit-env.sh`.

Then run either the source directly:

```sh
scripts/check_steamkit_pics.sh runs/2026-05-11
```

or the normal Frame watcher:

```sh
scripts/run_frame_watch.sh 2026-07-28
```

The Frame watcher automatically uses `.local/steamkit-session.json`, so routine runs should not ask for a fresh Steam Guard code. If Steam invalidates the refresh token, rerun `scripts/steamkit_auth.sh` with a fresh guard approval to create a new session file.

Outputs:

- `RUN_DIR/api/steamkit/pics-product-info.json`
- `RUN_DIR/reports/steamkit-pics-packages.tsv`
- `RUN_DIR/reports/steamkit-pics-key-lines.txt`
- `RUN_DIR/reports/steamkit-pics-detail.md`
- `RUN_DIR/reports/steamkit-pics-errors.txt`

If the env file and session file are missing, the script writes a non-fatal `missing_credentials` report so the Frame watcher still completes. Do not use your main Steam account, do not poll aggressively, and do not extend this helper to protected depot downloads.

## Output

Each run writes:

- raw API and HTML snapshots
- per-source summary files
- comparison report versus the previous run when available
- `frame-focus.md`
- `run-summary.md`
- `status-draft.md`
- visual asset ledgers:
  - `discovered-visual-assets.tsv`
  - `retrieved-visual-assets.tsv`
  - `blocked-visual-assets.tsv`
  - `manual-asset-urls.txt`
- `steamkit-pics-packages.tsv`
- `steamkit-pics-detail.md`
- `steamvr-depots-key-lines.txt`
- `steamos-mirror-key-lines.txt`

The first human-readable file to inspect is:

- `RUN_DIR/reports/frame-focus.md`

Then use:

- `RUN_DIR/reports/run-summary.md`
- `RUN_DIR/reports/compare-vs-*.md`

## Agent Checklist

For a fresh coding agent, the normal operating loop is:

1. Read `SKILL.md` before running or editing anything.
2. Choose the narrowest relevant command:
   - `scripts/run_frame_watch.sh YYYY-MM-DD` for the normal Frame-focused pass.
   - `scripts/run_frame_watch.sh --komodo-only YYYY-MM-DD` for a quick Komodo recheck.
   - `scripts/run_watch.sh YYYY-MM-DD` only for the broader all-hardware view or source-helper debugging.
3. Inspect `frame-focus.md` first for full runs, then `run-summary.md`, `status-draft.md`, and `compare-vs-*.md`.
4. Put primary package/store gates first when reporting: SteamKit/PICS, Valve APIs, SteamDB package pages, then Komodo.
5. Treat SteamTracking, SteamVR, SteamOS, and customs rows as secondary context unless they connect directly to Frame package/API, public-page, or shipment evidence.
6. Update `status/current.md` only for material movement or a new clean baseline.
7. Append `status/evidence.jsonl` only for evidence-grade findings, using `scripts/append_evidence.py`.
8. Keep raw artifacts under gitignored `runs/`; never commit `.local/`, browser profiles, sessions, cookies, or one-time auth codes.
9. Validate before finishing: parse `status/evidence.jsonl` if touched, run `git diff --check`, inspect staged scope, and finish with `git status --short`.
10. Commit only the intended files.

## Agent Usage

This repo is meant to be used by coding agents, not only by a human at a shell.

### Codex

Install or symlink the repo into your Codex skills directory:

```sh
ln -s "$PWD" ~/.codex/skills/steam-hardware-watch
```

Then ask Codex to use the `steam-hardware-watch` skill.

### Claude or Other Agents

Point the agent at this repo and have it:

1. read `SKILL.md`
2. use `scripts/run_frame_watch.sh` as the default Frame-focused entry point
3. summarize results from:
   - `frame-focus.md`
   - `run-summary.md`
   - `status-draft.md`
   - any `compare-vs-*.md`

The agent should treat the scripts as implementation details and present the run summaries to the user.

## Komodo Caveat

`Komodo` is the most valuable source and the least reliable one.

What usually works:

- public `wp-json` product, section, and media endpoints
- still-image asset URLs

What may fail:

- video and AVIF asset downloads
- some API fetches when Cloudflare blocks automation
- optional Playwright fallback if it is pointed at a problematic local browser channel

The workflow handles this by separating:

- `discovered`
- `retrieved`
- `blocked`

Blocked assets are still reported with direct manual URLs.

## Optional Komodo Browser Bootstrap

Use this only when Komodo blocks automated media access and you need the protected files.

This is intentionally user-local and should never be committed.

### Preferred Low-Disruption Flow

Use the bundled helper to launch a dedicated Komodo Chrome instance in the background:

```sh
scripts/bootstrap_komodo.sh
```

This:

- uses a dedicated profile under `.local/`
- launches a separate Chrome instance in the background
- exposes a stable CDP endpoint
- writes `.local/komodo-env.sh`

If Komodo needs any manual interaction, switch to that dedicated window when convenient. Otherwise leave it running in the background.

Then run:

```sh
scripts/run_frame_watch.sh 2026-07-28
```

`check_komodo.sh` will automatically pick up `.local/komodo-env.sh` when present.
`run_frame_watch.sh` will also auto-close the dedicated Komodo browser at the end unless you set:

```sh
KOMODO_KEEP_BROWSER_OPEN=1
```

When finished:

```sh
scripts/close_komodo.sh
```

That closes only the dedicated Komodo browser/profile, not your normal run output.

### Manual Playwright Bootstrap

If you prefer the raw Playwright flow, you can still do it manually.

1. Open a persistent Playwright browser profile:

```sh
playwright-cli open --persistent --profile ~/.steam-hardware-watch/playwright-profile https://komodostation.com/product/steam-controller_jpy/
```

2. Solve any challenge manually in that browser.

3. Optionally save storage state:

```sh
playwright-cli state-save ~/.steam-hardware-watch/komodo-state.json
```

4. Reuse that state for later agent runs with environment variables:

```sh
PLAYWRIGHT_PROFILE_DIR=~/.steam-hardware-watch/playwright-profile
PLAYWRIGHT_STORAGE_STATE=~/.steam-hardware-watch/komodo-state.json
PLAYWRIGHT_REFERER=https://komodostation.com/product/steam-controller_jpy/
KOMODO_PLAYWRIGHT_FALLBACK=1
```

The current helper scripts support these variables for Playwright-based fallback fetches.

Important:

- the Komodo Playwright fallback is `off` by default
- it only runs when `KOMODO_PLAYWRIGHT_FALLBACK=1` is set
- by default the Playwright helpers use Playwright's normal Chromium target, not your system Chrome
- only set `PLAYWRIGHT_BROWSER_CHANNEL=chrome` if you explicitly want that behavior

### Stronger Fallback: Live Trusted Browser Attach

If storage state is not enough for Komodo, use a live trusted browser session instead.

This is the most reliable path we found for protected Komodo media.

1. Open the persistent profile and load Komodo successfully:

```sh
playwright-cli open --headed --persistent --profile ~/.steam-hardware-watch/playwright-profile https://komodostation.com/product/steam-controller_jpy/
```

2. Leave that browser running.

3. Discover the local CDP port for that profile:

```sh
ps aux | rg 'playwright-profile|remote-debugging-port'
```

4. Set:

```sh
PLAYWRIGHT_CDP_ENDPOINT=http://127.0.0.1:PORT
KOMODO_PLAYWRIGHT_FALLBACK=1
```

5. Run the watcher again.

If `PLAYWRIGHT_PROFILE_DIR` is set and a matching Chrome process is already running, `scripts/check_komodo.sh` will try to discover the CDP port automatically and use it instead of reopening the locked profile.

The helper scripts now support that same live-session route with:

- `PLAYWRIGHT_CDP_ENDPOINT`
- automatic local env loading from `.local/komodo-env.sh`

## Optional SteamDB Browser Bootstrap

SteamDB may return a Cloudflare browser challenge to `curl` and to fresh automated browser contexts. The SteamDB helper uses a realistic Chrome user agent by default and rejects challenge HTML instead of saving it as a successful page. When that is not enough, use a dedicated live Chrome session.

Use the bundled helper:

```sh
scripts/bootstrap_steamdb.sh
```

This:

- uses a dedicated profile under `.local/`
- launches a separate Chrome instance in the background
- exposes a stable CDP endpoint
- writes `.local/steamdb-env.sh`

If SteamDB needs manual interaction, switch to that dedicated Chrome window, complete the challenge, and leave the browser running.

Then run:

```sh
scripts/run_frame_watch.sh 2026-07-28
```

`check_steamdb.sh` automatically picks up `.local/steamdb-env.sh` when present. `run_frame_watch.sh` auto-closes the dedicated SteamDB browser at the end unless you set:

```sh
STEAMDB_KEEP_BROWSER_OPEN=1
```

When finished:

```sh
scripts/close_steamdb.sh
```

Manual equivalent:

```sh
STEAMDB_PLAYWRIGHT_FALLBACK=1
STEAMDB_PROFILE_DIR=~/.steam-hardware-watch/playwright-steamdb-profile
STEAMDB_CDP_ENDPOINT=http://127.0.0.1:PORT
STEAMDB_BROWSER_CHANNEL=chrome
```

## SteamVR And SteamOS Datamining

The wrapper also checks two lower-level sources:

- `scripts/check_steamvr_depots.sh` saves SteamVR app `250820` metadata and scans local SteamVR install/depot snapshots when available.
- `scripts/check_steamos_mirror.sh` saves public SteamOS package mirror metadata and extracts package names from selected `holo` and `jupiter` repos by default.

Useful knobs:

```sh
STEAMVR_SCAN_DIRS="/path/to/SteamVR /path/to/depot_snapshot"
STEAMOS_MIRROR_REPOS="holo-3.8 holo-main jupiter-3.8 jupiter-main"
```

Set `STEAMOS_MIRROR_REPOS` to include `core`, `extra`, or `multilib` repos when you want a broader but noisier package pass.

SteamVR content is distributed through SteamPipe depots rather than the SteamOS package mirror. Use the generated `steamvr-depot-download-candidates.txt` as a reminder of the high-yield depot IDs, then fill in manifest IDs from SteamDB before downloading old snapshots with Steam's depot tools.

## Current Known Limits

- `Komodo` can block both `curl` and fresh browser automation.
- `SteamKit/PICS` requires a separate Steam account and a one-time Steam Guard bootstrap to create `.local/steamkit-session.json`.
- `SteamDB` can return a Cloudflare browser challenge to curl and fresh automated browser contexts.
- `SteamVR` depot contents require a Steam install, Steam console, SteamCMD, or another depot downloader; the helper does not download large depots by default.
- The SteamOS mirror is public, but package names are not proof of product launch state without corroborating evidence.
- `/tmp/SteamTracking-*` checkouts can become invalid even when source files still exist. If `git -C /tmp/SteamTracking-* status` fails, clone a fresh shallow checkout and rerun with that path.
- We can currently discover and report blocked media URLs even when we cannot download them automatically.
- Exported storage state may still be insufficient for Cloudflare-protected Komodo assets.
- Live trusted browser attach is currently the strongest repeatable fallback for protected Komodo media.
- Live trusted browser attach is also the strongest SteamDB fallback when browser-style curl is blocked.
- The fully non-visual path is not reliable yet; after bootstrap, the working fallback is still a live dedicated browser running in the background.

## Recommended Workflow

Normal use:

1. run `scripts/run_frame_watch.sh`
2. read `frame-focus.md`, then `run-summary.md`
3. inspect the comparison report if something changed
4. update `status/current.md` and `status/evidence.jsonl` only for material changes

Quick Komodo recheck:

1. run `scripts/run_frame_watch.sh --komodo-only YYYY-MM-DD`
2. scan the CLI lines for product timestamp changes and new asset URLs
3. read `run-summary.md` and the Komodo reports under `reports/`
4. rerun the full Frame watcher only if Komodo exposes material movement

Escalation:

1. if Komodo blocks, continue the run
2. use `manual-asset-urls.txt` for manual follow-up
3. if SteamDB blocks, use `scripts/bootstrap_steamdb.sh` and rerun when SteamDB verification is important
4. only use the Playwright bootstrap if protected Komodo media or SteamDB verification is important to the run
