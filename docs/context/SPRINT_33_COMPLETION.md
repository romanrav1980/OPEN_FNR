# Sprint 33 Completion - Capacity And Workload

Date: 2026-05-28

## Completed Scope

- Added DC, transport and store receiving capacity planning slice.
- Added capacity overload detection and smoothing preview.
- Added affected order movement preview with priority-based order shifts.
- Added approval endpoint with role check and audit reason.
- Added idempotent TMS capacity export mock.
- Added Capacity Workbench UI section.
- Added BPMN, DMN and CMMN artifacts for OPEN FNR Process Engine.
- Added HTML presentation-style report with screenshot evidence.

## Artifacts

- API: `apps/backend/open_fnr_api/capacity.py`
- Process registry: `apps/backend/open_fnr_api/process_engine.py`
- BPMN: `processes/capacity/capacity_smoothing_process.bpmn20.xml`
- DMN: `processes/capacity/capacity_overload_decision.dmn.xml`
- DMN: `processes/capacity/order_shift_priority_decision.dmn.xml`
- CMMN: `processes/capacity/capacity_overload_case.cmmn.xml`
- Backend tests: `tests/backend/test_capacity.py`
- Process artifact tests: `tests/process/test_bpmn_artifacts.py`, `tests/process/test_decision_and_case_artifacts.py`
- UI: `apps/frontend/src/main.tsx`
- Test report: `docs/test-reports/sprint-33-capacity-workload/index.html`
- Screenshot: `docs/test-reports/sprint-33-capacity-workload/screenshots/capacity-workbench.png`

## Strengthened Tests

- Capacity overload helper test.
- Smoothing preview API test.
- Approval RBAC and audit test.
- TMS export idempotency test.
- Process registry visibility test.
- BPMN parse and required step coverage test.
- DMN decision table parse tests.
- CMMN lifecycle task coverage test.
- Frontend production build test.
- Playwright screenshot evidence capture.

## Verification

- `python -m pytest` -> 267 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- `npx.cmd playwright screenshot` -> screenshot captured.

## Remaining Plan

- Completed sprint checkpoints: 34 of 37.
- Remaining sprint checkpoints: 3.
- Approximate remaining time share: 8%.
- Next sprint: Sprint 34 - Supply Chain Diagnostics.
