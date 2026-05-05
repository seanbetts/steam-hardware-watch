# Customs Shipment Monitor Design

Date: 2026-05-05

## Context

The current `steam-hardware-watch` workflow treats customs and regulatory sources as confirmation signals, but there is no repeatable shipment helper in `scripts/run_watch.sh`. The existing customs evidence came from a targeted 2026-05-01 pass against NBD and ImportGenius, then was recorded manually in `status/current.md`, `status/runs/2026-05-01.md`, and `status/evidence.jsonl`.

HMRC UK Trade Info was investigated and rejected for this use case. It provides lagged monthly trader/commodity presence, not shipment-level records. It should not be part of the automated monitor unless the goal changes to historical UK commodity-presence analysis.

## Goal

Add a repeatable customs shipment monitor that captures shipment-level or near-shipment-level evidence for Valve hardware logistics, especially `GAME CONSOLE` and controller-related imports tied to Valve, CEVA, Ingram Micro, Tech-Front, and known Valve hardware supply-chain entities.

The monitor should answer:

- Did a new relevant shipment appear since the previous run?
- Which consignee/importer path was used?
- Which supplier shipped it?
- What arrived, when, where, and at what weight/package count?
- Does the pattern materially change launch-readiness confidence?

It should not infer price, exact release date, or product identity from customs data alone.

## Source Strategy

Primary automated source:

- ImportInfo search pages and company pages.

Initial ImportInfo searches:

- `CEVA C/O VALVE CORPORATION`
- `INGRAM MICRO C/O VALVE CORPORATION`
- `TECH-FRONT (CHONGQING) COMPUTER CO` with filtering for `GAME CONSOLE`
- `VALVE CORPORATION` for direct-consignee hardware shipments

Corroborating/manual sources:

- NBD Valve Corporation and Ingram/Valve pages.
- ImportGenius public previews for CEVA/Valve, Ingram/Valve, Tech-Front, and relevant suppliers.
- Paid or sample-only UK/global aggregators only as research leads, not automated dependencies.

Rejected source:

- HMRC UK Trade Info, because it is monthly, lagged, and aggregate-only.

## Artifacts

Each run should save customs outputs under the dated run folder:

- Raw HTML pages under `api/customs/`.
- Extracted machine-readable rows under `reports/customs-shipments.tsv`.
- A concise report under `reports/customs-shipments.md`.
- Summary lines under `reports/customs-shipments-key-lines.txt`.
- Errors or blocked fetches under `reports/customs-shipments-errors.txt`.

The helper should not update `status/current.md` directly. It should produce run artifacts for the agent to review, then material findings can be appended to `status/evidence.jsonl` through the existing evidence workflow.

## Data Model

Extract these fields when available:

- `source`
- `query`
- `run_date`
- `master_bol`
- `house_bol`
- `voyage`
- `bill_type`
- `carrier_code`
- `imo`
- `vessel_name`
- `arrival_date`
- `us_port`
- `foreign_port`
- `quantity`
- `weight`
- `type_of_service`
- `shipper`
- `consignee`
- `notify_party`
- `commodity`
- `source_url`

The stable row identity should be `house_bol` when present, otherwise `master_bol`, otherwise a composite of arrival date, shipper, consignee, quantity, weight, and commodity.

## Filtering

The helper should keep rows that match at least one relevant party and one relevant product/signal.

Relevant parties:

- `VALVE`
- `CEVA`
- `INGRAM MICRO`
- `TECH-FRONT`
- `CHENG UEI`
- known hardware logistics aliases already present in evidence records

Relevant products/signals:

- `GAME CONSOLE`
- `VR CONTROLLER`
- `CONTROLLER`
- `STEAM`
- `BASE STATION`
- `HEADSET`
- `DONGLE`
- future codenames or product names added to `references/sources.md`

The first implementation should be conservative: preserve raw pages even when extraction filters are too narrow, and make filtered-out rows easy to recover by adjusting terms.

## Reporting

`customs-shipments.md` should include:

- At-a-glance counts by source query.
- Newest relevant shipments.
- Rows grouped by consignee/importer path.
- Rows grouped by supplier.
- Out-of-pattern notes, such as package count or weight deviation.
- Known limitations, including public-source ambiguity and non-product-specific `GAME CONSOLE` descriptions.

`customs-shipments-key-lines.txt` should contain short lines suitable for `write_run_summary.py` and `draft_status_update.py`, for example:

```text
2026-05-01	CEVA C/O VALVE CORPORATION	TECH-FRONT (CHONGQING) COMPUTER CO	GAME CONSOLE	42 PKG	12596 Kgs	SNHBSHALAX264015
```

## Integration

Add a new helper script:

- `scripts/check_customs_shipments.sh`

Then integrate it into:

- `scripts/run_watch.sh`
- `scripts/write_run_summary.py`
- `scripts/draft_status_update.py`
- `references/sources.md`
- `SKILL.md`

The runner should execute the customs helper on normal watch runs because ImportInfo is quick and high-signal. If ImportInfo blocks or changes structure, record the failure and let the rest of the watch continue.

## Error Handling

The helper should:

- Save fetch failures to `customs-shipments-errors.txt`.
- Treat HTTP 401/403/429 as blocked source states, not empty evidence.
- Avoid requiring credentials.
- Avoid paid export endpoints.
- Avoid committing cookies, sessions, or local browser profile state.

## Testing

Add focused tests that use a fake `curl` response with ImportInfo-style HTML tables.

Tests should cover:

- Extraction of BOL rows from a search page.
- Filtering to relevant Valve hardware rows.
- Preservation of multiple same-day shipments with different BOLs.
- Graceful blocked-source reporting.

## Evidence Rules

Shipment records are confirmation signals. They can support active logistics and relative rollout readiness, but they do not prove:

- final retail product identity,
- price,
- exact launch date,
- same-day launch timing,
- region-specific consumer availability.

Use `medium` confidence only when a public shipment row clearly ties a relevant party to a relevant product description. Use `low` confidence for masked or aggregate corroboration.
