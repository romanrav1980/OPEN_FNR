# Sprint 7 Completion Snapshot

Date: 2026-05-28

## Scope Completed

Sprint 7 implemented Promo Data Model and Validation:

- promo plan contract;
- mandatory fields: SKU, stores, dates, mechanic, regular price, promo price, discount, display location, display capacity;
- promo status model;
- promo validation API;
- overlap detection;
- BPMN `promo_draft_validation_process`;
- DMN `promo_completeness_decision`;
- DMN `promo_overlap_decision`;
- CMMN `promo_data_issue_case`;
- UI Promo Workbench Draft;
- HTML UI/process test report with screenshot.

## Business Process Focus

The promo lifecycle now has an explicit validation path:

1. Promo Planner saves draft promo.
2. System validates required fields.
3. System checks overlap by SKU, store and date interval.
4. Valid promo moves to `ready_for_forecast`.
5. Invalid or conflicting promo creates a promo data issue case.
6. Promo Planner fixes fields or overlap.
7. Category Manager approves correction when needed.

## UI Focus

The UI now shows:

- promo id;
- status;
- SKU;
- stores;
- promo dates;
- discount;
- promo price;
- display location;
- display capacity units;
- ready/conflict state.

## Verification Results

```text
python -m pytest
58 passed

npm.cmd run build
vite build completed

Playwright screenshot
promo-workbench-draft.png saved
```

## Test Report

`docs/test-reports/sprint-7-promo-data-validation/index.html`

## Known Notes

- Sprint 7 implements promo contracts, validation and read-only UI.
- Create/edit form persistence is not yet implemented.
- Promo uplift calculation starts in Sprint 8.

## Next Sprint

Sprint 8 should implement Promo Uplift Forecast V1:

- regular baseline on promo period;
- uplift forecast contract;
- total forecast = regular + uplift;
- reference promo comparison;
- promo forecast UI;
- process status `forecasted`.
