# OPEN FNR Industrial Hardening Sprint Plan

Date: 2026-05-29
Phase: after functional prototype completion.

## H1. Config, CI And Persistence Boundary

Status: completed.

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

Status: completed.

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
- Business action audit recording is controlled by `OPEN_FNR_AUDIT_ENABLED`; default is `true`.
- `open_fnr.schema_migrations` tracks schema baseline.

## H3. ClickHouse Marts

Status: completed.

### Scope

- create forecast, order proposal, stock projection and KPI marts;
- add write/read repository boundaries;
- add ClickHouse integration smoke tests;
- define retention and partitioning.

### Current Implementation

- ClickHouse DDL declares industrial marts for forecast, order proposals, stock projections, KPI, diagnostics and supplier performance.
- `apps/backend/open_fnr_api/mart_repositories.py` defines a ClickHouse mart metadata boundary.
- `/marts/clickhouse` exposes mart metadata for readiness and diagnostics.

## I1. POS Sales Ingestion

Status: implemented as contract, manifest, DAG skeleton and pilot landing discovery gate; awaiting actual pilot source files/API credentials.

### Scope

- add POS landing contract;
- add Airflow DAG for sales ingestion;
- add row count, checksum and schema validation;
- load sales into clean canonical table;
- route DQ failures to Process Engine.

### Current Implementation

- `PosSalesLine` defines POS receipt-line level contract with non-zero quantity validation.
- `/data/ingestion/manifests/pos-sales` exposes the current POS batch manifest with checksum, landing URI and idempotency key.
- `orchestration/airflow/dags/pos_sales_ingestion.py` defines the POS ingestion DAG skeleton: manifest, schema validation, DQ and clean publication.
- ClickHouse raw landing DDL includes `open_fnr.raw_pos_sales_lines`.

## I2. WMS Stock, Open Orders And In-Transit

Status: implemented as contract, manifest, DAG skeleton and pilot landing discovery gate; awaiting actual pilot source files/API credentials.

### Scope

- add WMS stock snapshot contract;
- add open order and in-transit contracts;
- add canonical clean tables;
- connect projected stock pipeline to real inputs.

### Current Implementation

- WMS contracts cover stock snapshots, open order lines and in-transit shipment lines.
- WMS manifest endpoints expose idempotency keys for stock, open orders and in-transit batches.
- `orchestration/airflow/dags/wms_inventory_ingestion.py` defines the WMS inventory ingestion DAG skeleton.
- ClickHouse raw landing DDL includes WMS stock snapshot, open order and in-transit tables.

## I3. ERP Prices And Order Export Statuses

Status: implemented as contract, manifest, DAG skeleton and pilot landing discovery gate; awaiting actual pilot source files/API credentials.

### Scope

- add ERP price source contract;
- add ERP order export status contract;
- add raw ClickHouse landing tables;
- add Airflow DAG skeleton for ERP commercial ingestion;
- expose idempotent manifests for prices and order status reconciliation.

### Current Implementation

- ERP contracts cover price validity and order export statuses.
- ERP manifest endpoints expose idempotency keys for price and order status batches.
- `orchestration/airflow/dags/erp_commercial_ingestion.py` defines the ERP commercial ingestion DAG skeleton.
- ClickHouse raw landing DDL includes ERP price and order export status tables.

## I4. MDM And PIM Reference Data

Status: implemented as contract, manifest, DAG skeleton and pilot landing discovery gate; awaiting actual pilot source files/API credentials.

### Scope

- add product and store MDM source contracts;
- include lifecycle, shelf-life, supplier, replenishment calendar and warehouse keys;
- add raw ClickHouse landing tables;
- add Airflow DAG skeleton for reference data ingestion;
- expose idempotent manifests for product and store sources.

### Current Implementation

- MDM contracts cover product lifecycle/fresh attributes and store replenishment routing keys.
- MDM manifest endpoints expose product and store source batches.
- `orchestration/airflow/dags/mdm_reference_ingestion.py` defines the MDM reference ingestion DAG skeleton.
- ClickHouse raw landing DDL includes product and store MDM tables.

## I5. Promo Source Ingestion

Status: implemented as contract, manifest, DAG skeleton and pilot landing discovery gate; awaiting actual pilot source files/API credentials.

### Scope

- add promo plan source contract;
- include SKU, store scope, period, price, discount, display location and display capacity;
- add raw ClickHouse landing table;
- add Airflow DAG skeleton for promo plan ingestion;
- expose idempotent manifest for promo plan source.

### Current Implementation

- Promo contract captures price, discount, mechanics, display place and display capacity.
- Promo manifest endpoint exposes source batch metadata and idempotency key.
- `orchestration/airflow/dags/promo_plan_ingestion.py` defines the promo plan ingestion DAG skeleton.
- ClickHouse raw landing DDL includes promo plan table.

## RDI-1. Real Source Landing Wiring

Status: completed for first pilot gate.

### Scope

- define mandatory pilot source contract matrix;
- discover configured local file drops for POS/WMS/ERP/MDM/PROMO;
- validate `manifest.json` sidecar presence and file references;
- return recovery tasks for missing files and manifest mismatch;
- surface source coverage in Control Tower.

