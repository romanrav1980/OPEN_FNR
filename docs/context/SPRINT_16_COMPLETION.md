# Sprint 16 Completion Context

Date: 2026-05-28

## Sprint

Sprint 16. Publication And Export V1.

## Goal

Implement controlled publication and export of forecasts and orders to external contours with publication packages, export status, idempotency key, retry and audit.

## Completed Functional Scope

- Added Publication API:
  - `GET /publication/packages`
  - `GET /publication/packages/{package_id}`
  - `POST /publication/packages/{package_id}/send`
  - `POST /publication/packages/{package_id}/retry`
- Added publication concepts:
  - publication package;
  - target system;
  - payload version;
  - idempotency key;
  - export status;
  - retry count;
  - target response code/message;
  - linked export failure exception.
- Added guards:
  - service account required;
  - no export before approval;
  - duplicate export detection by idempotency key;
  - retry only for failed packages.

## Business Process Artifacts

- BPMN: `processes/publication/publication_process.bpmn20.xml`
- DMN: `processes/publication/publication_eligibility_decision.dmn.xml`
- CMMN: `processes/publication/export_failure_case.cmmn.xml`

## Business Process Steps

1. Integration Owner prepares publication package.
2. DMN checks publication eligibility.
3. System rejects unapproved final orders.
4. System checks idempotency key.
5. System sends export to mock ERP/WMS/DWH target.
6. System stores accepted/rejected/failed status.
7. Export failure opens CMMN case and linked exception.
8. Integration Owner retries failed export.

## UI Scope

- Added `Publication Console` section.
- Added package list.
- Added idempotency key and target response display.
- Added retry action panel.
- Added linked exception display.
- Added publication audit table.

## Verification

- `python -m pytest` -> 126 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- UI screenshot captured:
  - `docs/test-reports/sprint-16-publication-export-v1/screenshots/publication-console.png`

## Test Report

- `docs/test-reports/sprint-16-publication-export-v1/index.html`

## Remaining Plan

The current execution plan contains Sprint 0 through Sprint 36.

After Sprint 16:

- Completed: 17 sprints.
- Remaining: 20 sprints.
- Approximate time remaining: 54%.

## Next Sprint

Sprint 17. Accuracy And KPI Dashboards.
