# Sprint 19 Completion Context

Date: 2026-05-28

## Sprint

Sprint 19. Lifecycle SKU V1.

## Goal

Support SKU phase-in, reference product, cold-start fallback, phase-out, termination date, replacement link and clearance risk.

## Completed Functional Scope

- Added SKU lifecycle API:
  - `GET /lifecycle/skus`
  - `GET /lifecycle/skus/{sku_id}`
  - `GET /lifecycle/skus/{sku_id}/order-allowed`
  - `POST /lifecycle/skus/{sku_id}/{action}`
  - `GET /lifecycle/skus/{sku_id}/audit`
- Added lifecycle concepts:
  - planned;
  - active;
  - replacing;
  - phase_out;
  - terminated;
  - reference SKU;
  - replacement SKU;
  - termination date;
  - clearance risk;
  - cold-start forecast.

## Business Process Artifacts

- BPMN: `processes/lifecycle/sku_phase_in_process.bpmn20.xml`
- BPMN: `processes/lifecycle/sku_phase_out_process.bpmn20.xml`
- DMN: `processes/lifecycle/lifecycle_order_allowed_decision.dmn.xml`
- CMMN: `processes/lifecycle/clearance_risk_case.cmmn.xml`

## Strengthened Business Process Tests

- Phase-in process verifies:
  - reference product selection;
  - cold-start forecast calculation;
  - active matrix update;
  - phase-in approval;
  - SKU activation.
- Phase-out process verifies:
  - replacement SKU link;
  - clearance risk evaluation;
  - order block after termination;
  - phase-out approval;
  - SKU termination.
- API tests verify:
  - Category Manager rights;
  - order block after termination date;
  - cold-start fallback;
  - lifecycle audit.

## UI Scope

- Added `SKU Lifecycle` section.
- Added phase-in card.
- Added phase-out card.
- Added lifecycle table.
- Added phase-in form actions.
- Added clearance risk warning/actions.

## Verification

- `python -m pytest` -> 151 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- UI screenshot captured:
  - `docs/test-reports/sprint-19-lifecycle-sku-v1/screenshots/sku-lifecycle.png`

## Test Report

- `docs/test-reports/sprint-19-lifecycle-sku-v1/index.html`

## Remaining Plan

The current execution plan contains Sprint 0 through Sprint 36.

After Sprint 19:

- Completed: 20 sprints.
- Remaining: 17 sprints.
- Approximate time remaining: 46%.

## Next Sprint

Sprint 20. Multi-Echelon V1.
