# Sprint 8 Completion Context

Date: 2026-05-28

## Sprint

Sprint 8. Promo Uplift Forecast V1.

## Goal

Separate regular forecast and promo uplift forecast, calculate total promo demand, and show reference promo logic in the UI and process artifacts.

## Completed Functional Scope

- Added promo forecast API endpoints:
  - `GET /promo/forecasts`
  - `GET /promo/forecasts/{promo_id}`
- Added explicit data model for:
  - regular forecast quantity;
  - promo uplift quantity;
  - total forecast quantity;
  - post-promo projected stock;
  - reference promos and similarity score.
- Added helper formula for total promo forecast:
  - `total_forecast_qty = regular_forecast_qty + promo_uplift_qty`
- Added UI section `Promo Forecast V1` with:
  - promo forecast summary;
  - post-promo stock preview;
  - regular/uplift/total daily chart;
  - forecast day table;
  - reference promo table.

## Business Process Artifacts

- BPMN: `processes/promo/promo_forecast_process.bpmn20.xml`
- DMN: `processes/promo/promo_forecast_quality_decision.dmn.xml`
- CMMN: `processes/promo/promo_forecast_anomaly_case.cmmn.xml`

## Business Process Steps

1. Promo reaches `ready_for_forecast`.
2. Process loads regular forecast baseline for the promo period.
3. Process selects reference promos by similarity.
4. Process calculates promo uplift.
5. Process calculates total forecast as regular forecast plus uplift.
6. DMN evaluates quality gates:
   - uplift accuracy smoke threshold;
   - minimum reference promo count.
7. If quality is acceptable, forecast is published for downstream replenishment.
8. If quality is weak, CMMN case opens manual review:
   - review reference promos;
   - adjust uplift draft;
   - approve promo forecast.

## Data Integration Decision

The factual data integration area was split into a dedicated strategic and technical document:

- `DATA_INTEGRATION_SPEC.md`

It defines loading of factual sales, store stock, DC stock, in-transit goods, open orders, file/API manifests, data quality gates, idempotency, replay and operational SLA.

## Verification

- `python -m pytest` -> 63 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- UI screenshot captured:
  - `docs/test-reports/sprint-8-promo-uplift-forecast/screenshots/promo-forecast-v1.png`

## Test Report

- `docs/test-reports/sprint-8-promo-uplift-forecast/index.html`

## Remaining Plan

The current execution plan contains Sprint 0 through Sprint 36.

After Sprint 8:

- Completed: 9 sprints.
- Remaining: 28 sprints.
- Approximate time remaining: 76%.

## Next Sprint

Sprint 9. Process Engine Foundation.
