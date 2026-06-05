# Steam Hardware Watch Status

Last updated: `2026-06-05`

## Best Current Answer

- `Price`: Steam Controller remains confirmed by official Valve store APIs at `$99.00` in the US. Steam Machine and Steam Frame still have no confirmed public price.
- `Release date`: Steam Controller remains confirmed with release date `May 4, 2026` and package `1558609`. Steam Machine and Steam Frame still only expose broad `Coming soon` / `2026` timing.
- `Same-time launch`: same-day availability for the full trio is ruled out. Steam Controller is public and purchasable; Machine and Frame still have no public package, package group, price, or exact availability. Steam Machine reservation package changenumbers have now moved twice: a multi-package cluster on `2026-05-12`, followed by another bump across all four watched Machine packages on `2026-05-14`. The `2026-06-05` pass found no new watched SteamKit/PICS package/app movement and no Valve public API readiness. SteamTracking advanced to commit `135035494a6bf1156ee33c4a42db1c5dd1939b8a` (`2026-06-05T05:09:38Z`) and includes significant Steam Frame client-beta surface: `WelcomeToSteamFrame`, `skip_steamframe_pairing_dialog`, `controller_steamframe_pair`, `SteamFrameWirelessAdapterDialog`, `k_EAppTestType_SteamFrameCompatibilityReview`, `steamFrameVerifiedApps`, and `LibraryTab_FrameVerified`. This is a real client-readiness signal, but still not a package unlock, price, or launch-date signal. ImportGenius still shows relevant `GAME CONSOLE` shipments to `INGRAM MICRO C/O VALVE CORPORATION` through `2026-05-18`; this remains logistics corroboration, not public launch confirmation.

## Source Snapshot

### Komodo

- Komodo was reachable in the `2026-06-05` pass through the dedicated browser profile.
- Product modified timestamps remain unchanged from `2026-05-28`:
  - Controller: `2026-05-27T16:52:25`
  - Machine: `2026-05-27T16:53:06`
  - Frame: `2026-05-27T16:53:46`
- This was not timestamp-only: all three product JSON records gained WooCommerce product category `961`, exposed as `product_cat-hardware` in `class_list`. Controller now has product categories `[961, 93]`; Machine and Frame now have `[961]`.
- No new Komodo section, media URL, asset exposure, or product timestamp movement appeared on `2026-05-30`. Treat the category addition as a real Komodo catalog-organization signal, not preorder confirmation.
- Visual asset retrieval found `141` candidate assets, retrieved `137`, and left `4` blocked known Komodo URLs for manual retry. No new asset URL was exposed.

### SteamKit / PICS

- SteamKit/PICS is the primary direct Steam metadata source for watched app and package movement.
- Current changenumbers from the `2026-06-05` run:
  - Controller app `4165870`: `35731145`
  - Frame app `4165890`: `35675573`
  - Machine app `4165910`: `35675573`
  - Controller package `1558609`: `35893035`
  - Machine package `1629446`: `35842876`
  - Machine package `1629447`: `35842851`
  - Machine package `1629458`: `35842860`
  - Machine package `1629460`: `35842863`
  - Frame packages `1629484`, `1629486`: `35672606`
- No watched SteamKit/PICS changenumbers moved on `2026-06-05`.
- The latest Controller package signal remains the `2026-05-17` private PICS change on package `1558609`, where `ignorereservationifstockavailable=1` was removed from the package `extended` fields. Public Valve `appdetails` / `packagedetails` still did not change.
- The latest material Machine signal remains the `2026-05-14` follow-up bump across all four watched Steam Machine package IDs, especially because the two watched Steam Frame package IDs did not move.
- Manual package-history context remains important: Steam Controller package `1558609` reportedly had a clustered change pattern plus one later follow-up change roughly two days before Valve's public purchase-timing update appeared. The Machine set now has both the initial multi-package cluster and the later follow-up bump. Treat this as a stronger imminent-preorder heuristic, not confirmation.
- Machine and Frame apps/packages currently require private PICS metadata tokens, but changenumbers are visible and suitable for movement monitoring.
- Raw snapshot: `/Users/sean/Coding/steam-hardware-watch/runs/2026-06-05/api/steamkit/pics-product-info.json`
- Human-readable detail: `/Users/sean/Coding/steam-hardware-watch/runs/2026-06-05/reports/steamkit-pics-detail.md`

### SteamDB

- SteamDB package pages were mostly reachable through the dedicated browser profile on `2026-06-05`; the Controller app page was still challenge-blocked, but the watched package-page snapshot was captured.
- SteamDB package-page baseline:
  - Controller package `1558609`: last record update `15 May 2026 - 16:07:19 UTC`, changenumber `35893035`, details available.
  - Machine packages `1629446`, `1629447`, `1629458`, `1629460`: last record updates clustered on `13 May 2026`, private/existence-only, possible app `4165910:Steam Machine`.
  - Frame packages `1629484`, `1629486`: last record update `5 May 2026 - 18:50:54 UTC`, private/existence-only, possible app `4165890:Steam Frame`.
- SteamDB is now a useful human-readable corroboration layer again, while SteamKit/PICS remains the primary direct metadata source.

### SteamTracking / GameTracking

