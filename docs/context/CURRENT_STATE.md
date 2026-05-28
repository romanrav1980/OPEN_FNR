# OPEN FNR Current State

Last updated: 2026-05-28

## Active Work

Sprint 0 implementation is complete.

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

## Verification

- `python -m pytest` -> 6 passed.
- `npm.cmd install` in `apps/frontend` -> completed, 0 vulnerabilities.
- `npm.cmd run build` in `apps/frontend` -> completed.
- `powershell -ExecutionPolicy Bypass -File scripts/dev/health.ps1` -> all dev services OK.
- `docker compose --env-file infra/dev/.env.example -f infra/dev/compose.yaml ps` -> services up.

## Next Step

Commit Sprint 0 checkpoint to `romanrav1980/OPEN_FNR`, then start Sprint 1.
