# OPEN FNR Next Delivery Plan

Date: 2026-05-29
Scope: industrial hardening, production deployment, real integrations and pilot preparation.

## Goal

Move OPEN FNR from a completed functional prototype with process/UI/API coverage and hardened outbound target adapters to a pilot-ready industrial system connected to real enterprise data sources.

## Release Map

| Release | Name | Goal | Exit criteria |
| --- | --- | --- | --- |
| R1 | Industrial Hardening Foundation | Make code, config, persistence and CI ready for real environments | Completed for config, audit, marts, target adapters and CI gates |
| R2 | Real Data Integration | Connect POS, ERP, WMS, DWH, MDM and promo data | Daily real data loads pass DQ and lineage checks |
| R3 | Process And Security Productionization | Deploy Flowable artifacts and production security | OIDC/JWT, RBAC, object-level access, IdP provisioning and process deployment pipeline |
| R4 | UI Productization | Replace demo control tower with routed API-backed application | Core workflows use real API, E2E tests pass |
| R5 | Supplement 1 Production Controls | Turn Supplement 1 governance into executable controls | Source SLA, ML lifecycle, acceptance, API, supplier, DR/BC and notification gates are enforced |
| R6 | Process Navigator | Make process execution visible through a zoomable map | Business-process map, alerts, BPMN drill-down and task/audit overlays are available |
| R7 | Pilot Launch | Run controlled pilot on selected stores/SKU | Pilot KPIs measured, business acceptance signed |

## Workstream Plan

### 1. Industrial Hardening

| Task | Output |
| --- | --- |
| Replace in-memory module data with repository interfaces | Backend persistence boundary |
| Add PostgreSQL migrations for metadata and audit | Versioned DB schema |
| Add ClickHouse marts for forecasts, orders, KPI, stock and diagnostics | Analytical storage |
| Add CI pipeline for tests, build, lint and artifact checks | Repeatable release gates |
| Add process deployment automation | Flowable deployment package |
| Add API versioning and error schema | Stable integration contracts |
| Harden outbound target adapters | Completed for publication, supplier, procurement, capacity/TMS, Store App, planogram and IdP provisioning |

### 2. Production Deployment

| Task | Output |
| --- | --- |
| Keep Docker Compose for local/dev/test/stage | Reproducible non-prod contours |
| Decide production orchestrator: Kubernetes preferred for HA | Production topology decision |
| Prepare environment-specific config model | DEV/TEST/STAGE/PROD config matrix |
| Add backup/restore smoke | RPO/RTO evidence |
| Add runbooks | Support readiness |

### 3. Real Integrations

| Source | Direction | First production-ready slice |
| --- | --- | --- |
| POS | Inbound | daily sales facts, returns, store/SKU/date |
| WMS | Inbound/outbound | DC stock, in-transit, open orders, order status |
| ERP | Inbound/outbound | prices, suppliers, order export, order status |
| DWH | Inbound/outbound | historical facts, forecast/order marts |
| MDM/PIM | Inbound | product, store, hierarchy, lifecycle |
| Promo system | Inbound/outbound | promo plans, promo status |
| Store app | Inbound/outbound | store tasks, stock feedback, display confirmation |
| TMS | Outbound | capacity smoothing and moved order export |
| Planogram/space management | Outbound | shelf/display capacity decision export |
| IdP/IAM | Outbound | approved access provisioning |

### 4. Production Security

| Task | Output |
| --- | --- |
| Add OIDC integration | User authentication |
| Add JWT verification in FastAPI | API authentication |
| Add RBAC and ABAC policy layer | Role and object-level access |
| Add persistent audit log | Compliance evidence |
| Externalize secrets | No secrets in git or images |
| Add service accounts | Controlled integration access |
| Add IdP provisioning adapter | Implemented with configurable endpoint and service account gate |

### 5. UI Productization

| Task | Output |
| --- | --- |
| Add React Router | Real navigation |
| Split control tower into feature pages | Maintainable UI modules |
| Add API client layer | Real API-backed screens |
| Add loading/error/empty states | Production UX |
| Add forms with validation | Real workflow actions |
| Add E2E tests per workflow | UI regression safety |

### 6. Pilot Launch

| Task | Output |
| --- | --- |
| Select pilot stores/categories/SKU | Pilot scope |
| Load 12-24 months history | Forecast training/backtesting base |
| Run shadow mode | Compare OPEN FNR vs current process |
| Run planner UAT | User acceptance |
| Enable controlled exports | Real operational impact |
| Measure business KPIs | WAPE, service level, lost sales, overstock, waste |

### 7. Supplement 1 Production Controls

Source document: [SUPPLEMENT_1_IMPLEMENTATION_SPRINT_PLAN.md](SUPPLEMENT_1_IMPLEMENTATION_SPRINT_PLAN.md).

