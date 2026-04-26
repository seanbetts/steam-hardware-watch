# Evidence Rubric

## Strong

- official page or API record
- SteamDB app, package, depot, or history change
- downloadable media, manuals, or support docs
- public shipment or regulatory filing clearly matching the device

## Medium

- client strings or protobufs describing concrete rollout flows
- hidden sections and media exposed by public site APIs
- product metadata showing real SKUs or rollout state without price or date

## Weak

- CSS class toggles
- generic platform scripts
- reused templates
- stale assets without fresh timestamps
- inference unsupported by product-specific artifacts

## Confidence Labels

- `high`: direct primary evidence, little ambiguity
- `medium`: strong inference from primary artifacts
- `low`: plausible but not confirmed

Use the lowest defensible confidence that matches the evidence.
