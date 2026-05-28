# OPEN FNR Industrial Hardening Sprint Plan

Date: 2026-05-29
Phase: after functional prototype completion.

## H1. Config, CI And Persistence Boundary

Status: in progress.

### Scope

- runtime mode and mock mode settings;
- repository boundary for persistence;
- audit event API and repository;
- PostgreSQL audit and integration batch tables;
- CI workflow for backend, frontend and compose configuration;
- tests for configuration and audit.

### Acceptance Criteria

- `python -m pytest` passes;
- `npm.cmd run build` passes;
- Docker Compose DEV/TEST/STAGE configs validate;
- application code has no hardcoded network addresses;
- metadata exposes runtime and mock mode;
- audit event can be written and listed.

## H2. PostgreSQL Persistence And Audit Store

Status: in progress.

### Scope

- introduce database connection management;
- replace in-memory audit repository with PostgreSQL implementation;
- add repository tests with a temporary PostgreSQL service;
- add migration/version table;
- persist process/action audit events.

### Current Implementation

- `apps/backend/open_fnr_api/database.py` provides lazy PostgreSQL connection management.
- `PostgresAuditEventRepository` writes to and reads from `open_fnr.audit_events`.
- `build_audit_event_repository(...)` selects in-memory repository for `mock_mode=true` and PostgreSQL repository for `mock_mode=false`.
- `open_fnr.schema_migrations` tracks schema baseline.

## H3. ClickHouse Marts

### Scope

- create forecast, order proposal, stock projection and KPI marts;
- add write/read repository boundaries;
- add ClickHouse integration smoke tests;
- define retention and partitioning.

## I1. POS Sales Ingestion

### Scope

- add POS landing contract;
- add Airflow DAG for sales ingestion;
- add row count, checksum and schema validation;
- load sales into clean canonical table;
- route DQ failures to Process Engine.

## I2. WMS Stock, Open Orders And In-Transit

### Scope

- add WMS stock snapshot contract;
- add open order and in-transit contracts;
- add canonical clean tables;
- connect projected stock pipeline to real inputs.

## S1. Production Security Foundation

### Scope

- add authentication middleware;
- add policy layer for RBAC and object scopes;
- replace endpoint-local role checks with shared policy checks;
- persist audit events for all writes;
- add security regression tests.

## U1. Routed UI Foundation

### Scope

- introduce React Router;
- split feature pages;
- add API client;
- add loading/error/denied states;
- keep control tower as a demo/status page only.

## Pilot Readiness Gate

The system can enter pilot only when:

- real POS/WMS/ERP/MDM/promo data flows pass DQ;
- security foundation is enabled;
- UI core workflows are API-backed;
- process deployment pipeline is available;
- load gate proves pilot SLA;
- business signs pilot scope and rollback plan.
