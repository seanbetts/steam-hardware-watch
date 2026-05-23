# Steam Hardware Watch Status

Last updated: `2026-05-23`

## Best Current Answer

- `Price`: Steam Controller remains confirmed by official Valve store APIs at `$99.00` in the US. Steam Machine and Steam Frame still have no confirmed public price.
- `Release date`: Steam Controller remains confirmed with release date `May 4, 2026` and package `1558609`. Steam Machine and Steam Frame still only expose broad `Coming soon` / `2026` timing.
- `Same-time launch`: same-day availability for the full trio is ruled out. Steam Controller is public and purchasable; Machine and Frame still have no public package, package group, price, or exact availability. Steam Machine reservation package changenumbers have now moved twice: a multi-package cluster on `2026-05-12`, followed by another bump across all four watched Machine packages on `2026-05-14`. ImportGenius now shows continued `GAME CONSOLE` shipments to `INGRAM MICRO C/O VALVE CORPORATION` through `2026-05-18`; this is a stronger logistics corroboration signal, but public Valve APIs still do not expose Machine purchase or reservation readiness.

## Source Snapshot

### Komodo

- Komodo was available again on `2026-05-23` through the dedicated browser fallback after the automated path initially blocked.
- Product modified timestamps captured in this run remain unchanged versus `2026-05-22`:
  - Controller: `2026-05-22T15:28:27`
  - Machine: `2026-04-24T14:32:54`
  - Frame: `2026-04-24T14:33:36`
- Controller changed from `2026-05-15T15:50:21` to `2026-05-22T15:28:27`, but a direct JSON diff versus `2026-05-18` found only `modified` / `modified_gmt` changes. Treat this as timestamp-only until corroborated by visible content, media, store-state movement, or Steam metadata.
- Machine and Frame remain unchanged from their April 24 product timestamps, and their visible Komodo section baseline is still the old wishlist section only.
- Visual asset retrieval found `141` candidate assets, retrieved `136`, and left `5` blocked known Komodo URLs for manual retry.

### SteamKit / PICS

- SteamKit/PICS is the primary direct Steam metadata source for watched app and package movement.
- Current changenumbers from the `2026-05-23` run:
  - Controller app `4165870`: `35731145`
  - Frame app `4165890`: `35675573`
  - Machine app `4165910`: `35675573`
  - Controller package `1558609`: `35893035`
  - Machine package `1629446`: `35842876`
  - Machine package `1629447`: `35842851`
  - Machine package `1629458`: `35842860`
  - Machine package `1629460`: `35842863`
  - Frame packages `1629484`, `1629486`: `35672606`
- No watched SteamKit/PICS changenumbers moved on `2026-05-23`.
- The latest Controller package signal remains the `2026-05-17` private PICS change on package `1558609`, where `ignorereservationifstockavailable=1` was removed from the package `extended` fields. Public Valve `appdetails` / `packagedetails` still did not change.
- The latest material Machine signal remains the `2026-05-14` follow-up bump across all four watched Steam Machine package IDs, especially because the two watched Steam Frame package IDs did not move.
- Manual package-history context remains important: Steam Controller package `1558609` reportedly had a clustered change pattern plus one later follow-up change roughly two days before Valve's public purchase-timing update appeared. The Machine set now has both the initial multi-package cluster and the later follow-up bump. Treat this as a stronger imminent-preorder heuristic, not confirmation.
- Machine and Frame apps/packages currently require private PICS metadata tokens, but changenumbers are visible and suitable for movement monitoring.
- Raw snapshot: `/Users/sean/Coding/steam-hardware-watch/runs/2026-05-23/api/steamkit/pics-product-info.json`
- Human-readable detail: `/Users/sean/Coding/steam-hardware-watch/runs/2026-05-23/reports/steamkit-pics-detail.md`

### SteamDB

- Automated SteamDB access remained blocked on `2026-05-23`.
- The package report is still a structural baseline, not a content baseline: all watched SteamDB package rows are `missing_or_blocked`.
- SteamDB remains useful as corroborating/human-readable metadata once a trusted browser session can pass the challenge, but SteamKit/PICS now covers primary package movement.

### SteamTracking / GameTracking

- Fresh SteamTracking content at commit `5f58a47` (`2026-05-23T04:32:36Z`) still contains the known Triton/Ibex controller pairing surface:
  - `ibex_internal`
  - `ibex_external`
  - `PairDongleTritonConnected`
  - `PairDongleTritonDocked`
  - `ShouldTritonPairInOobe`
- Known reservation package-code baseline remains: Machine package IDs `1629446`, `1629447`, `1629458`, `1629460` and Frame package IDs `1629484`, `1629486` first appeared in SteamTracking commit `334bd31a28a0` at `2026-04-28T23:46:34Z`.
- New high-signal client manifest watch target: `steam_client_beta_linuxarm64` first appeared in the local SteamTracking baseline at commit `28f5287` (`2026-05-22T04:56:58Z`) with version `1779139477`.
- Track `steam_client_beta_linuxarm64` and `steam_client_publicbeta_linuxarm64` every run, especially `bins_hardware_linuxarm64`, `bins_linuxarm64`, `steam_linuxarm64`, `runtime_steamrt_linuxarm64`, and `bins_steamrt_linuxarm64`.
- Current ARM64 client manifest baseline in the `2026-05-23` report:
  - `steam_client_beta_linuxarm64`: version `1779139477`; `bins_hardware_linuxarm64.zip.cc71be587407299a6125bfa9e889b97bf8df7591`; size `7590487`.
  - `steam_client_publicbeta_linuxarm64`: version `1779479049`; `bins_hardware_linuxarm64.zip.da8814f3cc3788fd3789ce233dd86f107b2b244a`; size `10039405`.
- The updated SteamTracking checkout did not add a new Machine/Frame reservation package, price, exact availability, or product-publication signal.

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

- Customs status on `2026-05-23`: partial. ImportInfo automated fetches were blocked, but the ImportGenius importer page fetched and parsed successfully.
- ImportGenius now lists `10` relevant `GAME CONSOLE` rows for `INGRAM MICRO C/O VALVE CORPORATION` from `2026-03-27` through `2026-05-18`.
- No newer customs rows appeared versus the `2026-05-22` ImportGenius baseline.
- Newer rows since the old `2026-04-23` baseline include:
  - `SNHBSHACHI265020`, arrived `2026-05-18`, `42 PKG`, `14353 Kgs`.
  - `SNHBSHACHI264140`, arrived `2026-05-18`, `42 PKG`, `14533 Kgs`.
  - `SNHBSHACHI264031`, arrived `2026-05-08`, `42 PKG`, `12615 Kgs`.
- The prior NBD / ImportGenius context also remains relevant:
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
