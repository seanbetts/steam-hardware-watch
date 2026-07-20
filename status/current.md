# Steam Hardware Watch Status

Last updated: `2026-07-20`

## Best Current Answer

- `Price`: Steam Controller remains confirmed by official Valve store APIs at `$99.00` in the US. Steam Machine is confirmed public in the Valve store API, starting at `$1,049.00` in the US and `£879.00` in the UK. Steam Frame still has no confirmed public price.
- `Release date`: Steam Controller remains confirmed with release date `May 4, 2026` and package `1558609`. Steam Machine is confirmed with release date `Jun 30, 2026` in the US API / `30 Jun, 2026` in the UK API. Steam Frame still exposes only `Coming soon`.
- `Same-time launch`: same-day availability for the full trio is ruled out. Steam Controller is public and purchasable, Steam Machine is public with packages/package group/prices/date, and Steam Frame still has no public package, package group, price, or exact availability.
- `2026-07-20 Frame check`: no new Steam Frame launch-readiness movement since the July 16/17 backend package change. Valve still shows Frame app `4165890` as `Coming soon` with no packages, package group, or price; Frame packages `1629484` and `1629486` still return `packagedetails success:false`; SteamKit/PICS changenumbers are unchanged at `37298233` / `37298229`; and SteamDB still shows both Frame packages as `private_exists_only` with `16 July 2026` last-record updates. Komodo Frame is unchanged at `2026-07-03T15:56:30`, while Komodo Machine moved again to `2026-07-20T14:27:32`. SteamTracking source is `7fed97457fb2ad2eee35401ea775e962acc56e59`; `steam_client_beta_linuxarm64` moved to `1784323984`, but `steam_client_publicbeta_linuxarm64` and `bins_hardware_linuxarm64` did not move, and normalized hardware-signal comparison versus `2026-07-17` showed `0` semantic additions/removals. Customs still has no newer relevant rows beyond the `2026-07-15` `VIRTUAL REALITY DEVICES` rows and `2026-07-14` controller row.
- `2026-07-17 Frame check`: Steam Frame has real backend package movement, but not public launch readiness yet. SteamKit/PICS shows Frame packages `1629484` and `1629486` moved from changenumber `35672606` to `37298233` / `37298229`; SteamDB corroborates `16 July 2026 - 03:50:58 UTC` and `16 July 2026 - 03:50:44 UTC` last-record updates, still `private_exists_only`. Valve still shows Frame app `4165890` as `Coming soon` with no packages, package group, or price, and both Frame packages still return `packagedetails success:false`. Komodo Frame is unchanged at `2026-07-03T15:56:30`. Supporting signals also moved: all four Machine packages moved minutes earlier as a comparator cluster; SteamTracking advanced to `24d3ab943a5f6087473115087fbb4435cadca270` with mostly Machine compatibility additions, `steam_client_publicbeta_linuxarm64` moved to `1784145295` while `bins_hardware_linuxarm64` did not change, and customs now includes three `2026-07-15` `VIRTUAL REALITY DEVICES` rows.
- `2026-07-13 Frame check`: no Steam Frame launch-readiness movement in the primary gates. Valve still shows Frame app `4165890` as `Coming soon` with no packages, package groups, or price; Frame packages `1629484` and `1629486` still return `packagedetails success:false`; SteamKit/PICS changenumbers are unchanged; SteamDB still shows both Frame packages as `private_exists_only`; and Komodo Frame remains at `2026-07-03T15:56:30` with only the old wishlist section / old `Frame_BG.png`. SteamTracking stayed at `292afdbd449f44b4988e5c0423d90bf1c564ad7c`, ARM64 beta/publicbeta manifests did not move, and `bins_hardware_linuxarm64` did not change. Supporting logistics: customs now includes a new `2026-07-10` `WIRELESS PC CONTROLLER, XXXXXX` row from `CHENG UEI PRECISION IND. CO LTD` to `VALVE CORPORATION` (`20 PKG`, `6410 Kgs`, BOL `SNHBHKGCHI267009`), which is controller logistics rather than Frame launch readiness.
- `2026-07-11 Frame check`: no Steam Frame launch-readiness movement in the primary gates. Valve still shows Frame app `4165890` as `Coming soon` with no packages, package groups, or price; Frame packages `1629484` and `1629486` still return `packagedetails success:false`; SteamKit/PICS changenumbers are unchanged; SteamDB still shows both Frame packages as `private_exists_only`; and Komodo Frame remains at `2026-07-03T15:56:30` with only the old wishlist section / old `Frame_BG.png`. Supporting signals: a new `2026-07-09` customs row appeared for `HMD+VR CONTROLLER ACCESSORY, XXXXXX` from `CHENG UEI PRECISION IND. CO LTD` to `VALVE CORPORATION` (`9 PKG`, `1656 Kgs`, BOL `SNHBHKGLBG267012`); `steam_client_publicbeta_linuxarm64` moved to `1783717985`, but `bins_hardware_linuxarm64` did not change; and normalized SteamTracking comparison added Steam Machine compatibility UI strings, which looks like Machine software/support polish rather than Frame launch readiness.
- `2026-07-10 Frame check`: Steam Frame still has no public launch-readiness movement in the primary gates. Valve still shows Frame app `4165890` as `Coming soon` with no packages, package groups, or price; Frame packages `1629484` and `1629486` still return `packagedetails success:false`; SteamKit/PICS changenumbers are unchanged; SteamDB still shows both Frame packages as `private_exists_only`; and Komodo Frame remains at `2026-07-03T15:56:30` with only the old wishlist section / old `Frame_BG.png`. Supporting signals did move: SteamTracking advanced to `319a0a9d08aaa4c700914f0224372e41eaf4e29b` and added semantic Steam Frame Wireless Adapter troubleshooting / airplane-mode dialog strings and skip settings; `steam_client_publicbeta_linuxarm64` moved to `1783556394`, but `bins_hardware_linuxarm64` did not change. Customs now includes newer `2026-07-08` and `2026-07-07` rows, including one `VIRTUAL REALITY DEVICES` shipment and multiple `GAME CONSOLE` shipments. Steam Machine app `4165910` and package `1629446` moved in SteamKit/PICS post-launch; treat that as comparator/background unless it later connects to Frame.
- `2026-07-08 Frame check`: no Steam Frame launch-readiness movement in the primary gates. Valve still shows Frame app `4165890` as `Coming soon` with no packages, package groups, or price; Frame packages `1629484` and `1629486` still return `packagedetails success:false`; SteamKit/PICS changenumbers are unchanged; SteamDB still shows both Frame packages as `private_exists_only`; and Komodo Frame remains at `2026-07-03T15:56:30` with only the old wishlist section / old `Frame_BG.png`. Supporting background movement did appear in SteamTracking: source advanced to `5f07ded044d4a83a4d53fa68966b9c978821ae55`, `steam_client_beta_linuxarm64` moved to `1783475136`, and `steam_client_publicbeta_linuxarm64` moved to `1783376539`; however `bins_hardware_linuxarm64` did not change and a normalized SteamTracking hardware-signal diff versus `2026-07-06` had `0` semantic additions/removals. Customs still has no newer relevant rows beyond `2026-07-01`.
- `2026-07-06 Frame check`: no new Steam Frame launch-readiness movement. Valve still shows Frame app `4165890` as `Coming soon` with no packages, package groups, or price; Frame packages `1629484` and `1629486` still return `packagedetails success:false`; SteamKit/PICS changenumbers are unchanged; SteamDB still shows both Frame packages as `private_exists_only` with `5 May 2026 - 18:50:54 UTC` last record updates; and Komodo Frame remains at `2026-07-03T15:56:30` with only the old wishlist section / old `Frame_BG.png`. SteamTracking did not advance from `d7f9e6423a61e5e00dea911fce64233765aca379`, ARM64 manifests did not move, and customs still has no newer relevant rows beyond `2026-07-01`.
- `2026-07-05 Frame check`: no new Steam Frame launch-readiness movement since the July 3 Komodo media/product staging. Valve still shows Frame app `4165890` as `Coming soon` with no packages or package groups, Frame packages `1629484` and `1629486` still return `packagedetails success:false`, SteamKit/PICS changenumbers are unchanged, SteamDB still shows both Frame packages as `private_exists_only`, and Komodo Frame remains at `2026-07-03T15:56:30` with one old wishlist section / old `Frame_BG.png`. SteamTracking source advanced to `d7f9e6423a61e5e00dea911fce64233765aca379` (`2026-07-04T00:48:46Z`), but no new Frame package/API/string launch signal appeared.
- `2026-07-03 Frame check`: Komodo Frame product staging moved and is not timestamp-only: product `modified` moved to `2026-07-03T15:56:30`, `featured_media` changed from `413708` to `456489`, and the product excerpt removed the inline `frameLogo.svg` image. The new featured media is `source_SF_headsetControllers_front_2.jpg`, dated/modified `2026-07-03T15:54:53`. A later same-day recheck still shows no launch: Valve, SteamKit/PICS, and SteamDB show no public Frame package, package group, price, or exact date. SteamTracking publicbeta ARM64 advanced, but `bins_hardware_linuxarm64` did not change. New `2026-07-01` shipment rows include one `VIRTUAL REALITY DEVICES` row and two `GAME CONSOLE` rows.
- `2026-07-01 Frame check`: no public Steam Frame readiness change. Frame app/package rows are unchanged in Valve, SteamKit/PICS, and SteamDB; Komodo Frame timestamp remains `2026-06-29T12:11:28` with unchanged old wishlist section/media; no newer shipment rows appeared. Background movement was limited to Steam Machine app and Steam Controller package metadata.
- `2026-06-29 Frame check`: no public Steam Frame readiness change. Komodo Frame product timestamp moved to `2026-06-29T12:11:28`, but raw JSON diff versus `2026-06-28` showed no content/class/category/tag/field change after excluding `modified` / `modified_gmt`; Frame sections and media also remained unchanged. Valve, SteamKit/PICS, and SteamDB all remain unchanged for Frame app `4165890` and packages `1629484`, `1629486`.
- `2026-06-28 Frame check`: no public Steam Frame readiness change. Valve, SteamKit/PICS, SteamDB, and Komodo all remain unchanged for Frame app `4165890` and packages `1629484`, `1629486`. Newer `2026-06-24` `VIRTUAL REALITY DEVICES` shipment rows appeared, which is useful logistics corroboration but not launch confirmation.
- `2026-06-25 Frame check`: no public Steam Frame readiness change. Valve, SteamKit/PICS, SteamDB, and Komodo all remain unchanged for Frame app `4165890` and packages `1629484`, `1629486`. SteamTracking/ARM64 client manifests moved, but without Frame package/API movement or new semantic Frame strings.

