# Steam Hardware Watch Status

Last updated: `2026-06-22`

## Best Current Answer

- `Price`: Steam Controller remains confirmed by official Valve store APIs at `$99.00` in the US. Steam Machine is now confirmed public in the Valve store API, starting at `$1,049.00` in the US and `£879.00` in the UK. Steam Frame still has no confirmed public price.
- `Release date`: Steam Controller remains confirmed with release date `May 4, 2026` and package `1558609`. Steam Machine is now confirmed with release date `Jun 30, 2026` in the US API / `30 Jun, 2026` in the UK API. Steam Frame still exposes only `Coming soon`.
- `Same-time launch`: same-day availability for the full trio is ruled out. Steam Controller is public and purchasable, Steam Machine is now public with packages/package group/prices/date, and Steam Frame still has no public package, package group, price, or exact availability. The Steam Machine watch correctly caught the launch sequence: multi-package backend movement, same-day Komodo page/media staging, then public Valve API exposure.

## Source Snapshot

### Komodo

- Komodo was unblocked on `2026-06-22` after fixing the trusted-browser Playwright runtime path and rerunning the Komodo section through the dedicated Chrome session.
- Product modified timestamps:
  - Controller: `2026-06-10T17:25:21`
  - Machine: `2026-05-27T16:53:06`
  - Frame: `2026-05-27T16:53:46`
- This was not timestamp-only: all three product JSON records gained WooCommerce product category `961`, exposed as `product_cat-hardware` in `class_list`. Controller now has product categories `[961, 93]`; Machine and Frame now have `[961]`.
- The Controller timestamp moved on `2026-06-10`, but selected content/class/category/product fields matched the `2026-06-09` snapshot, so treat it as timestamp-only unless later corroborated.
- Product modified timestamps still did not move, but the section layer did: eleven new Steam Machine sections appeared with `2026-06-22` dates/modifications:
  - `steam-machine-01-video`
  - `steam-machine-03-video`
  - `steam-machine-04-core-features`
  - `steam-machine-05-video`
  - `steam-machine-06-led-strip`
  - `steam-machine-07-support`
  - `steam-machine-08-pc`
  - `steam-machine-09-pc-video`
  - `steam-machine-10-plays-well`
  - `steam-machine-11-tech-image`
  - `steam-machine-12-tech-spec`
- Komodo section media now includes `26` new `2026-06-22` Steam Machine assets: `7` WEBM videos, multiple PNG/WEBP video-poster assets, and English/Japanese AVIF tech/line-art images. No equivalent new Steam Frame sections appeared.
- Visual asset retrieval found `425` candidate assets, retrieved `400`, and left `25` blocked known Komodo URLs for manual retry. Most blocked rows are known Controller WEBP variants; the new `machine_video5.webp` variants should be retried manually if visual completeness matters.
- Komodo has not yet flipped its product layer: `steam-machine_jpy` still has `product_tag-wishlist-only`, `product_tag-hide-product-top`, and `outofstock`. Treat Komodo as lagging behind Valve's public store API for the actual launch state.

### SteamKit / PICS

- SteamKit/PICS is the primary direct Steam metadata source for watched app and package movement.
- Current changenumbers from the `2026-06-22` run:
  - Controller app `4165870`: `35731145`
  - Frame app `4165890`: `35675573`
  - Machine app `4165910`: `36756875`
  - Controller package `1558609`: `36708367`
  - Machine package `1629446`: `36756963`
  - Machine package `1629447`: `36756942`
  - Machine package `1629458`: `36756957`
  - Machine package `1629460`: `36756953`
  - Frame packages `1629484`, `1629486`: `35672606`
- All four watched Steam Machine packages are now `available` in SteamKit/PICS and contain app `4165910`; watched Steam Frame package changenumbers did not move.
- Steam Controller package `1558609` also moved on `2026-06-22`, from `35893035` to `36708367`, with a new PICS SHA. Public Valve `appdetails` / `packagedetails` still did not change.
- The launch conversion happened in the expected PICS shape: Machine app `4165910` moved, all four watched Machine packages moved again, changed from private-token/existence-only to available package details, and now report `apps_count=1`.
- Manual package-history context remains important: Steam Controller package `1558609` had a clustered change pattern plus a later follow-up before public purchase timing appeared. The Machine set followed a similar pattern, and the final same-day package movements preceded public package availability.
- Frame apps/packages currently still require private PICS metadata tokens or private package rows, but changenumbers remain visible and suitable for movement monitoring.
- Raw snapshot: `/Users/sean/Coding/steam-hardware-watch/runs/2026-06-22/api/steamkit/pics-product-info.json`
- Human-readable detail: `/Users/sean/Coding/steam-hardware-watch/runs/2026-06-22/reports/steamkit-pics-detail.md`

### SteamDB

