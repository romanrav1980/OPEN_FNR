# OPEN FNR Remaining Project Focused Sprint Plan

Status: active tactical plan  
Date: 2026-05-29  
Scope: remaining work after completed Process Navigator PN-3..PN-12

## 1. Purpose

This document turns the remaining OPEN FNR work into a focused sprint plan. It is intentionally narrower than the full product vision: the goal is to move from the current prototype/engineering baseline to a pilot-ready industrial system without expanding scope.

## 2. Focus Rules

| Rule | Decision |
| --- | --- |
| One active release at a time | Do not start the next release until the previous release exit criteria are met or explicitly waived. |
| No new product domains | Work is limited to industrial hardening, real integrations, production security, UI productization, ML/replenishment production, deployment and pilot launch. |
| No proprietary dependencies | Self-hosted open-source only; no GPL, AGPL, SSPL, BUSL, proprietary or SaaS-required tools. |
| Config first | Hosts, ports, URLs, credentials, feature flags, polling and thresholds are configured through env/config. |
| Evidence required | Each sprint produces tests and, where UI/process behavior is touched, an HTML evidence report with screenshots. |
| Pilot orientation | Every sprint must improve pilot readiness or remove a production blocker. |

## 3. Release Map

| Release | Sprints | Goal | Exit Gate |
| --- | --- | --- | --- |
| R1 | IH-1..IH-4 | Industrial hardening foundation | Persistent storage, audit, backup smoke and repository boundaries are ready. |
| R2 | RI-1..RI-6 | Real enterprise integrations | POS/ERP/WMS/DWH/MDM/Promo loads pass DQ, idempotency and reconciliation gates. |
| R3 | SEC-1..SEC-4 | Production security | OIDC/JWT, RBAC, object access, secrets and service accounts are production-ready. |
| R4 | UI-1..UI-5 | UI productization | Routed React app uses real APIs and has E2E/visual/accessibility coverage. |
| R5 | ML-1..ML-5 | ML and replenishment production | Training, backtesting, champion/challenger, drift and EPYC performance gates are ready. |
| R6 | DEP-1..DEP-4 | Deployment and operations | DEV/TEST/STAGE/PROD, CI/CD, rollback, monitoring and runbooks are ready. |
| R7 | PILOT-1..PILOT-5 | Pilot launch | Shadow mode, controlled exports and business acceptance are complete. |

## 4. Sprint Summary

| Sprint | Name | Main Output | Depends On |
| --- | --- | --- | --- |
| IH-1 | Persistence Inventory And Repository Boundaries | Inventory of remaining mock/in-memory state and repository interfaces | Completed |
| IH-2 | PostgreSQL Persistence And Migrations | Metadata, process, audit and operational tables with migrations | Completed foundation |
| IH-3 | Production Audit Event Storage | Production-grade audit/event repository, retention and query APIs | Completed |
| IH-4 | Backup Restore Smoke | PostgreSQL/ClickHouse backup/restore smoke and runbook | Completed |
| RI-1 | Source Contracts Freeze | Real source contracts, field mapping and SLA matrix | Completed |
| RI-2 | POS And DWH Sales Ingestion | Real sales facts and history ingestion | Completed foundation |
| RI-3 | WMS Stock, In-Transit And Open Orders | Real stock/in-transit/open-order ingestion | Completed foundation |
| RI-4 | ERP Prices, Suppliers And Order Status | ERP commercial ingestion and outbound status reconciliation | Completed foundation |
| RI-5 | MDM And Promo Ingestion | Product, store, hierarchy, lifecycle and promo ingestion | Completed foundation |
| RI-6 | Reconciliation, Retries And Source SLA | Idempotency, retry, reconciliation, degraded mode and source SLA gates | Completed foundation |
| SEC-1 | OIDC/JWT Authentication | Real authentication and token verification | Completed foundation |
| SEC-2 | RBAC And Object-Level Access | Role/object policy across API and UI | Completed foundation |
| SEC-3 | Secrets And Service Accounts | Secrets outside git and controlled integration identities | Completed foundation |
| SEC-4 | Security Audit And Access Review | Audit views, access review workflow and negative tests | Completed foundation |
| UI-1 | Routed Application Foundation | React Router, feature pages and API client | SEC-1 |
| UI-2 | Forecast And Replenishment Workbenches | Real API-backed forecast/order workflows | UI-1, RI-6 |
| UI-3 | Integration And Data Quality UI | Source status, DQ, reconciliation and retry screens | UI-1, RI-6 |
| UI-4 | Security, Admin And Process UI | User/role/admin/process operational screens | UI-1, SEC-4 |
| UI-5 | UI E2E Visual Accessibility Suite | Playwright E2E, visual checks and accessibility reports | UI-2..UI-4 |
| ML-1 | Training Data Mart And Backtesting | Real training dataset and backtesting jobs | RI-6 |
| ML-2 | Forecast Training And Retraining | Regular/promo model training and scheduled retraining | ML-1 |
| ML-3 | Champion Challenger And Drift | Model registry, shadow, drift, rollback and fallback controls | ML-2 |
| ML-4 | Replenishment Optimization Production | Demand projection, safety stock, order proposals on real data | ML-2, RI-6 |
| ML-5 | EPYC Performance Gate | Production-scale forecast/replenishment runtime validation | ML-4 |
| DEP-1 | Environment Topology | DEV/TEST/STAGE/PROD Compose/Kubernetes decision and config matrix | IH-2 |
| DEP-2 | CI/CD Release Gates | Build, test, migration, image and artifact gates | DEP-1 |
| DEP-3 | Observability And Runbooks | Metrics, logs, traces, alerts and operational runbooks | DEP-1 |
| DEP-4 | Rollback And DR Drill | Release rollback, backup restore and degraded mode drill | IH-4, DEP-2 |
| PILOT-1 | Pilot Scope And Data Readiness | Stores/SKU/categories/suppliers, 12-24 month history readiness | RI-6 |
| PILOT-2 | Shadow Mode | OPEN FNR vs current process comparison without operational exports | ML-4, UI-5 |
| PILOT-3 | Controlled Export Pilot | Limited ERP/auto-order export with rollback | PILOT-2, DEP-4 |
| PILOT-4 | Business KPI Acceptance | WAPE, service level, lost sales, overstock and waste evidence | PILOT-3 |
| PILOT-5 | Production Go/No-Go | Final acceptance pack and launch decision | PILOT-4 |

