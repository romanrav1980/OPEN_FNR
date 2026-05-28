# OPEN FNR Current State

Last updated: 2026-05-28

## Active Work

Sprint 1 implementation is complete.

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

## Verification

- `python -m pytest` -> 14 passed.
- `npm.cmd install` in `apps/frontend` -> completed, 0 vulnerabilities.
- `npm.cmd run build` in `apps/frontend` -> completed.
- `powershell -ExecutionPolicy Bypass -File scripts/dev/health.ps1` -> all dev services OK.
- `docker compose --env-file infra/dev/.env.example -f infra/dev/compose.yaml ps` -> services up.

## Next Step

Commit Sprint 1 checkpoint to `romanrav1980/OPEN_FNR`, then start Sprint 2.
