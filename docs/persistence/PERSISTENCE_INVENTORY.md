# OPEN FNR Persistence Inventory

Status: IH-1 baseline  
Date: 2026-05-29  
Next sprint: IH-2 PostgreSQL Persistence And Migrations

## 1. Purpose

This inventory fixes the persistence boundary for the remaining industrial hardening work. It separates production state that must become durable from DEV fixtures that may remain static until their module is productized.

## 2. Classification

| Classification | Meaning | Target |
| --- | --- | --- |
| P0 | Production decision state; losing it changes business outcome or auditability | PostgreSQL in IH-2/IH-3 |
| P1 | Operational state needed for pilot workflows and reconciliation | PostgreSQL in IH-2 or release-specific migration |
| P2 | Analytical/model state needed for scalable calculations | ClickHouse and/or object storage in ML/RI releases |
| D1 | DEV fixture or demo/read-only reference | May stay static while `OPEN_FNR_MOCK_MODE=true` |
| C1 | Configuration or rule catalog | Config, versioned table, or governed artifact depending on owner |

## 3. Current Repository Boundary

| Area | Current State | Target Decision |
| --- | --- | --- |
| Audit events | `AuditEventRepository` has in-memory and PostgreSQL implementations | Keep, harden in IH-3; process business audit remains enabled by default |
| PostgreSQL connection | `database.py` provides pg8000 connection factory | Keep; add repository interfaces per state domain |
| ClickHouse marts | `mart_repositories.py` catalogs mart tables | Keep; add real write/read adapters in RI/ML releases |
| Process runtime | `process_engine.py` uses static task/audit fixtures | Move runtime task and audit state to PostgreSQL; BPMN artifacts remain in `processes/` and Flowable |
| Process Navigator cache | in-memory conformance job/cache dictionaries | Keep only as short-lived cache; persistent job history goes to PostgreSQL if used in production |

## 4. P0/P1 Production Persistence Targets

| Module | Current in-memory/static state | Classification | Target repository | First sprint |
| --- | --- | --- | --- | --- |
| `adjustments.py` | `ADJUSTMENTS`, `ADJUSTMENT_AUDIT_EVENTS` | P0 | `AdjustmentRepository`, `AdjustmentAuditRepository` | IH-2/IH-3 |
| `exceptions.py` | `EXCEPTIONS`, `EXCEPTION_AUDIT_EVENTS` | P0 | `ExceptionRepository`, `ExceptionAuditRepository` | IH-2/IH-3 |
| `process_engine.py` | `TASKS`, `AUDIT_EVENTS` | P0 | `ProcessTaskRepository`, `ProcessAuditRepository` | IH-2/IH-3 |
| `publication.py` | `PUBLICATION_PACKAGES` | P0 | `PublicationPackageRepository`, `ExportAttemptRepository` | IH-2 |
| `replenishment.py` | `ORDER_PROPOSALS`, `FINAL_ORDERS`, `ORDER_AUDIT_EVENTS` | P0 | `OrderProposalRepository`, `FinalOrderRepository`, `OrderAuditRepository` | IH-2/IH-3 |
| `security.py` | `USERS`, `SERVICE_ACCOUNTS`, `ACCESS_REQUESTS` | P0 | `UserRepository`, `ServiceAccountRepository`, `AccessRequestRepository` | SEC-1/SEC-3 |
| `store_management.py` | `STORE_TASKS` | P0 | `StoreTaskRepository`, `StoreFeedbackRepository` | IH-2/UI-3 |
| `capacity.py` | `AFFECTED_ORDERS` | P1 | `CapacityPlanRepository`, `CapacityMoveRepository` | IH-2/RI-6 |
| `clean_publication.py` | clean publication plans/runs are computed from fixtures | P1 | `CleanPublicationRunRepository` | RI-6 |
| `data_quality.py` | `INCIDENTS`, source contract run outputs | P1 | `DqIncidentRepository`, `DqRunRepository` | RI-6 |
| `ingestion.py` | `SAMPLE_BATCHES`, readiness fixtures | P1 | `IngestionBatchRepository`, `SourceReadinessRepository` | RI-1/RI-6 |
| `lifecycle.py` | `LIFECYCLE_AUDIT` | P1 | `LifecycleEventRepository` | RI-5 |
| `pilot.py` | `PILOT_FEEDBACK`, `PILOT_ISSUES`, checklist state | P1 | `PilotRunRepository`, `PilotIssueRepository` | PILOT-1 |
| `process_governance.py` | `VERSIONS`, `CHANGE_REQUESTS` | P1 | `ProcessVersionRepository`, `ProcessChangeRepository` | SEC-4/DEP-2 |
| `procurement.py` | approval/export outcomes around purchase proposals | P1 | `ProcurementProposalRepository`, `ProcurementExportRepository` | RI-4 |
| `promo.py` | `PROMO_APPROVALS` | P1 | `PromoApprovalRepository`, `PromoWorkflowRepository` | RI-5/UI-2 |
| `release_gate.py` | approval checklist/risk state | P1 | `ReleaseGateRepository` | DEP-2 |
| `shelf_space.py` | shelf exception decisions | P1 | `ShelfExceptionRepository` | UI-3 |
| `supplier_collaboration.py` | supplier confirmations | P1 | `SupplierConfirmationRepository` | RI-4 |

## 5. P2 Analytical And ML Persistence Targets