## 5. Detailed Sprints

### IH-1. Persistence Inventory And Repository Boundaries

Goal: identify all remaining mock/in-memory state and define repository boundaries before changing storage.

Functional scope:

- inventory in-memory stores in backend modules;
- classify state as configuration, reference data, operational state, audit event, ML metadata or report cache;
- define repository interfaces and migration plan;
- freeze what remains intentionally mock-only for DEV demos.

Tests:

- quality test proving no production endpoint writes only to in-memory repository unless explicitly marked DEV/mock;
- architecture test for repository interface coverage;
- documentation lint for persistence inventory.

Acceptance criteria:

- persistence inventory is complete;
- each stateful module has target storage and owner;
- next migration sprint has a precise table/repository list.

Not in scope:

- implementing all migrations;
- changing business behavior.

### IH-2. PostgreSQL Persistence And Migrations

Goal: replace critical mock/in-memory state with PostgreSQL-backed repositories.

Functional scope:

- versioned migrations for operational metadata, user actions, process task state, export status and audit indexes;
- repository implementations with transaction boundaries;
- idempotent write APIs;
- migration smoke for clean database and upgrade path.

Tests:

- repository tests with PostgreSQL container/local test config;
- migration apply/reapply tests;
- API tests proving restart does not lose state;
- encoding and no-hardcoded-network gates.

Acceptance criteria:

- critical operational state survives process restart;
- migration version is recorded;
- no production path depends on in-memory state for persisted decisions.

### IH-3. Production Audit Event Storage

Goal: make audit/event storage production-grade while keeping business-process event audit enabled by default.

Functional scope:

- PostgreSQL audit event repository;
- retention policy and query indexes;
- event schema for actor, role, object, action, before/after, correlation id and process instance;
- API endpoints for audit search and export;
- config switch for non-process audit where applicable; business-process event audit remains enabled by default.

Tests:

- audit write/read tests;
- retention policy tests;
- RBAC negative tests for audit access;
- process audit trail tests.

Acceptance criteria:

- process event audit is enabled by default;
- audit records are immutable from application APIs;
- audit query works by actor, object, process and date range.

### IH-4. Backup Restore Smoke

Goal: prove that PostgreSQL and ClickHouse can be backed up and restored for pilot operations.

Functional scope:

- backup scripts/runbooks for PostgreSQL and ClickHouse;
- restore smoke into clean environment;
- RPO/RTO evidence template;
- degraded mode decision checklist.

Tests:

- backup artifact existence and checksum;
- restore smoke with sample data;
- runbook validation test.

Acceptance criteria:

- restore smoke is repeatable;
- RPO/RTO values are documented;
- support team has a runbook.