### Current Implementation

- Required contract matrix: `PILOT_REQUIRED_SOURCE_CONTRACTS`.
- API endpoint: `/data/ingestion/pilot-shadow-load/plan`.
- UI Shadow Load Gate now loads source coverage and recovery tasks from the API.
- Test evidence: `docs/test-reports/sprint-real-source-landing-wiring/index.html`.

## S1. Production Security Foundation

Status: partially completed.

### Scope

- add authentication middleware;
- add policy layer for RBAC and object scopes;
- replace endpoint-local role checks with shared policy checks;
- persist audit events for all writes;
- add security regression tests.

### Current Implementation

- Admin Console and Security API expose users, service accounts, access requests and scope checks.
- Access approval/provisioning process is covered by API tests and UI evidence.
- IdP/IAM provisioning target adapter is configurable through `OPEN_FNR_IDP_PROVISIONING_URL`.
- JWT/OIDC boundary middleware is configurable through `OPEN_FNR_AUTH_ENABLED`, `OPEN_FNR_AUTH_DEV_BYPASS_ENABLED`, `OPEN_FNR_OIDC_ISSUER`, `OPEN_FNR_OIDC_AUDIENCE` and `OPEN_FNR_OIDC_JWKS_URL`.
- Shared policy layer `apps/backend/open_fnr_api/policy.py` centralizes role, service account and object-scope checks for the Security API.
- Local fallback is available for DEV/TEST; service account `svc-open-fnr-idp-provisioning` gates outbound provisioning.
- Remaining work: migrate remaining domain endpoints to shared policy helpers, add cryptographic JWKS signature validation and external secret store.

## X1. Outbound Target Adapter Hardening

Status: completed for core pilot outbound targets.

### Scope

- replace hardcoded/mock-only outbound behavior with configurable target adapters;
- keep DEV/TEST local fallback mode;
- require service accounts and idempotency keys for sends;
- add UI evidence and business-process test reports.

### Current Implementation

- Publication export targets: `OPEN_FNR_ERP_EXPORT_URL`, `OPEN_FNR_WMS_EXPORT_URL`, `OPEN_FNR_DWH_EXPORT_URL`, `OPEN_FNR_BI_EXPORT_URL`, `OPEN_FNR_AUTO_ORDER_EXPORT_URL`.
- Supplier forecast sharing target: `OPEN_FNR_SUPPLIER_FORECAST_SHARE_URL`.
- Procurement ERP target: `OPEN_FNR_ERP_EXPORT_URL`.
- Capacity TMS target: `OPEN_FNR_TMS_CAPACITY_EXPORT_URL`.
- Store App task target: `OPEN_FNR_STORE_APP_TASK_EXPORT_URL`.
- Planogram target: `OPEN_FNR_PLANOGRAM_EXPORT_URL`.
- IdP/IAM provisioning target: `OPEN_FNR_IDP_PROVISIONING_URL`.

### Evidence

- `docs/test-reports/sprint-outbound-publication-targets/index.html`
- `docs/test-reports/sprint-supplier-forecast-sharing-target/index.html`
- `docs/test-reports/sprint-procurement-erp-target/index.html`
- `docs/test-reports/sprint-capacity-tms-target/index.html`
- `docs/test-reports/sprint-store-app-task-target/index.html`
- `docs/test-reports/sprint-planogram-target/index.html`
- `docs/test-reports/sprint-idp-provisioning-target/index.html`

## U1. Routed UI Foundation

Status: completed for first shell; route-specific module split remains.

### Scope

- introduce React Router;
- split feature pages;
- add API client;
- add loading/error/denied states;
- keep control tower as a demo/status page only.

### Current Implementation

- Hash-route workspace shell defines Control Tower, Data, Forecast, Replenishment, Operations and Admin routes.
- Topbar and route summary reflect active route owner and purpose.
- Existing Control Tower remains the overview screen while route-specific page split is pending.
- Test evidence: `docs/test-reports/sprint-routed-ui-shell/index.html`.

## PROC-DEPLOY-1. Flowable Deployment Package

Status: completed for package manifest and checksum gate.

### Scope

- scan BPMN/DMN/CMMN artifacts;
- classify artifacts by Flowable type;
- compute SHA-256 checksums;
- expose package manifest through API;
- show deployment package evidence in Admin workspace.

### Current Implementation

- API module: `apps/backend/open_fnr_api/process_deployment.py`.
- Endpoint: `/process-deployment/packages/current`.
- Backend Docker image copies `processes` into `/app/processes`.
- Process artifacts root is configured by `OPEN_FNR_PROCESS_ARTIFACTS_ROOT_PATH`.
- Test evidence: `docs/test-reports/sprint-flowable-deployment-package/index.html`.

## Pilot Readiness Gate

The system can enter pilot only when:

- real POS/WMS/ERP/MDM/promo data flows pass DQ;
- security foundation is enabled;
- UI core workflows are API-backed;
- process deployment pipeline is available;
- load gate proves pilot SLA;
- business signs pilot scope and rollback plan.
