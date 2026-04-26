# Steam Hardware Watch Status

Last updated: `2026-04-26`

## Best Current Answer

- `Price`: no confirmed public price leak for the new Steam Controller, Steam Machine, or Steam Frame.
- `Release date`: official Valve store pages now support a broad `early 2026` / `coming in 2026` window, but no exact preorder, ship, or launch date was found.
- `Same-time launch`: stronger than the seeded baseline for a shared public rollout window because Valve's official Steam Hardware page groups Controller, Machine, and Frame together. Exact same-day availability is still unconfirmed, and the controller remains furthest along.

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
- Rechecked on `2026-04-26`: product modified timestamps remain `2026-04-24T15:12:12` for Controller, `2026-04-24T14:32:54` for Machine, and `2026-04-24T14:33:36` for Frame.
- No comparable fresh Machine or Frame section and media rollout was found. Machine and Frame still only show older wishlist sections in the current Komodo search output.

### SteamDB

- Browser-verified SteamDB state on `2026-04-26`:
  - `Steam Controller` app `4165870` remains `prerelease` with store release date `Coming soon`.
  - `steam_controller_unboxing_2026` app `4653940` remains a released free video app, first seen on `2026-04-20`, with package `1620489` available as free on demand and showing `No Price`.
  - The standard curl helper was blocked by SteamDB, so browser-style verification is the current usable path.

### SteamTracking / GameTracking

- A fresh SteamTracking checkout on `2026-04-26` still includes controller onboarding, firmware update flow, puck handling, and pairing logic for the new controller ecosystem.
- Pairing-focused hits include `ibex_internal`, `ibex_external`, `PairDongleTritonConnected`, `PairDongleTritonDocked`, and `ShouldTritonPairInOobe`.

### Valve Support / CDN

- Official Valve store pages were reachable and saved:
  - `/sale/hardware` says the Steam Hardware family expands in early 2026, lists Steam Controller, Steam Machine, and Steam Frame, and was modified at `2026-04-26T06:06:01Z` in the embedded event metadata.
  - `/sale/steamcontroller` has a dedicated Steam Controller page and was modified at `2026-04-26T06:05:47Z` in the embedded event metadata.
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
