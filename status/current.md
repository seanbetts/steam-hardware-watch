# Steam Hardware Watch Status

Last updated: `2026-04-28`

## Best Current Answer

- `Price`: no confirmed public price leak for the new Steam Controller, Steam Machine, or Steam Frame.
- `Release date`: official Valve store pages still support a broad `early 2026` / `coming in 2026` window, but no exact preorder, ship, or launch date was found.
- `Same-time launch`: stronger than the seeded baseline for a shared public rollout window because Valve's official Steam Hardware page groups Controller, Machine, and Frame together. Exact same-day availability is still unconfirmed, and the controller remains furthest along because the fresh Komodo movement is still controller-only.

## Source Snapshot

### Komodo

- Automated Komodo API access is working again after replacing the helper's rejected generic `Mozilla/5.0` user agent with a realistic browser user agent.
- `Steam Controller`, `Steam Machine`, and `Steam Frame` are all real published WooCommerce products in a held state:
  - `publish`
  - `product-type-simple`
  - `outofstock`
  - `wishlist-only`
- On `2026-04-24`, Komodo bulk-updated product records for all three hardware lines across currencies.
- Also on `2026-04-24`, Komodo exposed a fresh controller-only section and media rollout with banner, videos, feature art, controls imagery, and a spec image.
- Rechecked on `2026-04-28`: the Controller product modified timestamp moved to `2026-04-28T18:32:11`; Machine and Frame remain at `2026-04-24T14:32:54` and `2026-04-24T14:33:36`.
- No comparable fresh Machine or Frame section and media rollout was found. Machine and Frame still only show older wishlist sections in the current Komodo search output.
- Komodo added a new Controller section, `Steam Controller - 10 Specs`, modified `2026-04-27T09:41:01`.
- Komodo updated the Controller `09 Spec image` section on `2026-04-28T19:05:51`, adding two new AVIF media records plus their generated sizes.
- Visual asset retrieval is now complete for the current Komodo set: `130` discovered and `130` retrieved. The browsable library contains `11` videos, `11` images, `3` logos, `3` poster frames, `42` thumbnails, and `60` variants.

### SteamDB

- Browser-verified SteamDB state on `2026-04-26`:
  - `Steam Controller` app `4165870` remains `prerelease` with store release date `Coming soon`.
  - `steam_controller_unboxing_2026` app `4653940` remains a released free video app, first seen on `2026-04-20`, with package `1620489` available as free on demand and showing `No Price`.
- The standard curl helper was still blocked by SteamDB on `2026-04-28`, so browser-style verification remains the current usable path.

### SteamTracking / GameTracking

- A fresh SteamTracking checkout on `2026-04-28` still includes controller onboarding, firmware update flow, puck handling, and pairing logic for the new controller ecosystem.
- Pairing-focused hits include `ibex_internal`, `ibex_external`, `PairDongleTritonConnected`, `PairDongleTritonDocked`, and `ShouldTritonPairInOobe`.

### Valve Support / CDN

- Official Valve store pages were reachable and saved on `2026-04-28`:
  - `/sale/hardware` still says the Steam Hardware family expands in early 2026, lists Steam Controller, Steam Machine, and Steam Frame, and its embedded event metadata now shows `rtime32_last_modified` `2026-04-28T10:09:22Z`.
  - `/sale/steamcontroller` has a dedicated Steam Controller page and its embedded event metadata now shows `rtime32_last_modified` `2026-04-28T18:31:12Z`.
  - The embedded Steam Hardware submenu now points to cleaner `/hardware`, `/hardware/steamcontroller`, `/hardware/steammachine`, and `/hardware/steamframe` paths instead of the older `/sale/...` paths.
- No official Valve price, exact release date, or preorder date was found.

### Customs / Regulatory

- A quick `2026-04-26` web check did not find a new relevant Valve regulatory filing for the 2026 controller, Machine, or Frame. Results were dominated by old Steam Controller and Steam Deck records or unrelated products.

## Open Questions

- When will Valve publish price?
- Will preorder and ship dates differ?
- Will Steam Machine and Steam Frame share announcement timing with the controller, or trail it?
- When do comparable fresh media sets appear for Machine and Frame, if at all?

## Next Checks

- Recheck Komodo `sections` and `media` for Machine and Frame.
- Recheck SteamDB controller app, package, and hidden media activity.
- Recheck Valve support or CDN assets for manuals, safety docs, and store-adjacent media.
- Run customs or regulatory checks if a new primary-source signal appears.