## Source Snapshot

### 2026-07-20 Frame-Focused Pass

- Frame focus report: `/Users/sean/Coding/steam-hardware-watch/runs/2026-07-20/reports/frame-focus.md`
- Run note: `/Users/sean/Coding/steam-hardware-watch/status/runs/2026-07-20.md`
- Valve API:
  - Frame app `4165890`: public metadata only, `Coming soon`, `packages=`, `package_groups=0`, no price.
  - Frame package `1629484`: private, `packagedetails success:false`.
  - Frame package `1629486`: private, `packagedetails success:false`.
- SteamKit/PICS:
  - Frame app `4165890`: changenumber `35675573`, unchanged.
  - Frame package `1629484`: changenumber `37298233`, unchanged from `2026-07-17`, still `private_metadata_token_required`.
  - Frame package `1629486`: changenumber `37298229`, unchanged from `2026-07-17`, still `private_metadata_token_required`.
  - No watched SteamKit/PICS changenumber movement versus the previous report.
- SteamDB:
  - Frame package `1629484`: `16 July 2026 - 03:50:58 UTC`, changenumber `37298233`, still `private_exists_only`.
  - Frame package `1629486`: `16 July 2026 - 03:50:44 UTC`, changenumber `37298229`, still `private_exists_only`.
- Komodo:
  - Frame product timestamp remains `2026-07-03T15:56:30`.
  - No new Frame sections or section media appeared; still one old wishlist section and old `Frame_BG.png`.
  - Machine product timestamp moved to `2026-07-20T14:27:32`; treat as Machine comparator/background unless later tied to Frame.
