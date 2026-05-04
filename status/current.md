# Steam Hardware Watch Status

Last updated: `2026-05-04`

## Best Current Answer

- `Price`: Steam Controller remains confirmed by official Valve store APIs at `$99.00` in the US. Steam Machine and Steam Frame still have no confirmed public price.
- `Release date`: Steam Controller remains confirmed with release date `May 4, 2026` and package `1558609`. Steam Machine and Steam Frame still only have broad `2026` timing.
- `Same-time launch`: exact same-day availability is effectively ruled out for the full trio. Steam Controller has a purchase package and exact date; Machine and Frame still do not.

## Source Snapshot

### Komodo

- Automated Komodo API access was blocked on `2026-05-04`; do not treat the comparison report's Komodo section removals as real content removals.
- Automated Komodo API access worked on `2026-05-02` with the realistic browser user agent.
- `Steam Controller`, `Steam Machine`, and `Steam Frame` remain real published WooCommerce products.
- Controller product metadata moved again: modified timestamp is now `2026-04-30T19:14:10`.
- Controller remains in the sale-adjacent state seen in the prior run:
  - `product_tag-wishlist-only` is absent.
  - `purchasable` is present.
  - `outofstock` remains.
  - `product_tag` is `[112]`; tag `113` is `wishlist-only`.
- Machine and Frame remain dormant by comparison: both still carry `product_tag-wishlist-only`, remain `outofstock`, and do not have the `purchasable` class.
- Machine and Frame product modified timestamps are unchanged at `2026-04-24T14:32:54` and `2026-04-24T14:33:36`.
- Current Komodo section coverage shows Controller-only launch-page depth, with older wishlist-only sections for Machine and Frame.
- Visual asset retrieval is complete for the current Komodo set: `141` discovered and `141` retrieved, with `0` blocked. The browsable library contains `11` videos, `12` images, `3` logos, `3` poster frames, `44` thumbnails, and `68` variants.

### SteamDB

- The standard SteamDB helper was still blocked by challenge pages on `2026-05-04` for app `4165870`, app history, app `4653940`, and package `1620489`.
- Browser-verified SteamDB state from `2026-04-26` is now superseded for price and date by official Valve store APIs, but remains useful for historical app/package tracking.

### SteamTracking / GameTracking

- A fresh SteamTracking checkout on `2026-05-04` still includes controller onboarding, firmware update flow, puck handling, and pairing logic for the new controller ecosystem.
- Pairing-focused hits include `ibex_internal`, `ibex_external`, `PairDongleTritonConnected`, `PairDongleTritonDocked`, and `ShouldTritonPairInOobe`.
- The same Triton/Ibex pairing surface now also appears in `Random/SteamApkStrings.txt`, indicating the Steam Android APK string dump includes the controller pairing API names. This broadens the client-surface evidence, but does not introduce a new price or launch-date signal.

### SteamVR Depots

- SteamVR app `250820` news metadata was saved on `2026-05-04`.
- The SteamDB depot page for SteamVR was blocked by challenge pages, so no fresh manifest/build comparison was collected.
- The first SteamVR helper baseline found public news references to SteamVR/OpenXR/Steam Link VR, but no direct `Deckard`, `Roy`, or `Steam Frame` depot-content hit because no local SteamVR depot snapshot was available to scan.

### SteamOS Package Mirror

- Valve's public SteamOS package mirror was reachable on `2026-05-04`.
- The default `holo-3.8`, `holo-main`, `jupiter-3.8`, and `jupiter-main` package database pass produced `758` package rows and no fetch errors.
- No high-signal `Fremont`, `Deckard`, `Roy`, `Steam Frame`, `Steam Machine`, ARM/Snapdragon, or product-specific top-level repo namespace appeared in the default mirror pass.
- The notable mirror hits were Deck/Jupiter-adjacent, including `foxnet`, `foxnetstatsd`, `linux-firmware-neptune-*`, and `plasma-remotecontrollers`.

### Valve Support / CDN

- Official Valve store pages were reachable and saved on `2026-05-04`.
- Official appdetails for app `4165870` still show hardware type, package `1558609`, `price_overview.final_formatted` `$99.00`, and release date `May 4, 2026`.
- Official packagedetails for package `1558609` still show USD final price `9900` cents, release date `May 4, 2026`, and page content for the Steam Controller puck, 35+ hour battery, TMR thumbsticks, haptics, and inputs.
- Steam Controller store event metadata moved again to `rtime32_last_modified` `2026-05-04T18:27:52Z`; the Steam Hardware root event moved to `2026-05-04T18:27:56Z`. The announcement body hash was unchanged, so this is metadata/json movement rather than a clear text-body change.
- Steam Machine and Steam Frame still do not have comparable official price or exact purchase timing in the checked Valve artifacts.

### Customs / Regulatory

- No new customs or regulatory pass was run on `2026-05-02`; the latest saved customs evidence remains from `2026-05-01`.
- NBD's public Valve Corporation page showed latest Valve trade data dated `2026-04-04`, including a `WIRELESS PC CONTROLLER` row from `HONG KONG (CHINA)`.
- ImportGenius showed an April 23, 2026 `GAME CONSOLE .` shipment for `INGRAM MICRO C/O VALVE CORPORATION`, but that record does not identify which Valve hardware product.
- These customs records support active Valve hardware logistics, but do not prove price, exact launch date, or device-specific timing for Machine or Frame.

## Open Questions

- When will Valve publish Steam Machine and Steam Frame prices?
- Will Steam Controller ship dates or purchase-state details differ by region after the `May 4, 2026` release date?
- When will Steam Machine and Steam Frame receive exact availability timing?
- When do comparable fresh media and purchasable-state changes appear for Machine and Frame, if at all?

## Next Checks

- Recheck Komodo product classes/tags for Machine and Frame with browser-style fallback if normal API access remains blocked.
- Recheck SteamDB via browser-style access after the official appdetails movement.
- Watch Valve store metadata and `/hardware/...` paths for Machine and Frame price or availability fields.
- Download or point `STEAMVR_SCAN_DIRS` at SteamVR beta depot snapshots for a real depot-content diff.
- Monitor the SteamOS mirror root for new product-specific repos such as possible Machine/Frame namespaces.
- Track NBD and other customs aggregators for follow-on controller shipments and any Machine or Frame descriptions.
- Run customs or regulatory checks if a new primary-source signal appears.
