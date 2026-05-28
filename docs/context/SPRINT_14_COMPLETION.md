# Sprint 14 Completion Context

Date: 2026-05-28

## Sprint

Sprint 14. Exception Center V1.

## Goal

Create a unified Exception Center for stock-out risk, overstock risk, promo shortage risk, supplier constraints, data quality incidents, forecast anomalies and export failures.

## Completed Functional Scope

- Added Exception Center API:
  - `GET /exceptions`
  - `GET /exceptions/{exception_id}`
  - `POST /exceptions/{exception_id}/actions`
  - `GET /exceptions/{exception_id}/audit`
- Added exception model:
  - type;
  - severity;
  - status;
  - owner role;
  - owner user;
  - recommended action;
  - linked objects;
  - SLA due time.
- Added action lifecycle:
  - take;
  - resolve;
  - ignore;
  - escalate.
- Added role guard and audit event for every action.

## Business Process Artifacts

- BPMN: `processes/exceptions/exception_escalation_process.bpmn20.xml`
- DMN: `processes/exceptions/exception_severity_decision.dmn.xml`
- DMN: `processes/exceptions/exception_owner_routing.dmn.xml`
- CMMN: `processes/exceptions/generic_exception_case.cmmn.xml`

## Business Process Steps

1. Exception is created from linked object.
2. DMN decides exception severity.
3. DMN routes exception to owner role.
4. Owner takes exception into review.
5. Owner resolves, ignores or escalates with reason and comment.
6. System writes audit event.
7. Wrong-role action is rejected.

## UI Scope

- Added `Exception Center` section.
- Added filters by type, severity, owner and status.
- Added exception list.
- Added selected exception card.
- Added recommended action card.
- Added linked objects in table.
- Added action panel.
- Added audit table.

## Verification

- `python -m pytest` -> 109 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- UI screenshot captured:
  - `docs/test-reports/sprint-14-exception-center-v1/screenshots/exception-center-v1.png`

## Test Report

- `docs/test-reports/sprint-14-exception-center-v1/index.html`

## Remaining Plan

The current execution plan contains Sprint 0 through Sprint 36.

After Sprint 14:

- Completed: 15 sprints.
- Remaining: 22 sprints.
- Approximate time remaining: 59%.

## Next Sprint

Sprint 15. Manual Adjustments Framework.
