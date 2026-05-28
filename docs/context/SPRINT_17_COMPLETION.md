# Sprint 17 Completion Context

Date: 2026-05-28

## Sprint

Sprint 17. Accuracy And KPI Dashboards.

## Goal

Make forecast accuracy and business value visible through WAPE, Bias, service level, out-of-stock, overstock, proposal acceptance, manual adjustment effect and business value draft dashboards.

## Completed Functional Scope

- Added KPI API:
  - `GET /kpi/dashboard`
  - `GET /kpi/segments/{segment_id}`
- Added KPI dimensions:
  - network;
  - region;
  - category;
  - store;
  - SKU.
- Added metrics:
  - WAPE;
  - Bias;
  - service level;
  - out-of-stock rate;
  - overstock value;
  - lost sales value;
  - waste value;
  - proposal acceptance rate;
  - manual adjustment effect.

## Business Process Artifacts

- BPMN: `processes/kpi/weekly_kpi_review_process.bpmn20.xml`
- DMN: `processes/kpi/kpi_alert_decision.dmn.xml`
- CMMN: `processes/kpi/kpi_degradation_case.cmmn.xml`

## Business Process Steps

1. System calculates KPI.
2. DMN evaluates alert thresholds.
3. If WAPE/Bias/service level threshold is breached, process creates KPI review task.
4. Process Owner reviews KPI degradation.
5. Corrective action is created and audit trail is retained.

## UI Scope

- Added `Accuracy And KPI Dashboard` section.
- Added network/region/category/SKU filters.
- Added accuracy and business value cards.
- Added trend visual.
- Added KPI drill-down table.
- Added review task panel.

## Verification

- `python -m pytest` -> 134 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- UI screenshot captured:
  - `docs/test-reports/sprint-17-accuracy-kpi-dashboards/screenshots/accuracy-kpi-dashboard.png`

## Test Report

- `docs/test-reports/sprint-17-accuracy-kpi-dashboards/index.html`

## Remaining Plan

The current execution plan contains Sprint 0 through Sprint 36.

After Sprint 17:

- Completed: 18 sprints.
- Remaining: 19 sprints.
- Approximate time remaining: 51%.

## Next Sprint

Sprint 18. Fresh V1.
