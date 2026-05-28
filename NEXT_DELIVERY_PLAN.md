# OPEN FNR Next Delivery Plan

Date: 2026-05-28
Scope: industrial hardening, production deployment, real integrations and pilot preparation.

## Goal

Move OPEN FNR from a completed functional prototype with process/UI/API coverage to a pilot-ready industrial system connected to real enterprise data sources.

## Release Map

| Release | Name | Goal | Exit criteria |
| --- | --- | --- | --- |
| R1 | Industrial Hardening Foundation | Make code, config, persistence and CI ready for real environments | Config centralized, DB persistence introduced, CI quality gates green |
| R2 | Real Data Integration | Connect POS, ERP, WMS, DWH, MDM and promo data | Daily real data loads pass DQ and lineage checks |
| R3 | Process And Security Productionization | Deploy Flowable artifacts and production security | OIDC/JWT, RBAC, object-level access, process deployment pipeline |
| R4 | UI Productization | Replace demo control tower with routed API-backed application | Core workflows use real API, E2E tests pass |
| R5 | Pilot Launch | Run controlled pilot on selected stores/SKU | Pilot KPIs measured, business acceptance signed |

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

### 4. Production Security

| Task | Output |
| --- | --- |
| Add OIDC integration | User authentication |
| Add JWT verification in FastAPI | API authentication |
| Add RBAC and ABAC policy layer | Role and object-level access |
| Add persistent audit log | Compliance evidence |
| Externalize secrets | No secrets in git or images |
| Add service accounts | Controlled integration access |

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
| S1 | OIDC, RBAC And Audit | production security foundation |
| P1 | Process Deployment Pipeline | Flowable deploy/version/migration |
| U1 | Routed UI Foundation | navigation, layout, API client |
| U2 | Forecast/Replenishment UI Productization | real API-backed core workflows |
| U3 | Store/Supplier/Diagnostics UI Productization | extended workflows |
| L1 | Load And Reliability Gate | EPYC profile tests and runbooks |
| Pilot 1 | Shadow Pilot | no operational exports, KPI comparison |
| Pilot 2 | Controlled Export Pilot | limited real exports and business sign-off |

Detailed industrial hardening sprint execution is tracked in [INDUSTRIAL_HARDENING_SPRINTS.md](INDUSTRIAL_HARDENING_SPRINTS.md).

## Immediate Next Actions

1. Approve pilot scope: stores, categories, SKU, suppliers and regions.
2. Collect source contracts and sample files/API specs from POS, ERP, WMS, DWH, MDM and promo systems.
3. Decide production deployment mode: Kubernetes vs production Compose.
4. Choose IdP/OIDC integration details.
5. Prioritize UI productization pages for pilot users.
