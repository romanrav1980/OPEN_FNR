# Sprint 4 Completion Snapshot

Date: 2026-05-28

## Scope Completed

Sprint 4 implemented the Regular Forecast Baseline foundation:

- forecast version and forecast row contracts;
- WAPE and Bias calculation functions;
- forecast version list/latest API;
- forecast rows API;
- BPMN `regular_forecast_run_process`;
- DMN `forecast_publish_eligibility_decision`;
- CMMN `forecast_run_failure_case`;
- PostgreSQL forecast version metadata;
- UI Regular Forecast Baseline section;
- HTML UI/process test report with screenshot.

## API Endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /forecast/versions` | list forecast versions |
| `GET /forecast/versions/latest` | latest forecast version |
| `GET /forecast/versions/{forecast_version}/rows` | forecast rows |

## Test Report

HTML report:

`docs/test-reports/sprint-4-regular-baseline/index.html`

Screenshot:

`docs/test-reports/sprint-4-regular-baseline/screenshots/regular-forecast-baseline.png`

## Verification Results

```text
python -m pytest
38 passed

npm.cmd run build
vite build completed

Playwright screenshot
regular-forecast-baseline.png saved
```

## Known Notes

- Baseline scoring is represented by deterministic sample output and metric functions.
- Physical Spark/Polars batch scoring is not yet implemented.
- UI is read-only and static; API binding and interactive filters are planned for Sprint 5.

## Next Sprint

Sprint 5 should implement Forecast Workbench V1:

- filters by date, store, SKU and category;
- forecast table improvements;
- actual vs forecast chart placeholder;
- API pagination/filtering contract;
- UI E2E report.