- SteamTracking:
  - Source checkout is `7fed97457fb2ad2eee35401ea775e962acc56e59` (`2026-07-18T20:04:59Z`), `updated=no` during the run.
  - Normalized hardware-signal comparison versus `2026-07-17` showed `0` semantic additions and `0` removals.
  - `steam_client_beta_linuxarm64` moved from `1783475136` to `1784323984`.
  - `steam_client_publicbeta_linuxarm64` stayed at `1784145295`.
  - `bins_hardware_linuxarm64` did not change in beta or publicbeta.
- SteamVR / SteamOS:
  - SteamVR depot metadata page was challenge-blocked.
  - SteamOS mirror produced no material Frame launch signal.
- Customs:
  - No newer relevant rows appeared beyond the `2026-07-15` `VIRTUAL REALITY DEVICES` rows and the `2026-07-14` `WIRELESS PC CONTROLLER` row already captured on `2026-07-17`.
  - Some ImportInfo source searches failed, so customs status is partial. ImportGenius rows were still captured.

### 2026-07-17 Frame-Focused Pass

- Frame focus report: `/Users/sean/Coding/steam-hardware-watch/runs/2026-07-17/reports/frame-focus.md`
- Run note: `/Users/sean/Coding/steam-hardware-watch/status/runs/2026-07-17.md`
- Valve API:
  - Frame app `4165890`: public metadata only, `Coming soon`, `packages=`, `package_groups=0`, no price.
  - Frame package `1629484`: private, `packagedetails success:false`.
  - Frame package `1629486`: private, `packagedetails success:false`.
- SteamKit/PICS:
  - Frame app `4165890`: changenumber `35675573`, unchanged.
  - Frame package `1629484`: changenumber `35672606` -> `37298233`, still `private_metadata_token_required`.
  - Frame package `1629486`: changenumber `35672606` -> `37298229`, still `private_metadata_token_required`.
  - Machine package comparator cluster also moved: `1629446` -> `37298130`, `1629447` -> `37298138`, `1629458` -> `37298145`, `1629460` -> `37298146`.
- SteamDB:
  - Frame package `1629484`: `16 July 2026 - 03:50:58 UTC`, changenumber `37298233`, still `private_exists_only`.
  - Frame package `1629486`: `16 July 2026 - 03:50:44 UTC`, changenumber `37298229`, still `private_exists_only`.
  - Machine package movement was corroborated at `16 July 2026 - 03:44-03:45 UTC`.