- SteamTracking now fast-forwards and records source metadata before scanning. The `2026-06-05` pass used commit `135035494a6bf1156ee33c4a42db1c5dd1939b8a` (`2026-06-05T05:09:38Z`); the checkout was freshly restored because `/tmp/SteamTracking-master` had been wiped.
- The corrected hardware signal reporting now creates dedicated Frame and Machine reports before the broad hardware report, so high-signal product-specific client strings are not buried in generic hardware noise.
- Dedicated Steam Machine client signal report now surfaces setup-tour and compatibility lines:
  - `GuidedTour_SteamMachine_Welcome_Title`
  - `GuidedTour_SteamMachine_SendOff_Description`
  - `GuidedTour_SDCard_Title_SteamMachine`
  - Steam Machine compatibility-warning strings
- Dedicated Steam Frame client signal report now surfaces high-signal Frame lines that were previously buried in the broad hardware report:
  - `WelcomeToSteamFrame`
  - `skip_steamframe_pairing_dialog`
  - `controller_steamframe_pair`
  - `Settings_RemotePlay_WifiAPSection`
  - `SteamFrameWirelessAdapterDialog_*`
  - `k_EAppTestType_SteamFrameCompatibilityReview`
  - `steamFrameVerifiedApps`
  - `LibraryTab_FrameVerified`
- The older focused pairing report still contains the known Triton/Ibex controller pairing surface:
  - `ibex_internal`
  - `ibex_external`
  - `PairDongleTritonConnected`
  - `PairDongleTritonDocked`
  - `ShouldTritonPairInOobe`
- Known reservation package-code baseline remains: Machine package IDs `1629446`, `1629447`, `1629458`, `1629460` and Frame package IDs `1629484`, `1629486` first appeared in SteamTracking commit `334bd31a28a0` at `2026-04-28T23:46:34Z`.
- New high-signal client manifest watch target: `steam_client_beta_linuxarm64` first appeared in the local SteamTracking baseline at commit `28f5287` (`2026-05-22T04:56:58Z`) with version `1779139477`.
- Track `steam_client_beta_linuxarm64` and `steam_client_publicbeta_linuxarm64` every run, especially `bins_hardware_linuxarm64`, `bins_linuxarm64`, `steam_linuxarm64`, `runtime_steamrt_linuxarm64`, and `bins_steamrt_linuxarm64`.
- Current ARM64 client manifest baseline in the `2026-06-05` report:
  - `steam_client_beta_linuxarm64`: version `1780371519`; `bins_hardware_linuxarm64.zip.da8814f3cc3788fd3789ce233dd86f107b2b244a`; size `10039405`.
  - `steam_client_publicbeta_linuxarm64`: version `1780620638`; `bins_hardware_linuxarm64.zip.da8814f3cc3788fd3789ce233dd86f107b2b244a`; size `10039405`.
- ARM64 client manifest movement appeared versus the `2026-06-01` baseline, including `bins_linuxarm64`, `steam_linuxarm64`, and public-beta runtime/steamrt blocks. The hardware-specific `bins_hardware_linuxarm64` block did not change.
- The updated SteamTracking checkout did not add a new Machine/Frame reservation package, price, exact availability, or product-publication signal. It did add enough Frame UI/compatibility/pairing surface, plus enough Machine setup/compatibility surface, that the prior `2026-06-05` summary understated product-specific client-beta signals.

### SteamVR Depots

- SteamVR news metadata was saved. The latest public SteamVR news item is `Introducing SteamVR 2.16` from `2026-06-02T18:59:37Z`.
- SteamDB's SteamVR depot page remained blocked by challenge pages, so no fresh depot manifest/build comparison was collected.
- No local SteamVR depot snapshot was available for deeper content scanning.

### SteamOS Package Mirror

- Valve's public SteamOS package mirror was reachable.
- Notable mirror hits still include `fremont-hw-support 20260506.1-1` in `holo-3.8` and `holo-main`.
- `linux-firmware-neptune` and related Jupiter firmware packages moved from `jupiter.20260504.1-1` to `jupiter.20260604.1-1` in `jupiter-3.8` and `jupiter-main`. No direct `Deckard`, `Roy`, `Steam Frame`, `Steam Machine`, ARM/Snapdragon, or new product-specific top-level repo namespace appeared in the default pass.

### Valve Support / Store / CDN

- Official Valve pages and APIs were reachable.
- No Valve public API readiness change appeared on `2026-06-05`.
- Valve API package snapshot:
  - Controller app `4165870`: public, package `1558609`, package group present, `$99.00`.
  - Frame app `4165890`: public app metadata, `Coming soon`, no packages, no package groups, no price.
  - Machine app `4165910`: public app metadata, `Coming soon`, no packages, no package groups, no price.
  - Machine packages `1629446`, `1629447`, `1629458`, `1629460`: `packagedetails success:false`.
  - Frame packages `1629484`, `1629486`: `packagedetails success:false`.
- This remains the cleanest public-readiness baseline. The `2026-05-14` SteamKit/PICS Machine package movement and the corrected SteamTracking guided-tour baseline have not propagated to public `appdetails`, `packagedetails`, packages, package groups, price, or exact timing.

### Customs / Regulatory

- Customs status on `2026-06-05`: partial. ImportInfo automated fetches were blocked, while the existing ImportGenius-backed baseline still showed relevant rows.
- ImportGenius now lists `10` relevant `GAME CONSOLE` rows for `INGRAM MICRO C/O VALVE CORPORATION` from `2026-03-27` through `2026-05-18`.
- No newer customs rows appeared versus the `2026-05-22` / `2026-05-23` / `2026-05-25` ImportGenius baseline.
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
