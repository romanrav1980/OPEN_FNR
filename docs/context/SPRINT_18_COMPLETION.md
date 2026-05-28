# Sprint 18 Completion Context

Date: 2026-05-28

## Sprint

Sprint 18. Fresh V1.

## Goal

Add basic fresh and shelf-life support with batches, FEFO, expected waste, fresh projected stock, spoilage risk and Fresh Workbench.

## Completed Functional Scope

- Added fresh models:
  - batch;
  - shelf-life;
  - fresh projection day;
  - spoilage risk;
  - fresh workbench item.
- Added endpoints:
  - `GET /replenishment/fresh/workbench`
  - `GET /replenishment/fresh/workbench/{item_id}`
- Added helper logic:
  - FEFO ordering;
  - expected waste estimation;
  - spoilage risk classification.

## Business Process Artifacts

- BPMN: `processes/fresh/fresh_order_review_process.bpmn20.xml`
- DMN: `processes/fresh/fresh_spoilage_risk_decision.dmn.xml`
- CMMN: `processes/fresh/high_spoilage_risk_case.cmmn.xml`

## Business Process Steps

1. Fresh projection is calculated.
2. System loads FEFO batches.
3. System estimates expected waste.
4. DMN decides spoilage risk.
5. High spoilage risk opens CMMN case.
6. Fresh Manager adjusts order quantity.
7. System shows waste-service trade-off before approval.

## UI Scope

- Added `Fresh Workbench` section.
- Added fresh SKU summary.
- Added waste-service trade-off card.
- Added expected waste chart.
- Added batch/shelf-life table.
- Added projection table.
- Added fresh adjustment action panel.

## Verification

- `python -m pytest` -> 140 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- UI screenshot captured:
  - `docs/test-reports/sprint-18-fresh-v1/screenshots/fresh-workbench.png`

## Test Report

- `docs/test-reports/sprint-18-fresh-v1/index.html`

## Remaining Plan

The current execution plan contains Sprint 0 through Sprint 36.

After Sprint 18:

- Completed: 19 sprints.
- Remaining: 18 sprints.
- Approximate time remaining: 49%.

## Next Sprint

Sprint 19. Lifecycle SKU V1.