- SteamDB package pages were still partly challenge-prone on `2026-06-22`, but the watcher collected usable package rows for the watched reservation IDs.
- SteamDB package-page baseline:
  - Controller package `1558609`: last record update `19 June 2026 - 18:38:41 UTC`, changenumber `36708367`, details available.
  - Machine package `1629446`: last record update `22 June 2026 - 16:58:26 UTC`, changenumber `36756963`, details available, app `4165910:Steam Machine`.
  - Machine package `1629447`: last record update `22 June 2026 - 16:57:36 UTC`, changenumber `36756942`, details available, app `4165910:Steam Machine`.
  - Machine package `1629458`: last record update `22 June 2026 - 16:58:14 UTC`, changenumber `36756957`, details available, app `4165910:Steam Machine`.
  - Machine package `1629460`: last record update `22 June 2026 - 16:58:02 UTC`, changenumber `36756953`, details available, app `4165910:Steam Machine`.
  - Frame packages `1629484`, `1629486`: last record update `5 May 2026 - 18:50:54 UTC`, private/existence-only, possible app `4165890:Steam Frame`.
- SteamDB remains a useful human-readable corroboration layer when reachable, while SteamKit/PICS remains the primary direct metadata source.

### SteamTracking / GameTracking

- SteamTracking now fast-forwards and records source metadata before scanning. The `2026-06-22` pass used commit `d8c88a286f382752aa90b7dd5a9aa057db78a077` (`2026-06-19T23:33:59Z`).
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
  - `GuidedTour_FrameAlreadyPairedWith`
  - `GuidedTour_FrameNowPairedWith`
  - `GuidedTour_Frame_SetupComplete`
  - `GuidedTour_SearchingForWirelessAdapter`
  - `GuidedTour_WirelessAdapterDetected`
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
- Current ARM64 client manifest baseline in the `2026-06-22` report:
  - `steam_client_beta_linuxarm64`: version `1781223733`; `bins_hardware_linuxarm64.zip.da8814f3cc3788fd3789ce233dd86f107b2b244a`; size `10039405`.
  - `steam_client_publicbeta_linuxarm64`: version `1781911235`; `bins_hardware_linuxarm64.zip.da8814f3cc3788fd3789ce233dd86f107b2b244a`; size `10039405`.
- ARM64 public beta client manifest movement appeared versus the `2026-06-19` baseline, including `bins_linuxarm64`, `steam_linuxarm64`, `bins_steamrt_linuxarm64`, `bins_misc_linuxarm64`, and `webkit_linuxarm64`. The hardware-specific `bins_hardware_linuxarm64` block did not change.
- The updated SteamTracking checkout did not add a new Machine/Frame reservation package, price, exact availability, or product-publication signal. Content-normalized comparison showed no substantive Machine-specific additions, but did show new/renamed Steam Frame setup-tour and wireless-adapter localization strings.

### SteamVR Depots

- SteamVR news metadata was saved. The latest public SteamVR news item is `Introducing SteamVR 2.16` from `2026-06-02T18:59:37Z`.
- SteamDB's SteamVR depot page remained blocked by challenge pages on `2026-06-22`, so no fresh depot manifest/build comparison was collected.
- No local SteamVR depot snapshot was available for deeper content scanning.

### SteamOS Package Mirror

- Valve's public SteamOS package mirror was reachable.
- Notable mirror hits still include `fremont-hw-support 20260506.1-1` in `holo-3.8` and `holo-main`.
- `jupiter-3.8` Neptune firmware packages moved from `jupiter.20260610.1-1` to `jupiter.20260610.1-1.1`; `jupiter-main` remains at `jupiter.20260610.1-1`. Treat this as SteamOS firmware/package churn unless later tied to a product-specific hardware signal.
- No direct `Deckard`, `Roy`, `Steam Frame`, `Steam Machine`, ARM/Snapdragon, or new product-specific top-level repo namespace appeared in the default pass.

### Valve Support / Store / CDN

- Official Valve pages and APIs were reachable.
- Valve public API readiness changed materially on `2026-06-22`: Steam Machine is now public with packages, a package group, prices, and a release date.
- Valve API package snapshot:
  - Controller app `4165870`: public, package `1558609`, package group present, `$99.00`.
  - Frame app `4165890`: public app metadata, `Coming soon`, no packages, no package groups, no price.
  - Machine app `4165910`: public app metadata, package group present, `coming_soon=False`, release date `Jun 30, 2026`, starting price `$1,049.00` in the US / `£879.00` in the UK.
  - Machine package `1629447`: public, `Steam Machine 512GB`, `$1,049.00` US / `£879.00` UK.
  - Machine package `1629458`: public, `Steam Machine 512GB with Controller`, `$1,128.00` US / `£938.00` UK.
  - Machine package `1629446`: public, `Steam Machine 2TB`, `$1,349.00` US / `£1,149.00` UK.
  - Machine package `1629460`: public, `Steam Machine 2TB with Controller`, `$1,428.00` US / `£1,208.00` UK.
  - Frame packages `1629484`, `1629486`: `packagedetails success:false`.
- This is now the cleanest public-readiness baseline: Steam Machine launch state has propagated to public `appdetails`, `packagedetails`, package group, price, and release date. Steam Frame has not.

