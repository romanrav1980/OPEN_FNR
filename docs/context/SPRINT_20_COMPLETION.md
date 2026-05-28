# Sprint 20 Completion Context

Date: 2026-05-28

## Sprint

Sprint 20: Multi-Echelon V1.

## Completed Scope

- Connected store demand aggregation, DC available stock, DC shortage and allocation preview.
- Added explainable priority allocation based on store priority and service risk.
- Added RBAC-protected DC allocation approval for `Supply Chain Manager`.
- Added region/DC object-level access guard.

## Backend Artifacts

- `apps/backend/open_fnr_api/multi_echelon.py`
- `tests/backend/test_multi_echelon.py`
- `apps/backend/open_fnr_api/main.py`
- `tests/backend/test_process_engine.py`

## Process Engine Artifacts

- BPMN: `processes/multi-echelon/dc_replenishment_process.bpmn20.xml`
- DMN: `processes/multi-echelon/dc_allocation_priority_decision.dmn.xml`
- CMMN: `processes/multi-echelon/dc_shortage_case.cmmn.xml`
- Registered definitions in `apps/backend/open_fnr_api/process_engine.py`.

## Strengthened Business Process Testing

- BPMN test checks aggregation, stock loading, shortage calculation, allocation decision, shortage review task, approval path and end state.
- DMN test checks explainable outputs `allocation_priority` and `rule`, plus priority rule IDs.
- CMMN test checks full shortage case lifecycle: review shortage, approve allocation rule, notify affected stores and confirm store order cutoff.
- API tests cover data equality, shortage math, allocation explainability, RBAC, object-level DC scope and approval audit trail.

## UI Artifacts

- `apps/frontend/src/main.tsx`
- Supply Chain Dashboard with DC demand, shortage event, DC plan table, DC -> store drill-down and user actions.

## Test Report

- HTML report: `docs/test-reports/sprint-20-multi-echelon-v1/index.html`
- Screenshot: `docs/test-reports/sprint-20-multi-echelon-v1/screenshots/supply-chain-dashboard.png`

## Verification

- `python -m pytest` -> 161 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- Playwright screenshot captured.

## Remaining Plan

- Completed: 21 of 37 sprint checkpoints.
- Remaining: 16 sprint checkpoints.
- Approximate remaining time share: 43%.

## Next Sprint

Sprint 21: Performance Gate 1.
