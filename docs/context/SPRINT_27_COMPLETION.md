# Sprint 27 Completion Context

Date: 2026-05-28

## Sprint

Sprint 27: Production Replenishment Scale.

## Completed Scope

- Added industrial replenishment run with 3.6M proposals and 108M projected stock rows.
- Added partitioned proposal view and constraint performance tracking.
- Added bulk approval gate and Replenishment Owner-only bulk action.
- Added async ERP/WMS export package with idempotency key.
- Added proposal retention value for industrial runs.

## Backend Artifacts

- `apps/backend/open_fnr_api/replenishment_scale.py`
- `tests/backend/test_replenishment_scale.py`
- `apps/backend/open_fnr_api/main.py`
- `tests/backend/test_process_engine.py`

## Process Engine Artifacts

- BPMN: `processes/replenishment-scale/industrial_replenishment_process.bpmn20.xml`
- DMN: `processes/replenishment-scale/bulk_auto_approval_decision.dmn.xml`
- CMMN: `processes/replenishment-scale/replenishment_scale_exception_case.cmmn.xml`
- Registered definitions in `apps/backend/open_fnr_api/process_engine.py`.

## Strengthened Business Process Testing

- BPMN test checks projected stock partitions, partitioned proposals, constraint evaluation, bulk approval, exception path, async export and retention.
- DMN test checks manual review for blocked partitions/runtime and auto approval for valid high-volume run.
- CMMN test checks bulk approval block triage, constraint performance review, partition rerun approval and export recovery.
- API tests cover proposal counts, runtime gate, role permissions, saved filter audit and idempotent async export package.

## UI Artifacts

- `apps/frontend/src/main.tsx`
- Production Replenishment Scale section with partition table, bulk actions and exception path.

## Test Report

- HTML report: `docs/test-reports/sprint-27-production-replenishment-scale/index.html`
- Screenshot: `docs/test-reports/sprint-27-production-replenishment-scale/screenshots/production-replenishment-scale.png`

## Verification

- `python -m pytest` -> 220 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- Playwright screenshot captured.

## Remaining Plan

- Completed: 28 of 37 sprint checkpoints.
- Remaining: 9 sprint checkpoints.
- Approximate remaining time share: 24%.

## Next Sprint

Sprint 28: Production Process Governance.
