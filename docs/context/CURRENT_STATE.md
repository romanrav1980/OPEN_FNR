# OPEN FNR Current State

Last updated: 2026-05-28

## Active Work

Sprint 6 implementation is complete.

## Local Infrastructure

Docker Compose development infrastructure is defined in `infra/dev/compose.yaml`.

Known local URLs:

| Service | URL |
| --- | --- |
| Airflow | `http://127.0.0.1:18088` |
| Flowable | `http://127.0.0.1:18080` |
| ClickHouse HTTP | `http://127.0.0.1:18123` |
| OpenSearch | `http://127.0.0.1:19200` |
| OpenSearch Dashboards | `http://127.0.0.1:15601` |
| Superset | `http://127.0.0.1:18089` |

## Sprint 0 Artifacts

- FastAPI backend skeleton: `apps/backend`.
- React/Vite frontend shell: `apps/frontend`.
- Development BPMN smoke process: `processes/dev-healthcheck`.
- Encoding quality gate: `tests/quality/test_text_encoding.py`.
- Dev helper scripts: `scripts/dev`.

## Sprint 1 Artifacts

- Canonical ingestion contracts: `apps/backend/open_fnr_api/data_contracts.py`.
- Ingestion status API: `apps/backend/open_fnr_api/ingestion.py`.
- Data ingestion process artifacts: `processes/data-ingestion`.
- Airflow DAG skeleton: `orchestration/airflow/dags/daily_ingestion.py`.
- Dev SQL metadata/staging tables: `infra/dev/postgres/init/001_open_fnr.sql`, `infra/dev/clickhouse/init/001_open_fnr.sql`.
- UI Data Load Status section: `apps/frontend/src/main.tsx`, `apps/frontend/src/styles.css`.

## Sprint 2 Artifacts

- DQ API and models: `apps/backend/open_fnr_api/data_quality.py`.
- DQ tests: `tests/backend/test_data_quality.py`.
- DQ process artifacts: `processes/data-quality`.
- DQ storage structures: `open_fnr.dq_rules`, `open_fnr.dq_incidents`, `open_fnr.dq_error_rows`.
- UI Data Quality Console: `apps/frontend/src/main.tsx`, `apps/frontend/src/styles.css`.
- HTML test report with screenshot: `docs/test-reports/sprint-2-data-quality/index.html`.

## Sprint 3 Artifacts

- Feature Mart API and models: `apps/backend/open_fnr_api/feature_mart.py`.
- Feature Mart tests: `tests/backend/test_feature_mart.py`, `tests/data/test_feature_mart_rules.py`.
- Feature Mart process artifacts: `processes/feature-mart`.
- Active matrix and feature store SQL structures in ClickHouse init script.
- Feature version metadata SQL structure in PostgreSQL init script.
- UI Feature Mart Status section.
- HTML test report with screenshot: `docs/test-reports/sprint-3-feature-mart/index.html`.

## Sprint 4 Artifacts

- Forecast API and metrics: `apps/backend/open_fnr_api/forecast.py`.
- Forecast tests: `tests/backend/test_forecast.py`.
- Regular forecast process artifacts: `processes/forecast`.
- Forecast version metadata SQL table in PostgreSQL init script.
- UI Regular Forecast Baseline section.
- HTML test report with screenshot: `docs/test-reports/sprint-4-regular-baseline/index.html`.

## Sprint 5 Artifacts

- Forecast Workbench API slice: `/forecast/workbench`.
- Forecast review BPMN/DMN/CMMN artifacts in `processes/forecast`.
- Forecast Workbench UI filters and chart panel.
- HTML test report with screenshot: `docs/test-reports/sprint-5-forecast-workbench/index.html`.

## Sprint 6 Artifacts

- ML model metadata API: `apps/backend/open_fnr_api/ml_models.py`.
- ML model tests: `tests/backend/test_ml_models.py`.
- Model candidate review BPMN/DMN/CMMN artifacts in `processes/ml`.
- UI Model Monitoring V1 section.
- HTML test report with screenshot: `docs/test-reports/sprint-6-ml-regular-model/index.html`.

## Verification

- `python -m pytest` -> 51 passed.
- `npm.cmd install` in `apps/frontend` -> completed, 0 vulnerabilities.
- `npm.cmd run build` in `apps/frontend` -> completed.
- `powershell -ExecutionPolicy Bypass -File scripts/dev/health.ps1` -> all dev services OK.
- `docker compose --env-file infra/dev/.env.example -f infra/dev/compose.yaml ps` -> services up.

## Next Step

Commit Sprint 6 checkpoint to `romanrav1980/OPEN_FNR`, then start Sprint 7.
