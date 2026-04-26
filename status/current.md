# Steam Hardware Watch Status

Last updated: `2026-04-24`

## Best Current Answer

- `Price`: no confirmed public price leak for the new Steam Controller.
- `Release date`: no exact public launch date found.
- `Same-time launch`: not supported by the current evidence. A shared rollout window remains plausible, but the controller looks further along than Steam Machine or Steam Frame.

## Source Snapshot

### Komodo

- `Steam Controller`, `Steam Machine`, and `Steam Frame` are all real published WooCommerce products in a held state:
  - `publish`
  - `product-type-simple`
  - `outofstock`
  - `wishlist-only`
- On `2026-04-24`, Komodo bulk-updated product records for all three hardware lines across currencies.
- Also on `2026-04-24`, Komodo exposed a fresh controller-only section and media rollout with banner, videos, feature art, controls imagery, and a spec image.
- No comparable fresh Machine or Frame section and media rollout was found.

### SteamDB

- The strongest launch-adjacent signal remains the hidden `steam_controller_unboxing_2026` asset first seen on `2026-04-20`.

### SteamTracking / GameTracking

- Valve’s client strings already include controller onboarding, firmware update flow, puck handling, and pairing logic for the new controller ecosystem.

### Valve Support / CDN

- No controller price or date leak has been confirmed from support pages or discoverable docs in the seeded baseline.

### Customs / Regulatory

- Shipment and filing checks remain secondary confirmation sources. No direct price or launch-date confirmation is seeded here.

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
