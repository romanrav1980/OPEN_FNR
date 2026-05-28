# Sprint 10 Completion Context

Date: 2026-05-28

## Sprint

Sprint 10. Promo Approval Process.

## Goal

Implement the first end-to-end promo approval process after promo uplift forecast: category approval, supply approval, risk classification, rework path, reject path, publication readiness and decision audit.

## Completed Functional Scope

- Added promo approval API:
  - `GET /promo/approvals`
  - `GET /promo/approvals/{promo_id}`
- Added promo approval model:
  - status;
  - risk level;
  - risk reasons;
  - approval route;
  - blocking errors;
  - approval steps;
  - publication readiness.
- Added promo risk classifier:
  - low;
  - medium;
  - high.
- Extended Process Engine:
  - promo approval process definitions;
  - category and supply approval tasks;
  - approval/rework/reject event types;
  - actor role validation during task completion.

## Business Process Artifacts

- BPMN: `processes/promo/promo_planning_process.bpmn20.xml`
- DMN: `processes/promo/promo_risk_classification.dmn.xml`
- DMN: `processes/promo/promo_approval_route.dmn.xml`
- CMMN: `processes/promo/promo_shortage_case.cmmn.xml`

## Business Process Steps

1. Promo reaches `forecasted`.
2. BPMN starts `promo_planning_process`.
3. DMN classifies promo risk by discount, uplift and post-promo stock.
4. DMN selects approval route.
5. Category Manager reviews commercial terms.
6. Supply Chain Manager reviews stock and supply readiness.
7. Approver can approve, reject, request rework, comment or escalate.
8. Wrong-role approval is rejected by backend.
9. Blocking errors prevent publication readiness.
10. Every decision requires user/comment/reason and creates audit records.

## UI Scope

- Added `Promo Approval Process` section.
- Added promo card with process instance.
- Added risk card and risk reasons.
- Added decision panel with action buttons from process semantics.
- Added blocking errors panel.
- Added approval steps table.
- Added timeline table.

## Verification

- `python -m pytest` -> 79 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- UI screenshot captured:
  - `docs/test-reports/sprint-10-promo-approval-process/screenshots/promo-approval-process.png`

## Test Report

- `docs/test-reports/sprint-10-promo-approval-process/index.html`

## Remaining Plan

The current execution plan contains Sprint 0 through Sprint 36.

After Sprint 10:

- Completed: 11 sprints.
- Remaining: 26 sprints.
- Approximate time remaining: 70%.

## Next Sprint

Sprint 11. Replenishment Foundation.