### Customs / Regulatory

- Customs status on `2026-06-22`: partial. ImportInfo automated fetches were blocked, while ImportGenius importer pages fetched and parsed.
- The customs watcher now covers ImportGenius importer pages for `INGRAM MICRO C/O VALVE CORPORATION`, `CEVA C/O VALVE CORPORATION`, `CEVA NL C/O VALVE CORPORATION`, and `VALVE CORPORATION`.
- ImportGenius lists `37` relevant Valve-hardware shipment rows in the `2026-06-22` report.
- No newer customs rows appeared versus the `2026-06-19` report.
- Newest high-signal rows:
  - `SNHBSHACHI265222`, arrived `2026-06-17`, `CEVA NL C/O VALVE CORPORATION`, `GAME CONSOLE`, `42 PKG`, `12698 Kgs`.
  - `SNHBSHACHI265217`, arrived `2026-06-17`, `CEVA NL C/O VALVE CORPORATION`, `GAME CONSOLE`, `42 PKG`, `12554 Kgs`.
  - `SNHBSHACHI265224`, arrived `2026-06-17`, `CEVA NL C/O VALVE CORPORATION`, `VIRTUAL REALITY DEVICES`, `42 PKG`, `6464 Kgs`.
  - `SNHBSHALAX265223`, arrived `2026-06-17`, `CEVA NL C/O VALVE CORPORATION`, `VIRTUAL REALITY DEVICES`, `42 PKG`, `6467 Kgs`.
  - `SNHBSHACHI265216`, arrived `2026-06-17`, `CEVA NL C/O VALVE CORPORATION`, `VIRTUAL REALITY DEVICES`, `42 PKG`, `6406 Kgs`.
  - `SNHBHKGLBG266038`, arrived `2026-06-17`, `VALVE CORPORATION`, `WIRELESS PC CONTROLLER`, `40 PKG`, `12970 Kgs`.
  - `SNHBSHACHI265173`, arrived `2026-06-10`, `CEVA C/O VALVE CORPORATION`, `VIRTUAL REALITY DEVICES`, `42 PKG`, `6374 Kgs`.
  - `SNHBSHACHI265174`, arrived `2026-06-10`, `CEVA C/O VALVE CORPORATION`, `VIRTUAL REALITY DEVICES`, `42 PKG`, `6372 Kgs`.
  - `SNHBSHACHI265175`, arrived `2026-06-10`, `CEVA C/O VALVE CORPORATION`, `VIRTUAL REALITY DEVICES`, `42 PKG`, `6392 Kgs`.
  - `SNHBSHACHI265176`, arrived `2026-06-10`, `CEVA C/O VALVE CORPORATION`, `VIRTUAL REALITY DEVICES`, `42 PKG`, `6391 Kgs`.
  - `SNHBSHALAX265177`, arrived `2026-06-10`, `CEVA NL C/O VALVE CORPORATION`, `VIRTUAL REALITY DEVICES`, `42 PKG`, `6400 Kgs`.
  - `SNHBHKGLBG266011`, arrived `2026-06-10`, `VALVE CORPORATION`, `WIRELESS PC CONTROLLER`, `30 PKG`, `9727 Kgs`.
- Additional captured rows include `GAME CONSOLE` arrivals to CEVA/CEVA NL on `2026-06-03`, `2026-05-30`, and `2026-05-20`, plus `WIRELESS PC CONTROLLER` rows on `2026-06-02` and `2026-05-19`.
- The prior NBD / ImportGenius context also remains relevant:
  - `WIRELESS PC CONTROLLER` row dated `2026-04-04`.
  - `GAME CONSOLE` shipment arriving `2026-04-23` for `INGRAM MICRO C/O VALVE CORPORATION`.
- Customs data remains corroborating evidence only, not price/date/product-identity proof.

## Open Questions

- When will Valve publish Steam Frame price/package group/exact availability?
- Will Komodo flip the Steam Machine product layer from wishlist/outofstock to a public buy/reservation state?
- Will Valve expose Frame package IDs through public `packagedetails`, `appdetails.packages`, package groups, reservation text, or purchase eligibility?
- Are the `fremont-hw-support` SteamOS packages related to Steam Machine launch preparation?

## Next Checks

- Watch SteamKit/PICS changenumbers for Frame package IDs and any post-launch Machine package amendments.
- Watch Valve `appdetails` / `packagedetails` for Steam Frame package or package-group exposure, plus any Steam Machine purchase-state/reservation copy changes.
- Keep SteamDB as a corroboration layer for any post-launch Machine package-history changes.
- Continue normal Komodo, SteamTracking, SteamOS mirror, Valve API, and customs checks.
- Keep ImportGenius CEVA / CEVA NL / Valve Corp importer pages in the normal customs rotation and watch for additional `VIRTUAL REALITY DEVICES`, `GAME CONSOLE`, or `WIRELESS PC CONTROLLER` arrivals.