### RI-1. Source Contracts Freeze

Goal: lock real inbound/outbound contracts before building production ingestion.

Functional scope:

- POS, ERP, WMS, DWH, MDM and Promo source mapping;
- required/optional fields;
- source SLA, freshness, timezone, row-level uniqueness and reconciliation keys;
- source owner and escalation route.

Tests:

- contract schema validation tests;
- sample file/API fixture validation;
- DQ rule coverage tests.

Acceptance criteria:

- each source has signed contract and sample;
- reconciliation keys are known;
- no ingestion sprint starts with unresolved required fields.

### RI-2. POS And DWH Sales Ingestion

Goal: load real sales history and daily sales facts.

Functional scope:

- POS receipt-line ingestion;
- DWH historical sales ingestion for 12-24 months;
- returns, corrections and late-arriving facts;
- idempotency and partitioning by business date.

Tests:

- schema, row count, duplicates, referential integrity and freshness;
- reconciliation POS vs DWH totals;
- retry/idempotency tests;
- load test for pilot volume.

Acceptance criteria:

- daily sales facts are available for forecast/backtesting;
- late facts are handled without duplicate demand;
- DQ blockers create process tasks.

### RI-3. WMS Stock, In-Transit And Open Orders

Goal: load real inventory signals needed for projected stock and replenishment.

Functional scope:

- DC stock, store stock, open orders, in-transit and expected receipt dates;
- inventory snapshot versioning;
- reconciliation with ERP/order status where available.

Tests:

- schema, freshness, duplicates and referential integrity;
- negative quantity and impossible date checks;
- reconciliation by DC/store/SKU.

Acceptance criteria:

- projected stock can use real on-hand, on-order and in-transit data;
- stale inventory blocks publication or triggers degraded mode.

### RI-4. ERP Prices, Suppliers And Order Status

Goal: connect commercial ERP data and order export feedback.

Functional scope:

- price, supplier, lead time, MOQ, pack and ordering calendar ingestion;
- order export status ingestion;
- outbound order status reconciliation;
- retry and idempotency for export status.

Tests:

- contract tests for price/supplier/order status;
- idempotency tests;
- reconciliation order proposal vs ERP status;
- service account access tests.

Acceptance criteria:

- replenishment uses real commercial parameters;
- exported orders have traceable ERP status.

### RI-5. MDM And Promo Ingestion

Goal: load real product, store, hierarchy, lifecycle and promo plan data.

Functional scope:

- product, store, category, supplier and lifecycle master data;
- promo mechanics, SKU, discount, price, display place, display capacity, period and store scope;
- MDM change handling and effective dates.

Tests:

- referential integrity with sales/stock;
- promo overlap and missing price checks;
- lifecycle phase-in/phase-out tests.

Acceptance criteria:

- active store/SKU matrix is reliable;
- promo forecast has all required promo attributes;
- lifecycle events affect forecast/replenishment.

### RI-6. Reconciliation, Retries And Source SLA

Goal: make real integrations operationally safe.

Functional scope:

- source readiness gate;
- retry policies;
- reconciliation dashboards/API;
- degraded mode and waiver process;
- source SLA process tasks and audit.

Tests:

- retry and idempotency tests;
- source late/missing/error paths;
- process tests for blocker, waiver and recovery;
- UI report with screenshots if screens are touched.

Acceptance criteria:

- missing/late sources do not silently publish bad data;
- every blocker has owner, SLA, status and audit trail.

### SEC-1. OIDC/JWT Authentication

Goal: enable real authentication in non-DEV environments.

Functional scope:

- OIDC discovery/JWKS validation;
- JWT audience, issuer, expiry and signature checks;
- DEV bypass remains config-gated only.

Tests:

- valid/invalid token tests;
- expired token tests;
- environment gate tests.

Acceptance criteria:

- protected APIs require valid JWT in TEST/STAGE/PROD;
- auth behavior is config-driven.

### SEC-2. RBAC And Object-Level Access

Goal: enforce role and object-level access consistently.

Functional scope:

- role-to-permission matrix;
- region/category/store/supplier object filters;
- backend enforcement and UI hiding;
- supplier isolation.

Tests:

- positive/negative RBAC tests;
- object-level leakage tests;
- UI RBAC tests.

Acceptance criteria:

- users only see authorized stores, categories, suppliers and process data;
- unauthorized access is audited.

### SEC-3. Secrets And Service Accounts

Goal: remove secrets from code/config files and define integration identities.

Functional scope:

- secret loading from environment/secret files/orchestrator secret provider;
- service account registry;
- token scopes for POS/ERP/WMS/DWH/MDM/Promo/BI exports.