- Komodo:
  - Frame product timestamp remains `2026-07-03T15:56:30`.
  - No new Frame sections or section media appeared; still one old wishlist section and old `Frame_BG.png`.
  - Controller product timestamp moved to `2026-07-13T23:18:06`; Machine product timestamp moved to `2026-07-17T18:23:59`, but Frame did not move.
- SteamTracking:
  - Source advanced from `292afdbd449f44b4988e5c0423d90bf1c564ad7c` to `24d3ab943a5f6087473115087fbb4435cadca270` (`2026-07-17T03:55:21Z`).
  - Normalized hardware-signal comparison versus `2026-07-13` showed `18` semantic additions and `3` removals; the substantive additions were Steam Machine compatibility filter strings, not new Frame launch text.
  - `steam_client_beta_linuxarm64` stayed at `1783475136`.
  - `steam_client_publicbeta_linuxarm64` moved from `1783717985` to `1784145295`.
  - `bins_hardware_linuxarm64` did not change in beta or publicbeta.
- SteamVR / SteamOS:
  - SteamVR depot metadata page was challenge-blocked; public changelog/local-scan outputs produced no new Frame signal.
  - SteamOS mirror showed `jupiter` firmware package updates, treated as Deck/Jupiter background unless later tied to Frame.
- Customs:
  - New `2026-07-15` `VIRTUAL REALITY DEVICES` rows: BOLs `SNHBSHACHI267003`, `SNHBSHACHI267004`, and `SNHBSHALAX267013`, all from `TECH-FRONT (CHONGQING) COMPUTER CO`, `42 PKG`, `6424-6443 Kgs`.
  - New `2026-07-14` `WIRELESS PC CONTROLLER` row: BOL `SNHBHKGLBG267024`, `40 PKG`, `12970 Kgs`.
  - Treat customs as logistics corroboration only.

### 2026-07-13 Frame-Focused Pass

- Frame focus report: `/Users/sean/Coding/steam-hardware-watch/runs/2026-07-13/reports/frame-focus.md`
- Run note: `/Users/sean/Coding/steam-hardware-watch/status/runs/2026-07-13.md`
- Valve API:
  - Frame app `4165890`: public metadata only, `Coming soon`, `packages=`, `package_groups=0`, no price.
  - Frame package `1629484`: private, `packagedetails success:false`.
  - Frame package `1629486`: private, `packagedetails success:false`.
- SteamKit/PICS:
  - Frame app `4165890`: changenumber `35675573`, unchanged.
  - Frame packages `1629484`, `1629486`: changenumber `35672606`, unchanged.
  - No watched SteamKit/PICS changenumber movement versus the previous report.
- SteamDB:
  - Frame packages `1629484`, `1629486`: still `private_exists_only`, last record update `5 May 2026 - 18:50:54 UTC`, changenumber `35672606`.
  - SteamDB was not blocked for the watched package rows in this run.
- Komodo:
  - Frame product timestamp remains `2026-07-03T15:56:30`.
  - No new Frame sections or section media appeared; still one old wishlist section and old `Frame_BG.png`.
- SteamTracking:
  - Used restored shallow checkout `/tmp/SteamTracking-shallow-20260713`.
  - Source stayed at `292afdbd449f44b4988e5c0423d90bf1c564ad7c` (`2026-07-10T22:51:13Z`), `updated=no`.
  - `steam_client_beta_linuxarm64` stayed at `1783475136`.
  - `steam_client_publicbeta_linuxarm64` stayed at `1783717985`.
  - `bins_hardware_linuxarm64` did not change in beta or publicbeta.
- SteamVR / SteamOS:
  - SteamVR depot metadata page was challenge-blocked, but public changelog/local-scan outputs produced no new Frame signal.
  - SteamOS mirror watch rows remained unchanged for the tracked hardware packages.
- Customs:
  - New row: `2026-07-10` `VALVE CORPORATION` from `CHENG UEI PRECISION IND. CO LTD`, `WIRELESS PC CONTROLLER, XXXXXX`, `20 PKG`, `6410 Kgs`, BOL `SNHBHKGCHI267009`.
  - Prior `2026-07-09` `HMD+VR CONTROLLER ACCESSORY` and `2026-07-08` `VIRTUAL REALITY DEVICES` rows remain in the latest captured table. Treat customs as logistics corroboration only.

### 2026-07-11 Frame-Focused Pass

- Frame focus report: `/Users/sean/Coding/steam-hardware-watch/runs/2026-07-11/reports/frame-focus.md`
- Run note: `/Users/sean/Coding/steam-hardware-watch/status/runs/2026-07-11.md`
- Valve API:
  - Frame app `4165890`: public metadata only, `Coming soon`, `packages=`, `package_groups=0`, no price.
  - Frame package `1629484`: private, `packagedetails success:false`.
  - Frame package `1629486`: private, `packagedetails success:false`.
