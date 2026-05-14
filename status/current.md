# Steam Hardware Watch Status

Last updated: `2026-05-14`

## Best Current Answer

- `Price`: Steam Controller remains confirmed by official Valve store APIs at `$99.00` in the US. Steam Machine and Steam Frame still have no confirmed public price.
- `Release date`: Steam Controller remains confirmed with release date `May 4, 2026` and package `1558609`. Steam Machine and Steam Frame still only expose broad `Coming soon` / `2026` timing.
- `Same-time launch`: same-day availability for the full trio is ruled out. Steam Controller is public and purchasable; Machine and Frame still have no public package, package group, price, or exact availability. Steam Machine reservation package changenumbers have now moved twice: a multi-package cluster on `2026-05-12`, followed by another bump across all four watched Machine packages on `2026-05-14`. That is a stronger Controller-like backend-prep signal for Machine, but public Valve APIs still do not expose Machine purchase or reservation readiness.

## Source Snapshot

### Komodo

- Komodo was partially available on `2026-05-14` through the dedicated browser fallback.
- Product modified timestamps captured in this run:
  - Controller: `2026-05-13T09:02:58`
  - Machine: `n/a` in this run because the optional Machine product fetch failed
  - Frame: `n/a` in this run because the optional Frame product fetch failed
- Controller changed from `2026-05-12T09:15:51` to `2026-05-13T09:02:58`, but a direct JSON diff versus `2026-05-12` found only `modified` / `modified_gmt` changes. Treat this as timestamp-only until corroborated by visible content, media, store-state movement, or Steam metadata.
- Machine and Frame Komodo product/section endpoints failed in this run. Any compare-report lines about Machine or Frame section removal are partial-fetch artifacts, not evidence that Valve removed sections.
- Visual asset retrieval found `141` candidate assets, retrieved `136`, and left `5` blocked known Komodo URLs for manual retry.

### SteamKit / PICS

- SteamKit/PICS is the primary direct Steam metadata source for watched app and package movement.
- Current changenumbers from the `2026-05-14` run:
  - Controller app `4165870`: `35731145`
  - Frame app `4165890`: `35675573`
  - Machine app `4165910`: `35675573`
  - Controller package `1558609`: `35745078`
  - Machine package `1629446`: `35842876` (`35819604` on `2026-05-12`)
  - Machine package `1629447`: `35842851` (`35819607` on `2026-05-12`)
  - Machine package `1629458`: `35842860` (`35819602` on `2026-05-12`)
  - Machine package `1629460`: `35842863` (`35819593` on `2026-05-12`)
  - Frame packages `1629484`, `1629486`: `35672606`
- The four watched Steam Machine package IDs received a follow-up SteamKit/PICS changenumber bump on `2026-05-14`. This is the strongest current signal of fresh Machine-specific backend work, especially because the two watched Steam Frame package IDs did not move.
- Manual package-history context remains important: Steam Controller package `1558609` reportedly had a clustered change pattern plus one later follow-up change roughly two days before Valve's public purchase-timing update appeared. The Machine set now has both the initial multi-package cluster and the later follow-up bump. Treat this as a stronger imminent-preorder heuristic, not confirmation.
- Machine and Frame apps/packages currently require private PICS metadata tokens, but changenumbers are visible and suitable for movement monitoring.
- Raw snapshot: `/Users/sean/Coding/steam-hardware-watch/runs/2026-05-14/api/steamkit/pics-product-info.json`
- Human-readable detail: `/Users/sean/Coding/steam-hardware-watch/runs/2026-05-14/reports/steamkit-pics-detail.md`

### SteamDB

- Automated SteamDB access remained blocked on `2026-05-14`.
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
- Notable mirror hits still include `fremont-hw-support 20260506.1-1` in `holo-3.8` and `holo-main`.
- No direct `Deckard`, `Roy`, `Steam Frame`, `Steam Machine`, ARM/Snapdragon, or new product-specific top-level repo namespace appeared in the default pass.

### Valve Support / Store / CDN

- Official Valve pages and APIs were reachable.
- Valve API package snapshot:
  - Controller app `4165870`: public, package `1558609`, package group present, `$99.00`.
  - Frame app `4165890`: public app metadata, `Coming soon`, no packages, no package groups, no price.
  - Machine app `4165910`: public app metadata, `Coming soon`, no packages, no package groups, no price.
  - Machine packages `1629446`, `1629447`, `1629458`, `1629460`: `packagedetails success:false`.
  - Frame packages `1629484`, `1629486`: `packagedetails success:false`.
- This remains the cleanest public-readiness baseline. The `2026-05-14` SteamKit/PICS Machine package movement has not propagated to public `appdetails`, `packagedetails`, packages, package groups, price, or exact timing.

### Customs / Regulatory

- ImportInfo automated customs fetches were blocked on `2026-05-14`.
- The latest useful customs evidence remains the `2026-05-01` NBD / ImportGenius pass:
  - `WIRELESS PC CONTROLLER` row dated `2026-04-04`.
  - `GAME CONSOLE` shipment arriving `2026-04-23` for `INGRAM MICRO C/O VALVE CORPORATION`.
- Customs data remains corroborating evidence only, not price/date/product-identity proof.

## Open Questions

- When will Valve publish Steam Machine and Steam Frame prices?
- When will Steam Machine and Steam Frame receive public packages or package groups?
- Will the `2026-05-14` Machine follow-up changenumber bump precede public Valve API readiness?
- Will Valve expose Machine package IDs through public `packagedetails`, `appdetails.packages`, package groups, reservation text, or purchase eligibility?
- Are the `fremont-hw-support` SteamOS packages related to Steam Machine launch preparation?

## Next Checks

- Watch SteamKit/PICS changenumbers for all watched app and package IDs, with higher frequency over the next 24-48 hours if possible.
- Watch Valve `appdetails` / `packagedetails` for Machine and Frame package or package-group exposure.
- Get one trusted-browser SteamDB package-page baseline for the four Machine package IDs to corroborate the new PICS movement with human-readable history pages.
- Continue normal Komodo, SteamTracking, SteamOS mirror, Valve API, and customs checks.
