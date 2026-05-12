# Steam Hardware Watch Status

Last updated: `2026-05-12`

## Best Current Answer

- `Price`: Steam Controller remains confirmed by official Valve store APIs at `$99.00` in the US. Steam Machine and Steam Frame still have no confirmed public price.
- `Release date`: Steam Controller remains confirmed with release date `May 4, 2026` and package `1558609`. Steam Machine and Steam Frame still only expose broad `Coming soon` / `2026` timing.
- `Same-time launch`: same-day availability for the full trio is ruled out. Steam Controller is public and purchasable; Machine and Frame still have no public package, package group, price, or exact availability. Steam Machine reservation package changenumbers moved on `2026-05-12`; the multi-package change cluster resembles the Steam Controller package-history pattern before its public purchase timing appeared, but public Valve APIs still do not expose Machine purchase or reservation readiness.

## Source Snapshot

### Komodo

- Komodo API access worked on `2026-05-12`.
- Product modified timestamps:
  - Controller: `2026-05-12T09:15:51`
  - Machine: `2026-04-24T14:32:54`
  - Frame: `2026-04-24T14:33:36`
- Controller remains the only product with recent Komodo movement. A direct JSON diff versus `2026-05-11` found only `modified` / `modified_gmt` changes, so this is timestamp-only until corroborated by visible content, media, or store-state movement. Machine and Frame remain unchanged from their April 24 timestamps.
- Visual asset retrieval completed for the current set: `141` discovered, `141` retrieved, `0` blocked.

### SteamKit / PICS

- SteamKit/PICS is now the primary direct Steam metadata baseline for watched app and package movement.
- Current changenumbers from the `2026-05-12` run:
  - Controller app `4165870`: `35731145`
  - Frame app `4165890`: `35675573`
  - Machine app `4165910`: `35675573`
  - Controller package `1558609`: `35745078`
  - Machine package `1629446`: `35819604` (`35672615` on `2026-05-11`)
  - Machine package `1629447`: `35819607` (`35672615` on `2026-05-11`)
  - Machine package `1629458`: `35819602` (`35672615` on `2026-05-11`)
  - Machine package `1629460`: `35819593` (`35672615` on `2026-05-11`)
  - Frame packages `1629484`, `1629486`: `35672606`
- The four watched Steam Machine package IDs moved in SteamKit/PICS on `2026-05-12`. This is the strongest current signal of fresh backend work, but it remains private metadata only.
- Manual package-history comparison adds context: Steam Controller package `1558609` reportedly had three changes in about 40 minutes plus one later follow-up change roughly two days before Valve's public purchase-timing update appeared. The Machine package set now shows a tighter multi-package cluster, with uneven per-package counts (`1 / 3 / 3 / 4`) across about three minutes. Treat this as a medium-strength imminent-preorder heuristic, not confirmation.
- Machine and Frame apps/packages currently require private PICS metadata tokens, but changenumbers are visible and suitable for movement monitoring.
- Raw snapshot: `/Users/sean/Coding/steam-hardware-watch/runs/2026-05-12/api/steamkit/pics-product-info.json`
- Future runs also write `reports/steamkit-pics-detail.md` with human-readable product grouping, previous changenumber comparison, SHA hash, and exposed app/depot/branch fields.

### SteamDB

- Automated SteamDB access remained blocked on `2026-05-12`.
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
- This remains the cleanest public-readiness baseline. The `2026-05-12` SteamKit/PICS Machine package movement has not propagated to public `appdetails`, `packagedetails`, packages, package groups, price, or exact timing.

### Customs / Regulatory

- ImportInfo automated customs fetches were blocked on `2026-05-12`.
- The latest useful customs evidence remains the `2026-05-01` NBD / ImportGenius pass:
  - `WIRELESS PC CONTROLLER` row dated `2026-04-04`.
  - `GAME CONSOLE` shipment arriving `2026-04-23` for `INGRAM MICRO C/O VALVE CORPORATION`.
- Customs data remains corroborating evidence only, not price/date/product-identity proof.

## Open Questions

- When will Valve publish Steam Machine and Steam Frame prices?
- When will Steam Machine and Steam Frame receive public packages or package groups?
- Will SteamKit/PICS changenumber movement precede public Valve API readiness?
- Will the Machine package cluster receive a Controller-like follow-up changenumber bump before public preorder/reservation metadata appears?
- Are the `fremont-hw-support` SteamOS packages related to Steam Machine launch preparation?

## Next Checks

- Watch SteamKit/PICS changenumbers for all watched app and package IDs, especially whether the `2026-05-12` Machine package cluster gets a follow-up bump or begins to expose public metadata.
- Watch Valve `appdetails` / `packagedetails` for Machine and Frame package or package-group exposure.
- Get one trusted-browser SteamDB package-page baseline if we still want human-readable SteamDB corroboration.
- Continue normal Komodo, SteamTracking, SteamOS mirror, Valve API, and customs checks.