- SteamKit/PICS:
  - Frame app `4165890`: changenumber `35675573`, unchanged.
  - Frame packages `1629484`, `1629486`: changenumber `35672606`, unchanged.
  - No watched SteamKit/PICS changenumber movement versus the previous report.
- SteamDB:
  - Frame packages `1629484`, `1629486`: still `private_exists_only`, last record update `5 May 2026 - 18:50:54 UTC`, changenumber `35672606`.
  - Controller app page was challenge-blocked, but the watched reservation-package table was captured.
- Komodo:
  - Frame product timestamp remains `2026-07-03T15:56:30`.
  - No new Frame sections or section media appeared; still one old wishlist section and old `Frame_BG.png`.
- SteamTracking:
  - Source advanced from `319a0a9d08aaa4c700914f0224372e41eaf4e29b` to `292afdbd449f44b4988e5c0423d90bf1c564ad7c` (`2026-07-10T22:51:13Z`).
  - Normalized hardware-signal comparison versus `2026-07-10` showed `22` semantic additions and `0` removals, all for Steam Machine compatibility UI strings such as `SteamMachine_CompatibilitySection_Title`, `SteamMachine_CompatibilitySection_Details`, and `SteamMachineVerified_DescriptionHeader_*`.
  - `steam_client_beta_linuxarm64` stayed at `1783475136`.
  - `steam_client_publicbeta_linuxarm64` moved from `1783556394` to `1783717985`.
  - `bins_hardware_linuxarm64` did not change in beta or publicbeta.
- Customs:
  - New row: `2026-07-09` `VALVE CORPORATION` from `CHENG UEI PRECISION IND. CO LTD`, `HMD+VR CONTROLLER ACCESSORY, XXXXXX`, `9 PKG`, `1656 Kgs`, BOL `SNHBHKGLBG267012`.
  - The July 8 `VIRTUAL REALITY DEVICES` row and July 7-8 `GAME CONSOLE` rows remain in the latest captured table. Treat customs as logistics corroboration only.

### 2026-07-10 Frame-Focused Pass

- Frame focus report: `/Users/sean/Coding/steam-hardware-watch/runs/2026-07-10/reports/frame-focus.md`
- Run note: `/Users/sean/Coding/steam-hardware-watch/status/runs/2026-07-10.md`
- Valve API:
  - Frame app `4165890`: public metadata only, `Coming soon`, `packages=`, `package_groups=0`, no price.
  - Frame package `1629484`: private, `packagedetails success:false`.
  - Frame package `1629486`: private, `packagedetails success:false`.
- SteamKit/PICS:
  - Frame app `4165890`: changenumber `35675573`, unchanged.
  - Frame packages `1629484`, `1629486`: changenumber `35672606`, unchanged.
  - Background comparator movement: Machine app `4165910` moved from `36924026` to `37155792`; Machine package `1629446` moved from `36887709` to `37129417`.
- SteamDB:
  - Frame packages `1629484`, `1629486`: still `private_exists_only`, last record update `5 May 2026 - 18:50:54 UTC`.
  - Machine package `1629446` corroborates the post-launch movement with last record update `8 July 2026 - 22:51:58 UTC`, changenumber `37129417`.
- Komodo:
  - Frame product timestamp remains `2026-07-03T15:56:30`.
  - No new Frame sections or section media appeared; still one old wishlist section and old `Frame_BG.png`.
- SteamTracking:
  - Source advanced from `5f07ded044d4a83a4d53fa68966b9c978821ae55` to `319a0a9d08aaa4c700914f0224372e41eaf4e29b` (`2026-07-10T04:44:11Z`).
  - Normalized hardware-signal comparison versus `2026-07-08` showed semantic additions for Steam Frame Wireless Adapter troubleshooting and airplane-mode dialogs, including `SteamFrameWirelessAdapterTroubleshootingDialog_*`, `SteamFrameWirelessAdapterAirplaneDialog_Description`, `skip_steamframe_troubleshooting_dialog`, and `skip_steamframe_airplane_dialog`.
  - `steam_client_beta_linuxarm64` stayed at `1783475136`.
  - `steam_client_publicbeta_linuxarm64` moved from `1783376539` to `1783556394`.
  - `bins_hardware_linuxarm64` did not change in beta or publicbeta.
- Customs:
  - Newer rows appeared beyond `2026-07-01`, including `2026-07-08` `VIRTUAL REALITY DEVICES` shipment `SNHBSHALAX266135` (`42 PKG`, `6457 Kgs`) to `CEVA NL C/O VALVE CORPORATION`.
  - Additional `2026-07-08` and `2026-07-07` `GAME CONSOLE` rows also appeared. Treat customs as logistics corroboration only.

### 2026-07-08 Frame-Focused Pass

- Frame focus report: `/Users/sean/Coding/steam-hardware-watch/runs/2026-07-08/reports/frame-focus.md`
- Run note: `/Users/sean/Coding/steam-hardware-watch/status/runs/2026-07-08.md`
- Valve API:
  - Frame app `4165890`: public metadata only, `Coming soon`, `packages=`, `package_groups=0`, no price.
  - Frame package `1629484`: private, `packagedetails success:false`.
  - Frame package `1629486`: private, `packagedetails success:false`.
