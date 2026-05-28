# Sprint 15 Completion Context

Date: 2026-05-28

## Sprint

Sprint 15. Manual Adjustments Framework.

## Goal

Create a safe adjustment overlay layer for forecast, promo and order proposal changes with reason codes, validity period, scope, preview impact, apply/cancel actions and audit.

## Completed Functional Scope

- Added Manual Adjustments API:
  - `GET /adjustments`
  - `GET /adjustments/{adjustment_id}`
  - `GET /adjustments/{adjustment_id}/preview`
  - `POST /adjustments/{adjustment_id}/{action}`
  - `GET /adjustments/{adjustment_id}/audit`
- Added adjustment concepts:
  - target type;
  - target id;
  - reason code;
  - reason comment;
  - scope;
  - validity period;
  - percent/absolute mode;
  - preview impact;
  - approval required decision;
  - audit old/new values.

## Business Process Artifacts

- BPMN: `processes/adjustments/manual_adjustment_process.bpmn20.xml`
- DMN: `processes/adjustments/adjustment_approval_required_decision.dmn.xml`
- CMMN: `processes/adjustments/adjustment_dispute_case.cmmn.xml`

## Business Process Steps

1. Planner creates an adjustment request.
2. System validates scope and validity dates.
3. System previews adjustment impact.
4. DMN decides if approval is required.
5. Approver approves when threshold is exceeded.
6. System applies adjustment as overlay.
7. Original ML forecast or order proposal remains unchanged.
8. System writes audit event with old/new values.

## UI Scope

- Added `Manual Adjustments` section.
- Added adjustment modal-style summary.
- Added reason and validity display.
- Added impact preview.
- Added adjustments table.
- Added action panel.
- Added audit timeline.

## Verification

- `python -m pytest` -> 117 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- UI screenshot captured:
  - `docs/test-reports/sprint-15-manual-adjustments/screenshots/manual-adjustments.png`

## Test Report

- `docs/test-reports/sprint-15-manual-adjustments/index.html`

## Remaining Plan

The current execution plan contains Sprint 0 through Sprint 36.

After Sprint 15:

- Completed: 16 sprints.
- Remaining: 21 sprints.
- Approximate time remaining: 57%.

## Next Sprint

Sprint 16. Publication And Export V1.
