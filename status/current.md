# Steam Hardware Watch Status

Last updated: `2026-05-11`

## Best Current Answer

- `Price`: Steam Controller remains confirmed by official Valve store APIs at `$99.00` in the US. Steam Machine and Steam Frame still have no confirmed public price.
- `Release date`: Steam Controller remains confirmed with release date `May 4, 2026` and package `1558609`. Steam Machine and Steam Frame still only expose broad `Coming soon` / `2026` timing.
- `Same-time launch`: same-day availability for the full trio is ruled out. Steam Controller is public and purchasable; Machine and Frame still have no public package, package group, price, or exact availability.

## Source Snapshot

### Komodo

- Komodo API access worked on `2026-05-11`.
- Product modified timestamps:
  - Controller: `2026-05-08T15:55:26`
  - Machine: `2026-04-24T14:32:54`
  - Frame: `2026-04-24T14:33:36`
- Controller remains the only product with recent Komodo movement. Machine and Frame remain unchanged from their April 24 timestamps.
- Visual asset retrieval completed for the current set: `141` discovered, `141` retrieved, `0` blocked.

### SteamKit / PICS

- SteamKit/PICS is now the primary direct Steam metadata baseline for watched app and package movement.
- Baseline changenumbers from the repaired `2026-05-11` run:
  - Controller app `4165870`: `35731145`
  - Frame app `4165890`: `35675573`
  - Machine app `4165910`: `35675573`
  - Controller package `1558609`: `35745078`
  - Machine packages `1629446`, `1629447`, `1629458`, `1629460`: `35672615`
  - Frame packages `1629484`, `1629486`: `35672606`
- Machine and Frame apps/packages currently require private PICS metadata tokens, but changenumbers are visible and suitable for movement monitoring.
- Raw snapshot: `/Users/sean/Coding/steam-hardware-watch/runs/2026-05-11/api/steamkit/pics-product-info.json`
- Future runs also write `reports/steamkit-pics-detail.md` with human-readable product grouping, previous changenumber comparison, SHA hash, and exposed app/depot/branch fields.

### SteamDB

- Automated SteamDB access remained blocked on `2026-05-11`.
- The package report is still a structural baseline, not a content baseline: all watched SteamDB package rows are `missing_or_blocked`.
- SteamDB remains useful as corroborating/human-readable metadata once a trusted browser session can pass the challenge, but SteamKit/PICS now covers primary package movement.

### SteamTracking / GameTracking

- Fresh SteamTracking content still contains the known Triton/Ibex controller pairing surface:
  - `ibex_internal`
  - `ibex_external`
  - `PairDongleTritonConnected`
  - `PairDongleTritonDocked`
  - `ShouldTritonPairInOobe`
- Known reservation package-code baseline remains: Machine package IDs `1629446`, `1629447`, `1629458`, `1629460` and Frame package IDs `1629484`, `1629486` first appeared in SteamTracking commit `334bd31a28a0` at `2026-04-28T23:46:34Z`.
- No new price or exact availability signal was found in this run.

### SteamVR Depots

- SteamVR news metadata was saved.
- SteamDB's SteamVR depot page remained blocked by challenge pages, so no fresh depot manifest/build comparison was collected.
- No local SteamVR depot snapshot was available for deeper content scanning.

### SteamOS Package Mirror

- Valve's public SteamOS package mirror was reachable.
- Notable mirror hits include `fremont-hw-support 20260506.1-1` in `holo-3.8` and `holo-main`.
- No direct `Deckard`, `Roy`, `Steam Frame`, `Steam Machine`, ARM/Snapdragon, or new product-specific top-level repo namespace appeared in the default pass.

### Valve Support / Store / CDN

- Official Valve pages and APIs were reachable.
- Valve API package snapshot:
  - Controller app `4165870`: public, package `1558609`, package group present, `$99.00`.
  - Frame app `4165890`: public app metadata, `Coming soon`, no packages, no package groups, no price.
  - Machine app `4165910`: public app metadata, `Coming soon`, no packages, no package groups, no price.
  - Machine packages `1629446`, `1629447`, `1629458`, `1629460`: `packagedetails success:false`.
  - Frame packages `1629484`, `1629486`: `packagedetails success:false`.
- This remains the cleanest public-readiness baseline heading into next week.

### Customs / Regulatory

- ImportInfo automated customs fetches were blocked on `2026-05-11`.
- The latest useful customs evidence remains the `2026-05-01` NBD / ImportGenius pass:
  - `WIRELESS PC CONTROLLER` row dated `2026-04-04`.
  - `GAME CONSOLE` shipment arriving `2026-04-23` for `INGRAM MICRO C/O VALVE CORPORATION`.
- Customs data remains corroborating evidence only, not price/date/product-identity proof.

## Open Questions

- When will Valve publish Steam Machine and Steam Frame prices?
- When will Steam Machine and Steam Frame receive public packages or package groups?
- Will SteamKit/PICS changenumber movement precede public Valve API readiness?
- Are the `fremont-hw-support` SteamOS packages related to Steam Machine launch preparation?

## Next Checks

- Watch SteamKit/PICS changenumbers for all watched app and package IDs.
- Watch Valve `appdetails` / `packagedetails` for Machine and Frame package or package-group exposure.
- Get one trusted-browser SteamDB package-page baseline if we still want human-readable SteamDB corroboration.
- Continue normal Komodo, SteamTracking, SteamOS mirror, Valve API, and customs checks.