- SteamKit/PICS:
  - Frame app `4165890`: changenumber `35675573`, unchanged.
  - Frame packages `1629484`, `1629486`: changenumber `35672606`, unchanged.
- SteamDB:
  - Frame packages `1629484`, `1629486`: still `private_exists_only`, last record update `5 May 2026 - 18:50:54 UTC`.
- Komodo:
  - Frame product timestamp remains `2026-07-03T15:56:30`.
  - No new Frame sections or section media appeared; still one old wishlist section and old `Frame_BG.png`.
- SteamTracking:
  - Source advanced to commit `5f07ded044d4a83a4d53fa68966b9c978821ae55` (`2026-07-08T20:15:39Z`) after restoring the volatile `/tmp/SteamTracking-master` checkout.
  - `steam_client_beta_linuxarm64` moved from `1782442097` to `1783475136`.
  - `steam_client_publicbeta_linuxarm64` moved from `1783028805` to `1783376539`.
  - `bins_hardware_linuxarm64` did not change in beta or publicbeta.
  - A normalized SteamTracking hardware-signal diff versus `2026-07-06` had `0` semantic additions/removals, so the Frame string changes in the raw comparison are line-number churn around existing setup/pairing/compatibility strings.
- Customs:
  - No newer relevant rows appeared beyond the `2026-07-01` VR/game-console rows.

### 2026-07-06 Frame-Focused Pass

- Frame focus report: `/Users/sean/Coding/steam-hardware-watch/runs/2026-07-06/reports/frame-focus.md`
- Run note: `/Users/sean/Coding/steam-hardware-watch/status/runs/2026-07-06.md`
- Valve API:
  - Frame app `4165890`: public metadata only, `Coming soon`, `packages=`, `package_groups=0`, no price.
  - Frame package `1629484`: private, `packagedetails success:false`.
  - Frame package `1629486`: private, `packagedetails success:false`.
- SteamKit/PICS:
  - Frame app `4165890`: changenumber `35675573`, unchanged.
  - Frame packages `1629484`, `1629486`: changenumber `35672606`, unchanged.
- SteamDB:
  - Frame packages `1629484`, `1629486`: still `private_exists_only`, last record update `5 May 2026 - 18:50:54 UTC`.
  - Controller app page was challenge-blocked, but the watched reservation-package table was captured.
- Komodo:
  - Frame product timestamp remains `2026-07-03T15:56:30`.
  - No new Frame sections or section media appeared; still one old wishlist section and old `Frame_BG.png`.
- SteamTracking:
  - Source remained at commit `d7f9e6423a61e5e00dea911fce64233765aca379` (`2026-07-04T00:48:46Z`).
  - `steam_client_beta_linuxarm64` stayed at version `1782442097`.
  - `steam_client_publicbeta_linuxarm64` stayed at version `1783028805`.
  - `bins_hardware_linuxarm64` did not change.
- Customs:
  - No newer relevant rows appeared beyond the `2026-07-01` VR/game-console rows.

### 2026-07-05 Frame-Focused Pass

- Frame focus report: `/Users/sean/Coding/steam-hardware-watch/runs/2026-07-05/reports/frame-focus.md`
- Run note: `/Users/sean/Coding/steam-hardware-watch/status/runs/2026-07-05.md`
- Valve API:
  - Frame app `4165890`: public metadata only, `Coming soon`, `packages=`, `package_groups=0`, no price.
  - Frame package `1629484`: private, `packagedetails success:false`.
  - Frame package `1629486`: private, `packagedetails success:false`.
- SteamKit/PICS:
  - Frame app `4165890`: changenumber `35675573`, unchanged.
  - Frame packages `1629484`, `1629486`: changenumber `35672606`, unchanged.
- SteamDB:
  - Frame packages `1629484`, `1629486`: still `private_exists_only`, last record update `5 May 2026 - 18:50:54 UTC`.
- Komodo:
  - Frame product timestamp remains `2026-07-03T15:56:30`.
  - No new Frame sections or section media appeared; still one old wishlist section and old `Frame_BG.png`.
- SteamTracking:
  - Source updated to commit `d7f9e6423a61e5e00dea911fce64233765aca379` (`2026-07-04T00:48:46Z`) after restoring the volatile `/tmp/SteamTracking-master` checkout.
  - `steam_client_beta_linuxarm64` stayed at version `1782442097`.
  - `steam_client_publicbeta_linuxarm64` stayed at version `1783028805`.
  - `bins_hardware_linuxarm64` did not change.
- Customs:
  - No newer relevant rows appeared beyond the `2026-07-01` VR/game-console rows.

### 2026-07-03 Frame-Focused Pass

