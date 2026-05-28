# Sprint 0 Completion Snapshot

Date: 2026-05-28

## Scope Completed

Sprint 0 established the local development foundation for OPEN FNR:

- FastAPI backend skeleton with `/health`, `/ready`, `/metadata`.
- React/Vite frontend shell for the development control tower.
- Docker Compose development infrastructure already running.
- Flowable BPMN smoke artifact for process-engine verification.
- UTF-8 and mojibake prevention rules in `.editorconfig`, project charter and tests.
- Dev scripts for service health, backend run and test execution.
- Context snapshot directory for recovery after future restarts.

## Important Files

| Area | Files |
| --- | --- |
| Backend | `apps/backend/open_fnr_api/*`, `tests/backend/test_health.py` |
| Frontend | `apps/frontend/*`, `apps/frontend/src/*` |
| Process | `processes/dev-healthcheck/dev_healthcheck_process.bpmn20.xml` |
| Quality | `.editorconfig`, `tests/quality/test_text_encoding.py` |
| Dev scripts | `scripts/dev/health.ps1`, `scripts/dev/run-backend.ps1`, `scripts/dev/test.ps1` |
| Context | `docs/context/CURRENT_STATE.md`, `docs/context/SPRINT_0_COMPLETION.md` |

## Verification Results

```text
python -m pytest
6 passed

npm.cmd run build
vite build completed

scripts/dev/health.ps1
Airflow OK
ClickHouse OK
Flowable OK
OpenSearch OK
Superset OK
```

## Local URLs

| Service | URL |
| --- | --- |
| Backend API | `http://127.0.0.1:8000/docs` |
| Frontend | `http://127.0.0.1:13000` |
| Airflow | `http://127.0.0.1:18088` |
| Flowable | `http://127.0.0.1:18080` |
| ClickHouse | `http://127.0.0.1:18123` |
| OpenSearch Dashboards | `http://127.0.0.1:15601` |
| Superset | `http://127.0.0.1:18089` |

## Known Notes

- Repository folder was not initialized as git before Sprint 0 completion.
- Frontend dependencies were installed locally and `node_modules` is ignored.
- `package-lock.json` should be committed with frontend package metadata.

## Next Sprint

Sprint 1 should implement the first vertical data-contract slice:

- canonical dictionaries for stores, SKUs and calendars;
- ingestion contracts and validation;
- UI shell for data source status;
- first BPMN data intake process;
- DQ tests and integration mocks.