Tests:

- secret absence in git;
- service account scope tests;
- rotation runbook check.

Acceptance criteria:

- no production secret is stored in repository;
- each integration has a named service account and minimum permissions.

### SEC-4. Security Audit And Access Review

Goal: make security evidence reviewable.

Functional scope:

- audit views for auth, role changes, export actions and process decisions;
- access review workflow;
- admin report for inactive/excessive roles.

Tests:

- audit event tests;
- access review process tests;
- admin UI tests if screens are touched.

Acceptance criteria:

- access decisions are traceable;
- access review can be run before pilot.

### UI-1. Routed Application Foundation

Goal: replace demo control tower structure with a maintainable routed application.

Functional scope:

- React Router or equivalent project-approved routing;
- feature page layout;
- shared API client;
- loading, empty and error states;
- help-сноски standard component with links to specs and business processes.

Tests:

- route smoke tests;
- API client tests;
- accessibility smoke;
- visual baseline screenshots.

Acceptance criteria:

- pages are independently addressable;
- API calls are centralized;
- UI help standard is reusable.

### UI-2. Forecast And Replenishment Workbenches

Goal: productize core planner workflows with real API calls.

Functional scope:

- forecast review;
- promo uplift review;
- demand projection;
- order proposal approval;
- exception handling.

Tests:

- E2E happy/alternative/error paths;
- form validation;
- process task tests;
- screenshot HTML report.

Acceptance criteria:

- planner can complete core forecast and replenishment workflows through UI;
- actions write audit and process events.

### UI-3. Integration And Data Quality UI

Goal: expose source readiness, DQ blockers and reconciliation to operators.

Functional scope:

- source status screens;
- DQ incident queues;
- retry/reprocess actions;
- reconciliation views.

Tests:

- source late/missing scenarios;
- RBAC and audit tests;
- visual/accessibility tests.

Acceptance criteria:

- data operators can resolve source blockers without database access;
- every action is auditable.

### UI-4. Security, Admin And Process UI

Goal: provide production admin and process operations UI.

Functional scope:

- user/role management;
- service account view;
- access review workflow;
- process task inbox and audit search.

Tests:

- RBAC negative tests;
- admin workflow E2E;
- audit evidence report.

Acceptance criteria:

- admin workflows do not require manual DB edits;
- access and process actions are traceable.

### UI-5. UI E2E Visual Accessibility Suite

Goal: build UI regression safety net for pilot.

Functional scope:

- Playwright E2E per pilot-critical workflow;
- visual screenshots;
- accessibility checks;
- HTML evidence report generation.

Tests:

- smoke, validation, E2E, RBAC, audit, visual regression and accessibility.

Acceptance criteria:

- pilot-critical workflows have automated UI evidence;
- UI regressions are caught in CI.

### ML-1. Training Data Mart And Backtesting

Goal: create real training/backtesting foundation.

Functional scope:

- feature/training marts from real sales, stock, price, promo and MDM data;
- backtesting windows;
- data leakage checks.

Tests:

- data mart DQ;
- leakage tests;
- backtesting reproducibility.

Acceptance criteria:

- 12-24 months of pilot history can be used for backtesting;
- training data is versioned.

### ML-2. Forecast Training And Retraining

Goal: productionize regular and promo forecast training.

Functional scope:

- regular demand training;
- promo uplift training;
- scheduled retraining;
- model artifacts and metadata.

Tests:

- baseline comparison;
- WAPE/Bias backtesting;
- fallback tests.

Acceptance criteria:

- model training is reproducible;
- model is not promoted without metric evidence.

### ML-3. Champion Challenger And Drift

Goal: govern model lifecycle.

Functional scope:

- champion/challenger registry;
- shadow scoring;
- drift monitoring;
- rollback and fallback.

Tests:

- promotion approval tests;
- drift smoke tests;
- rollback tests;
- process audit tests.

Acceptance criteria:

- model promotion is controlled;
- rollback path is tested.

### ML-4. Replenishment Optimization Production

Goal: run demand projection and replenishment on real integrated data.

Functional scope:

- projected stock;
- safety stock;
- service level targets;
- order proposals;
- fresh/shelf-life logic where pilot scope requires it.

Tests:

- order proposal deterministic tests;
- service level and stock cost impact tests;
- stock-out and overstock scenario tests.

Acceptance criteria:

- replenishment produces explainable order proposals for pilot scope;
- no order export happens without approval gate.

### ML-5. EPYC Performance Gate

Goal: validate runtime on target EPYC production profile.