- Frame focus report: `/Users/sean/Coding/steam-hardware-watch/runs/2026-07-03/reports/frame-focus.md`
- Run note: `/Users/sean/Coding/steam-hardware-watch/status/runs/2026-07-03.md`
- Valve API:
  - Frame app `4165890`: public metadata only, `Coming soon`, `packages=`, `package_groups=0`, no price.
  - Frame package `1629484`: private, `packagedetails success:false`.
  - Frame package `1629486`: private, `packagedetails success:false`.
- SteamKit/PICS:
  - Frame app `4165890`: changenumber `35675573`, unchanged.
  - Frame packages `1629484`, `1629486`: changenumber `35672606`, unchanged.
- SteamDB:
  - Frame packages `1629484`, `1629486`: still `private_exists_only`, last record update `5 May 2026 - 18:50:54 UTC`.
  - Watched package rows were collected without SteamDB package errors on the later same-day recheck.
- Komodo:
  - Frame product timestamp moved from `2026-06-29T12:11:28` to `2026-07-03T15:56:30`.
  - This was not timestamp-only: `featured_media` changed from `413708` to `456489`, the product excerpt removed the inline `frameLogo.svg` image, and media `456489` is `source_SF_headsetControllers_front_2.jpg`, dated/modified `2026-07-03T15:54:53`.
  - Frame sections remained unchanged: one old `JA - Steam Frame Wishlist` section.
  - Frame section media remained unchanged: old `Frame_BG.png`.
- SteamTracking:
  - Source updated to commit `17c15d162dbb19ea40d0ae757401323edfe2fec8` (`2026-07-02T22:21:06Z`).
  - `steam_client_beta_linuxarm64` did not move from version `1782442097`.
  - `steam_client_publicbeta_linuxarm64` moved from `1782437068` to `1783028805`; `bins_linuxarm64`, `steam_linuxarm64`, and `runtime_steamrt_linuxarm64` changed.
  - `bins_hardware_linuxarm64` did not change, so treat this as ARM64 background movement rather than direct hardware readiness.
- Customs:
  - Newer `2026-07-01` rows appeared: one `VIRTUAL REALITY DEVICES` shipment (`42 PKG`, `6433 Kgs`) and two `GAME CONSOLE` shipments (`42 PKG`, `12541 Kgs` / `12681 Kgs`) from `TECH-FRONT (CHONGQING) COMPUTER CO` to `CEVA C/O VALVE CORPORATION`.
  - Customs data remains logistics corroboration only and does not prove launch timing or final SKU identity.

### 2026-07-01 Frame-Focused Pass

- Frame focus report: `/Users/sean/Coding/steam-hardware-watch/runs/2026-07-01/reports/frame-focus.md`
- Run note: `/Users/sean/Coding/steam-hardware-watch/status/runs/2026-07-01.md`
- Valve API:
  - Frame app `4165890`: public metadata only, `Coming soon`, `packages=`, `package_groups=0`, no price.
  - Frame package `1629484`: private, `packagedetails success:false`.
  - Frame package `1629486`: private, `packagedetails success:false`.
- SteamKit/PICS:
  - Frame app `4165890`: changenumber `35675573`, unchanged.
  - Frame packages `1629484`, `1629486`: changenumber `35672606`, unchanged.
  - Background changes: Machine app `4165910` moved to `36924026`; Controller package `1558609` moved to `36950464`.
- SteamDB:
  - Frame packages `1629484`, `1629486`: still `private_exists_only`, last record update `5 May 2026 - 18:50:54 UTC`.
  - Controller package `1558609` moved to changenumber `36950464`, last record update `30 June 2026 - 23:02:23 UTC`.
- Komodo:
  - Frame product timestamp remains `2026-06-29T12:11:28`.
  - Frame product JSON is unchanged versus `2026-06-29` after excluding `modified` / `modified_gmt`.
  - Frame sections/media remained unchanged: one old wishlist section and old `Frame_BG.png`.
- SteamTracking:
  - Source updated to commit `bc07c53ad22c34f43e2280adb42cbc9d143d5c44` (`2026-07-01T05:15:42Z`).
  - ARM64 client manifest versions did not advance beyond the `2026-06-28` baseline: beta `1782442097`, publicbeta `1782437068`.
  - `bins_hardware_linuxarm64` did not change.
- Customs:
  - No newer rows appeared beyond the `2026-06-24` VR/game-console rows.

### 2026-06-29 Frame-Focused Pass

- Frame focus report: `/Users/sean/Coding/steam-hardware-watch/runs/2026-06-29/reports/frame-focus.md`
- Run note: `/Users/sean/Coding/steam-hardware-watch/status/runs/2026-06-29.md`
- Valve API:
  - Frame app `4165890`: public metadata only, `Coming soon`, `packages=`, `package_groups=0`, no price.
  - Frame package `1629484`: private, `packagedetails success:false`.
  - Frame package `1629486`: private, `packagedetails success:false`.
- SteamKit/PICS:
  - Frame app `4165890`: changenumber `35675573`, unchanged.
  - Frame packages `1629484`, `1629486`: changenumber `35672606`, unchanged.
