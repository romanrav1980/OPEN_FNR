# IH-2 Completion Note

Status: completed as persistence foundation  
Date: 2026-05-29  
Sprint: IH-2 PostgreSQL Persistence And Migrations

## Scope Completed

IH-2 established the PostgreSQL-ready persistence foundation for production operational decisions while preserving existing API response shapes.

Completed artifacts:

- PostgreSQL DDL in `infra/dev/postgres/init/001_open_fnr.sql`:
  - `open_fnr.process_tasks`;
  - `open_fnr.process_task_events`;
  - `open_fnr.operational_decisions`;
  - `open_fnr.publication_packages`;
  - `open_fnr.export_attempts`.
- Repository records, protocols and implementations in `apps/backend/open_fnr_api/repositories.py`:
  - `ProcessTaskRecord`;
  - `ProcessTaskEventRecord`;
  - `OperationalDecisionRecord`;
  - `ProcessTaskRepository`;
  - `OperationalDecisionRepository`;
  - in-memory implementation for `OPEN_FNR_MOCK_MODE=true`;
  - PostgreSQL implementation for production mode.
- Runtime write boundaries:
  - process task completion;
  - publication send/retry;
  - replenishment order proposal adjustment;
  - store task completion;
  - manual adjustment actions;
  - exception actions.

## Acceptance Evidence

Targeted tests:

- `tests/backend/test_repositories.py`;
- `tests/data/test_postgres_operational_schema.py`;
- `tests/architecture/test_persistence_inventory.py`;
- `tests/backend/test_process_engine.py`;
- `tests/backend/test_publication.py`;
- `tests/backend/test_replenishment.py`;
- `tests/backend/test_store_management.py`;
- `tests/backend/test_adjustments.py`;
- `tests/backend/test_exceptions.py`.

Full verification:

- `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 482 passed, 1 warning about `.pytest_cache` permissions.

## Deferred From IH-2

These items are intentionally not implemented in IH-2 because the generic operational decision repository now provides the pilot-safe write boundary:

- dedicated `manual_adjustments` table;
- dedicated `exceptions` table;
- dedicated OLTP `order_proposals` and `final_orders` tables;
- dedicated `store_task_feedback` table;
- security admin tables for users, service accounts and access requests.

Deferred destinations:

- IH-3: audit retention, query APIs and immutable event evidence;
- SEC-1..SEC-3: production user/service account tables after OIDC/JWT boundaries are active;
- RI/UI sprints: domain-specific OLTP tables only when real integration or UI workflow requires mutable lists beyond `operational_decisions`.

## Remaining Risk

The current APIs still list many read models from static fixtures while writes are captured through durable boundaries. This is acceptable for the foundation stage but must be resolved during UI productization and real integration sprints where persisted read-after-write behavior becomes mandatory.