Functional scope:

- production-scale batch benchmark;
- API latency smoke;
- ClickHouse/PostgreSQL load profile;
- capacity report.

Tests:

- forecast/replenishment batch runtime;
- API P95;
- database read/write throughput;
- failure/retry test.

Acceptance criteria:

- daily calculation fits agreed SLA;
- sizing report is updated.

### DEP-1. Environment Topology

Goal: define and implement DEV/TEST/STAGE/PROD topology.

Functional scope:

- Docker Compose for local/dev/test/stage or Kubernetes decision for production;
- env file matrix;
- network and port config through env only;
- deployment diagram.

Tests:

- compose/k8s config validation;
- no hardcoded network test;
- environment smoke.

Acceptance criteria:

- each environment can be deployed reproducibly;
- configuration is centralized.

### DEP-2. CI/CD Release Gates

Goal: make release repeatable.

Functional scope:

- build/test/package pipeline;
- migration gate;
- artifact publishing;
- release notes template.

Tests:

- CI workflow tests;
- migration dry-run;
- frontend/backend build gates.

Acceptance criteria:

- release cannot pass with failing tests or migrations;
- artifacts are traceable to commit.

### DEP-3. Observability And Runbooks

Goal: prepare operations for support.

Functional scope:

- metrics, logs, traces and alerts;
- SLO dashboards;
- incident runbooks;
- on-call checklist.

Tests:

- alert rule tests;
- log/trace propagation smoke;
- runbook drill.

Acceptance criteria:

- support can diagnose source, forecast, replenishment, process and export issues.

### DEP-4. Rollback And DR Drill

Goal: prove production recovery procedures.

Functional scope:

- application rollback;
- migration rollback/forward fix strategy;
- backup restore drill;
- degraded mode drill.

Tests:

- rollback smoke;
- restore smoke;
- degraded run process test.

Acceptance criteria:

- failed release has documented recovery path;
- DR evidence is available before pilot export.

### PILOT-1. Pilot Scope And Data Readiness

Goal: freeze pilot scope and data readiness.

Functional scope:

- selected stores/SKU/categories/suppliers;
- 12-24 month history load;
- pilot business calendar;
- acceptance metric thresholds.

Tests:

- pilot data completeness;
- active matrix coverage;
- historical DQ report.

Acceptance criteria:

- pilot scope is signed;
- data is ready for shadow mode.

### PILOT-2. Shadow Mode

Goal: compare OPEN FNR decisions with current process without operational exports.

Functional scope:

- daily forecast/replenishment shadow run;
- comparison vs current orders/process;
- planner review.

Tests:

- shadow run reproducibility;
- WAPE/Bias/service level proxy;
- UI evidence report.

Acceptance criteria:

- shadow KPI report is accepted by business;
- blockers are triaged.

### PILOT-3. Controlled Export Pilot

Goal: enable limited real exports with rollback.

Functional scope:

- controlled ERP/auto-order export;
- approval gate;
- export status reconciliation;
- rollback and stop switch.

Tests:

- export idempotency;
- retry and failure paths;
- rollback drill.

Acceptance criteria:

- limited export works on approved scope;
- rollback is tested.

### PILOT-4. Business KPI Acceptance

Goal: measure business value.

Functional scope:

- WAPE;
- service level impact;
- lost sales;
- overstock;
- waste where applicable.

Tests:

- KPI calculation reproducibility;
- BI dashboard validation;
- business sign-off pack.

Acceptance criteria:

- KPI evidence is accepted or gap actions are documented.

### PILOT-5. Production Go/No-Go

Goal: make final launch decision.

Functional scope:

- final readiness checklist;
- unresolved risk review;
- production runbook handover;
- go/no-go meeting pack.

Tests:

- final regression;
- security gate;
- DR gate;
- pilot business acceptance gate.

Acceptance criteria:

- production decision is recorded;
- launch or remediation plan is approved.

## 6. Focus Control

The project should run with a single active sprint and at most one preparation sprint in discovery. Any request that adds a new feature must be classified as one of:

| Classification | Action |
| --- | --- |
| Pilot blocker | Add to the current or next sprint with explicit acceptance criteria. |
| Production hardening | Add to the relevant release backlog. |
| Nice to have | Defer after pilot. |
| New product domain | Reject for current plan unless project charter is amended. |

## 7. Recommended Immediate Start

Start with `IH-1 Persistence Inventory And Repository Boundaries`, then `IH-2 PostgreSQL Persistence And Migrations`. This keeps the project focused because real integrations, security, UI actions and pilot exports all need durable state before they can be trusted.