| Task | Output |
| --- | --- |
| Implement source SLA runtime controls | Daily source readiness, degraded mode and publication block/waiver |
| Implement ML lifecycle controls | Candidate, shadow, champion, challenger, rollback and fallback governance |
| Implement replenishment financial parameters | Signed holding/lost sales/waste/service-level inputs for order optimization |
| Implement historical simulation and acceptance gates | 52-week simulation, shadow, parallel run and controlled pilot evidence |
| Implement API versioning governance | Consumer registry, standard errors, deprecation and idempotency controls |
| Implement supplier isolation and data classification | Supplier claim, object-level access and C1-C4 data controls |
| Implement notification, SLA and ITSM escalation | Human-task SLA, notification routing and ITSM integration |
| Implement lineage, retention and DR/BC controls | Dataset lineage, retention, backup/restore and degraded runbooks |

### 8. Process Navigator

Source document: [PROCESS_NAVIGATOR_MAP_SPEC.md](PROCESS_NAVIGATOR_MAP_SPEC.md).

| Task | Output |
| --- | --- |
| Keep backend map contract current | `/process-navigator/map`, `/alerts`, BPMN drill-down |
| Add routed UI module | `#/process-navigator` with map canvas, filters and details |
| Add semantic zoom | Domain cluster -> process -> BPMN step -> task/audit |
| Add alert overlays | BPMN quality, SLA, source data, ML drift, integration and security alerts |
| Add Flowable runtime overlay | Live process instance, task and history data |
| Add BPMN exact viewer | bpmn-js viewer for selected executable BPMN model |
| Add E2E and visual reports | Screenshots, business-process test narrative and regression evidence |

## Suggested Sprint Breakdown

| Sprint | Name | Main output |
| --- | --- | --- |
| H1 | Config, CI And Persistence Boundary | environment config, repositories, CI gates |
| H2 | PostgreSQL And Audit Persistence | metadata/audit migrations and repository tests |
| H3 | ClickHouse Marts | forecast/order/stock/KPI marts |
| I1 | POS And Sales Ingestion | real sales pipeline with DQ |
| I2 | WMS Stock And In-Transit Ingestion | stock/open orders/in-transit pipeline |
| I3 | ERP Prices, Suppliers And Orders | prices/supplier/order export contracts |
| I4 | MDM And Promo Ingestion | product/store/promo lifecycle data |
| S1 | OIDC, RBAC And Audit | production security foundation; IdP target adapter already implemented |
| P1 | Process Deployment Pipeline | Flowable deploy/version/migration |
| U1 | Routed UI Foundation | navigation, layout, API client |
| U2 | Forecast/Replenishment UI Productization | real API-backed core workflows |
| U3 | Store/Supplier/Diagnostics UI Productization | extended workflows |
| L1 | Load And Reliability Gate | EPYC profile tests and runbooks |
| SUP-1 | Source SLA Runtime Controls | source readiness, degraded mode and publication decision workflow |
| SUP-2 | ML Lifecycle Runtime Controls | candidate/shadow/champion/fallback gates |
| SUP-3 | Replenishment Financial Parameters | signed cost and service-level parameters |
| SUP-4 | Historical Simulation And Acceptance | 52-week simulation, shadow and parallel-run evidence |
| SUP-5 | API Versioning And Consumer Registry | versioned APIs, error registry, deprecation and idempotency |
| SUP-6 | Supplier Isolation And Data Classification | supplier API isolation and C1-C4 controls |
| SUP-7 | Notification, SLA And ITSM Escalation | alert routing, human-task SLA and ITSM webhook |
| SUP-8 | Lineage, Retention And DR/BC | lineage, retention, backup/restore and degraded mode |
| SUP-9 | Process Navigator Map | zoomable process map, alerts and BPMN drill-down |
| SUP-10 | Pilot Production Gate | unified Supplement 1 go/no-go for pilot |
| PN-1 | Process Navigator Backend Map Contract | completed API contract and tests |
| PN-2 | Process Navigator UI Shell | routed map UI, filters and detail panel |
| PN-3 | Process Runtime Overlay | Flowable task/instance/history overlay |
| PN-4 | Alert Correlation | OpenSearch/Prometheus/Process Engine alert correlation |
| PN-5 | BPMN Exact Viewer | bpmn-js diagram panel and drill-down |
| PN-6 | Process Navigator Hardening | RBAC, load, audit, accessibility and presentation report |
| Pilot 1 | Shadow Pilot | no operational exports, KPI comparison |
| Pilot 2 | Controlled Export Pilot | limited real exports and business sign-off |

Detailed industrial hardening sprint execution is tracked in [INDUSTRIAL_HARDENING_SPRINTS.md](INDUSTRIAL_HARDENING_SPRINTS.md).

## Immediate Next Actions

1. Approve pilot scope: stores, categories, SKU, suppliers and regions.
2. Collect source contracts and sample files/API specs from POS, ERP, WMS, DWH, MDM and promo systems.
3. Provide real endpoint details for ERP/WMS/DWH/BI/auto-order, supplier portal, TMS, Store App, planogram and IdP.
4. Decide production deployment mode: Kubernetes vs production Compose.
5. Choose OIDC/JWT provider details and token validation parameters.
6. Prioritize UI productization pages for pilot users.
7. Start SUP-1 Source SLA Runtime Controls.
8. Start PN-2 Process Navigator UI Shell using the existing PN-1 backend contract.