- SteamDB:
  - Frame packages `1629484`, `1629486`: still `private_exists_only`, last record update `5 May 2026 - 18:50:54 UTC`.
- Komodo:
  - Frame product timestamp moved from `2026-05-27T16:53:46` to `2026-06-29T12:11:28`.
  - Raw Frame product JSON was otherwise identical to `2026-06-28` after excluding `modified` / `modified_gmt`.
  - Frame sections/media remained unchanged: one old wishlist section and old `Frame_BG.png`.
- SteamTracking:
  - Source updated to commit `b6376be5d2fd55efdade6f25f188a66c3306adf1` (`2026-06-28T20:12:17Z`).
  - ARM64 client manifest versions did not advance beyond the `2026-06-28` baseline: beta `1782442097`, publicbeta `1782437068`.
  - `bins_hardware_linuxarm64` did not change.
- Customs:
  - No newer rows appeared beyond the `2026-06-24` VR/game-console rows.

### 2026-06-28 Frame-Focused Pass

- Frame focus report: `/Users/sean/Coding/steam-hardware-watch/runs/2026-06-28/reports/frame-focus.md`
- Run note: `/Users/sean/Coding/steam-hardware-watch/status/runs/2026-06-28.md`
- Valve API:
  - Frame app `4165890`: public metadata only, `Coming soon`, `packages=`, `package_groups=0`, no price.
  - Frame package `1629484`: private, `packagedetails success:false`.
  - Frame package `1629486`: private, `packagedetails success:false`.
- SteamKit/PICS:
  - Frame app `4165890`: changenumber `35675573`, unchanged.
  - Frame packages `1629484`, `1629486`: changenumber `35672606`, unchanged.
  - Machine packages `1629446`, `1629447`, `1629458`, `1629460` moved again post-launch to changenumbers `36887709`, `36887708`, `36887710`, `36887712`.
- SteamDB:
  - Frame packages `1629484`, `1629486`: still `private_exists_only`, last record update `5 May 2026 - 18:50:54 UTC`.
  - Machine package movement was corroborated around `27 June 2026 - 22:06 UTC`; treat as post-launch Machine churn unless it later connects to Frame.
- Komodo:
  - Frame product timestamp remains `2026-05-27T16:53:46`.
  - No new Frame sections/media appeared.
- SteamTracking:
  - Source used fresh checkout commit `94700ae06b85d54b262bf6ce8e4607eaca293876` (`2026-06-27T04:43:47Z`) after `/tmp/SteamTracking-master` was found invalid.
  - `steam_client_beta_linuxarm64` moved to version `1782442097`; `steam_client_publicbeta_linuxarm64` moved to version `1782437068`.
  - `bins_hardware_linuxarm64` did not change in beta or publicbeta.
  - Frame string comparison showed line-number churn around existing setup/pairing/compatibility strings, not new launch-readiness content.
- Customs:
  - Newer `2026-06-24` VR rows appeared: four `VIRTUAL REALITY DEVICES` shipments from `TECH-FRONT (CHONGQING) COMPUTER CO` to CEVA / CEVA NL C/O Valve, each `42 PKG`, around `6422-6443 Kgs`.
  - One `2026-06-24` `GAME CONSOLE` row also appeared: `42 PKG`, `12606 Kgs`.
  - These rows are logistics corroboration only; they do not prove launch timing or final SKU identity.

### 2026-06-25 Frame-Focused Pass

- Frame focus report: `/Users/sean/Coding/steam-hardware-watch/runs/2026-06-25/reports/frame-focus.md`
- Run note: `/Users/sean/Coding/steam-hardware-watch/status/runs/2026-06-25.md`
- Valve API:
  - Frame app `4165890`: public metadata only, `Coming soon`, `packages=`, `package_groups=0`, no price.
  - Frame package `1629484`: private, `packagedetails success:false`.
  - Frame package `1629486`: private, `packagedetails success:false`.
- SteamKit/PICS:
  - Frame app `4165890`: changenumber `35675573`, unchanged.
  - Frame packages `1629484`, `1629486`: changenumber `35672606`, unchanged.
- SteamDB:
  - Frame packages `1629484`, `1629486`: still `private_exists_only`, last record update `5 May 2026 - 18:50:54 UTC`.
- Komodo:
  - Frame product timestamp remains `2026-05-27T16:53:46`.
  - No new Frame sections/media appeared.
- SteamTracking:
  - Source updated to commit `8dadd688e7c5b7ec08e73095ebd79afd4fdfee18` (`2026-06-25T02:29:29Z`).
  - `steam_client_beta_linuxarm64` moved to version `1782330129`; `steam_client_publicbeta_linuxarm64` moved to version `1782344391`.
  - `bins_hardware_linuxarm64` did not change in beta or publicbeta.
  - Frame string comparison showed line-number churn around existing setup/pairing/compatibility strings, not new launch-readiness content.
- Customs:
  - No newer rows appeared beyond the existing `2026-06-17` VR/game-console/controller rows.

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