| Module | Current state | Classification | Target |
| --- | --- | --- | --- |
| `forecast.py` | `FORECAST_VERSIONS`, `FORECAST_ROWS` | P2 | ClickHouse forecast mart and model artifact metadata |
| `feature_mart.py` | `ACTIVE_MATRIX`, `FEATURE_VERSIONS`, `FEATURES` | P2 | ClickHouse feature mart, version table |
| `kpi.py` | `KPI_ITEMS` | P2 | ClickHouse KPI mart |
| `ml_models.py` | `MODEL_VERSIONS` | P2 | model registry metadata in PostgreSQL plus artifact storage path |
| `ml_governance.py` | `MODEL_CANDIDATES` | P2/P1 | model governance repository and audit |
| `multi_echelon.py` | `STORE_DEMANDS`, `DC_STOCKS` | P2 | ClickHouse multi-echelon planning marts |
| `performance.py` | `PILOT_METRICS`, `BOTTLENECKS` | P2 | benchmark result mart |
| `replenishment.py` | `STOCK_SNAPSHOTS`, `OPEN_ORDERS`, `POLICIES`, `INVENTORY_PROJECTIONS`, `FRESH_WORKBENCH_ITEMS` | P2/P1 | ClickHouse stock/order/projection marts plus PostgreSQL policy approvals |
| `replenishment_scale.py` | `PARTITIONS` | P2 | batch run and partition status mart |

## 6. D1 DEV Fixtures That May Remain Static For Now

| Module | Fixture | Reason |
| --- | --- | --- |
| `data_contracts.py` | `SCHEMA_REGISTRY` | Code-level schema registry |
| `data_quality.py` | `RULES`, `SOURCE_CONTRACT_DQ_PLANS` | Rule catalog until governed rule UI is implemented |
| `data_scale.py` | `PARTITIONS`, `LINEAGE` | Demo observability until real lineage ingestion |
| `diagnostics.py` | `EVIDENCE` | Demo diagnostic cards |
| `observability.py` | `ALERTS`, `INCIDENTS` | Demo support views until monitoring integration |
| `process_engine.py` | `PROCESS_DEFINITIONS` | Built from local process artifacts; not operational state |
| `process_navigator.py` | `DOMAIN_LABELS`, `PROCESS_DEPENDENCY_EDGES`, `NAVIGATOR_READ_ROLES`, `SUPPLIER_DENIED_ROLES` | Static map/config; move to config only if business owners need runtime changes |
| `shadow_load.py` | `SOURCE_MANIFESTS` | Required source catalog; becomes config/table when source onboarding UI exists |
| `stage.py` | `STAGE_STEPS`, `UAT_CHECKLIST` | Stage rehearsal checklist fixture |
| `supplement_governance.py` | source SLA rules, financial parameters, acceptance gates, notification rules, human task SLAs, open questions | C1 governed catalogs; production owner sign-off required before table migration |

## 7. IH-2 Migration Order

1. `open_fnr.operational_events` and reusable audit/event indexes.
2. Process task state: `process_tasks`, `process_task_events`. Status: foundation DDL and repository added.
3. Forecast/replenishment operational decisions: `manual_adjustments`, `exceptions`, `order_proposals`, `final_orders`. Status: generic `operational_decisions` foundation added; domain tables still pending.
4. Publication/export state: `publication_packages`, `export_attempts`. Status: foundation DDL added; domain repository still pending.
5. Store and supplier operational feedback: `store_tasks`, `supplier_confirmations`.
6. Security admin state if OIDC/JWT sprint starts before pilot: `users`, `service_accounts`, `access_requests`.

## 8. Repository Interface Standard

Every production repository must expose:

- `mode: RepositoryMode`;
- deterministic create/update methods with idempotency key where applicable;
- `get` and `list` methods with object-level filter inputs;
- explicit transaction boundary for multi-step writes;
- tests for in-memory/dev mode only when `OPEN_FNR_MOCK_MODE=true`;
- PostgreSQL tests using fake connection or test database fixture;
- audit event emission for business decisions.

## 9. IH-1 Acceptance Checklist

| Item | Status |
| --- | --- |
| In-memory/mock production state is inventoried | Done |
| Target repository names are defined | Done |
| Migration order for IH-2 is defined | Done |
| DEV fixtures are explicitly separated from production state | Done |
| Quality test guards this inventory | Done |

## 10. Out Of Scope For IH-1

- Creating all PostgreSQL tables.
- Replacing every module in one sprint.
- Implementing production OIDC/JWT.
- Changing existing API response shapes unless required by repository boundary.

## 11. IH-2 Foundation Status

Completed foundation:

- PostgreSQL DDL for `process_tasks`, `process_task_events`, `operational_decisions`, `publication_packages` and `export_attempts`.
- `ProcessTaskRepository` with in-memory and PostgreSQL implementations.
- `OperationalDecisionRepository` with in-memory and PostgreSQL implementations.
- Runtime write boundary for process task completion.
- Runtime write boundary for publication send/retry.
- Runtime write boundary for replenishment order proposal adjustment.
- Runtime write boundary for store task completion.

Remaining IH-2 domain-table migrations:

- dedicated `manual_adjustments` table and repository;
- dedicated `exceptions` table and repository;
- dedicated `order_proposals`/`final_orders` PostgreSQL decision tables if pilot requires OLTP editing outside ClickHouse marts;
- dedicated `store_task_feedback` table if photo/evidence metadata must be queried independently;
- security admin tables for users, service accounts and access requests, unless moved to `SEC-1..SEC-3`.
