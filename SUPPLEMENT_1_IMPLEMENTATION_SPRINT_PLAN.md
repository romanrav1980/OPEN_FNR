# OPEN FNR Supplement 1 Implementation Sprint Plan

Status: accepted planning baseline after `TECHNICAL_SPEC_SUPPLEMENT_1.md`.
Date: 2026-05-29.
License boundary: only free self-hosted open-source tools compatible with Apache 2 project distribution. No proprietary, AGPL, GPL, SSPL, BUSL or SaaS dependencies.

## 1. Purpose

This document breaks `TECHNICAL_SPEC_SUPPLEMENT_1.md` into executable implementation sprints. The supplement is already adopted as a mandatory addendum through `SUPPLEMENT_1_ADOPTION_MATRIX.md`; this plan defines how the remaining controls are converted into production-grade functionality, tests, reports and business sign-off gates.

## 2. Planning Principles

| Principle | Decision |
| --- | --- |
| Supplement-first governance | Supplement 1 has priority where it defines operational governance and production acceptance requirements. |
| Process-first implementation | Every human approval, exception and escalation is modeled through OPEN FNR Process Engine, not hardcoded in business services. |
| Evidence by default | Each sprint must produce API tests, process tests and HTML evidence report when UI or process execution is touched. |
| Config over hardcode | Ports, IP addresses, URLs, SLA thresholds and integration endpoints must come from common project configuration. |
| UTF-8 safety | New text artifacts are UTF-8, LF line endings, and covered by encoding checks. |
| Runtime boundary clarity | BPMN is runtime-deployed to Flowable. DMN/CMMN remain governed artifacts until their runtime adapters are explicitly approved. |

## 3. Release Map

```mermaid
flowchart LR
    S0[SUP-0 Adoption completed] --> S1[SUP-1 Source SLA]
    S1 --> S2[SUP-2 ML lifecycle]
    S2 --> S3[SUP-3 Replenishment finance]
    S3 --> S4[SUP-4 Simulation and acceptance]
    S4 --> S5[SUP-5 API and integration governance]
    S5 --> S6[SUP-6 Supplier isolation]
    S6 --> S7[SUP-7 Notifications and ITSM]
    S7 --> S8[SUP-8 DR BC and lineage]
    S8 --> S9[SUP-9 Process Navigator Map]
    S9 --> S10[SUP-10 Pilot production gate]
```

## 4. Sprint Table

| Sprint | Name | Main outcome | Status |
| --- | --- | --- | --- |
| SUP-0 | Supplement Adoption | A-M sections exposed as governance gates | Completed |
| SUP-1 | Source SLA Runtime Controls | Source SLA evaluation controls pipeline start/publication | Planned |
| SUP-2 | ML Lifecycle Runtime Controls | Candidate/shadow/champion/fallback gates become enforceable | Planned |
| SUP-3 | Replenishment Financial Parameters | Signed business parameters drive safety stock and cost optimization | Planned |
| SUP-4 | Historical Simulation And Acceptance | 52-week simulation, shadow, parallel run and controlled pilot evidence | Planned |
| SUP-5 | API Versioning And Consumer Registry | Versioned APIs, deprecation, error registry and consumer ownership | Planned |
| SUP-6 | Supplier Isolation And Data Classification | Supplier API isolation, C1-C4 classification and object-level controls | Planned |
| SUP-7 | Notification, SLA And ITSM Escalation | Human task SLA, notification channels and ITSM incidents | Planned |
| SUP-8 | Lineage, Retention And DR/BC | Lineage, retention, backup/restore and degraded operations evidence | Planned |
| SUP-9 | Process Navigator Map | Zoomable business-process map with alerts, drill-down and BPMN quality | Started |
| SUP-10 | Pilot Production Gate | Unified go/no-go gate for limited pilot launch | Planned |

## 5. Detailed Sprints

### SUP-0. Supplement Adoption

Status: completed.

Delivered:

- `TECHNICAL_SPEC_SUPPLEMENT_1.md` accepted as mandatory addendum.
- `SUPPLEMENT_1_ADOPTION_MATRIX.md` created.
- `/supplement/*` API gates implemented.
- Admin UI shows Supplement 1 coverage.
- Regression test coverage added.

Acceptance evidence:

- `tests/backend/test_supplement_governance.py`
- `docs/test-reports/sprint-supplement-1-adoption/index.html`

### SUP-1. Source SLA Runtime Controls

Goal: turn Supplement section A into daily executable controls.

Functional scope:

- persist source SLA agreements for POS, WMS, ERP, MDM, promo and external factors;
- calculate source readiness before daily pipeline start;
- mark degraded mode with `quality_flag`;
- block publication by default when `degraded_publish_allowed=false`;
- create Process Engine tasks for source owners.

Process Engine:

| Artifact | Description |
| --- | --- |
| BPMN | `source_sla_breach_process`: detect breach, wait until cutoff, decide degraded mode, open remediation task |
| DMN | `source_sla_publish_decision`: publish blocked, manual confirmation, or degraded publish allowed |
| CMMN | `source_sla_recovery_case`: resend data, approve reprocessing, approve waiver, close incident |

Tests:

| Test class | Required checks |
| --- | --- |
| UI | SLA matrix, source owner filters, degraded warning, manual publish confirmation, RBAC |
| Process | happy path, late source, incomplete source, waiver, escalation, audit trail |
| Data | freshness, row count, source completeness, duplicate batches, idempotency |
| Integration | POS/WMS/ERP/MDM/promo mocks, retry, replay, invalid file handling |
| Performance | Airflow DAG runtime, PostgreSQL process throughput, ClickHouse source status reads |

Acceptance criteria:

- daily pipeline cannot silently use late or incomplete source data;
- each breach has owner, status, SLA, audit and next action;
- no endpoint or batch job contains hardcoded source URLs, ports or IP addresses.

### SUP-2. ML Lifecycle Runtime Controls

Goal: make Supplement section B enforceable for model release and rollback.

Functional scope:

- model stages `EXPERIMENT -> CANDIDATE -> SHADOW -> CHAMPION/CHALLENGER -> RETIRED`;
- 26-week backtesting gate;
- 14-day shadow protocol;
- emergency rollback within 1 hour;
- fallback chain and model-tier labeling.

Process Engine:

| Artifact | Description |
| --- | --- |
| BPMN | `model_lifecycle_release_process`: candidate registration, backtest approval, shadow launch, champion promotion |
| DMN | `model_release_gate_decision`: approve, shadow, block, rollback |
| CMMN | `model_emergency_rollback_case`: triage, rollback approval, publication freeze, incident closure |

Tests:

| Test class | Required checks |
| --- | --- |
| ML | WAPE/Bias baseline comparison, backtesting reproducibility, drift smoke, fallback |
| Process | candidate rejection, shadow completion, rollback path, DS approval, audit |
| UI | model card, shadow report, champion/challenger comparison, rollback action |
| Performance | model metrics aggregation runtime, shadow result write volume |

Acceptance criteria:

- no model can become champion without evidence;
- all production forecasts expose `model_tier` and `quality_flag`;
- rollback produces auditable event chain and publication impact summary.

### SUP-3. Replenishment Financial Parameters

Goal: implement Supplement section C as governed inputs to replenishment.

Functional scope:

- category/service-level parameter registry;
- holding, waste, lost sales and order cost parameters;
- approval workflow by CFO, Commercial Director and Supply Chain Director;
- versioning and effective dates;
- use parameters in safety stock and optimization APIs.

Process Engine:

| Artifact | Description |
| --- | --- |
| BPMN | `replenishment_finance_parameter_approval_process` |
| DMN | `financial_parameter_completeness_decision` |
| CMMN | `financial_parameter_dispute_case` |

Tests:

| Test class | Required checks |
| --- | --- |
| UI | parameter form validation, effective dates, approval route, history |
| Process | approve, reject, request rework, expired parameter, audit |
| Data | referential integrity to category/SKU/store segments |
| Performance | bulk parameter lookup during replenishment runtime |

Acceptance criteria:

- production replenishment cannot use unsigned financial parameters;
- parameter changes are versioned and auditable;
- service-level targets are visible in order proposal explanation.

### SUP-4. Historical Simulation And Acceptance

Goal: satisfy Supplement sections D and J before parallel run.

Functional scope:

- 52-week historical replenishment simulation;
- matched store/SKU control group;
- shadow mode and parallel run reports;
- acceptance sign-off gates.

Process Engine:

| Artifact | Description |
| --- | --- |
| BPMN | `historical_simulation_acceptance_process` |
| DMN | `business_acceptance_gate_decision` |
| CMMN | `simulation_exception_case` |

Tests:

| Test class | Required checks |
| --- | --- |
| ML/Data | backtest windows, leakage guard, WAPE/Bias, simulation completeness |
| Process | simulation fail, business rejection, controlled pilot approval |
| UI | simulation report, KPI deltas, sign-off panel |
| Performance | Spark/Polars runtime and ClickHouse write volume |

Acceptance criteria:

- simulation report exists in `docs/simulation-reports/`;
- pilot cannot start without signed shadow/parallel evidence;
- report includes service level, lost sales, overstock and waste impact.

### SUP-5. API Versioning And Consumer Registry

Goal: make Supplement section G operational.

Functional scope:

- `/api/v{major}/` contracts for production consumers;
- standard error model;
- consumer registry and owner contacts;
- 90-day deprecation workflow;
- idempotency keys for exports.

Process Engine:

| Artifact | Description |
| --- | --- |
| BPMN | `api_deprecation_management_process` |
| DMN | `api_change_risk_decision` |
| CMMN | `api_consumer_exception_case` |

Tests:

| Test class | Required checks |
| --- | --- |
| API | OpenAPI contracts, standard errors, deprecation headers, idempotency |
| Integration | ERP/WMS/DWH/autozakaz mocks, retry, duplicate export |
| Security | service account, object-level access, audit |
| UI | consumer registry, API health and export status |

Acceptance criteria:

- no production consumer uses unversioned API;
- breaking API change requires registered impact analysis;
- export errors are traceable to consumer and process task.

### SUP-6. Supplier Isolation And Data Classification

Goal: implement Supplement section H.

Functional scope:

- C1-C4 classification in data contracts;
- supplier API with mandatory `supplier_id` claim;
- object-level supplier isolation;
- audit of every supplier request.

Process Engine:

| Artifact | Description |
| --- | --- |
| BPMN | `supplier_access_review_process` |
| DMN | `supplier_data_visibility_decision` |
| CMMN | `supplier_data_leak_case` |

Tests:

| Test class | Required checks |
| --- | --- |
| Security | supplier cannot read another supplier, no missing claim, audit |
| API | supplier forecast/order endpoints, pagination, rate limits |
| Process | access request, revoke, incident |
| UI | supplier workspace denied/allowed states |

Acceptance criteria:

- supplier data leak scenario is blocked by tests;
- every supplier request has `supplier_id`, actor, endpoint and object scope in audit.

### SUP-7. Notification, SLA And ITSM Escalation

Goal: implement Supplement section K.

Functional scope:

- notification routing by event type;
- human task SLA registry;
- ITSM webhook integration through configuration;
- escalation policies and alert deduplication.

Process Engine:

| Artifact | Description |
| --- | --- |
| BPMN | `notification_escalation_process` |
| DMN | `notification_route_decision` |
| CMMN | `notification_delivery_failure_case` |

Tests:

| Test class | Required checks |
| --- | --- |
| Process | SLA breach, escalation, acknowledge, delivery failure |
| Integration | ITSM mock, retry, dedupe, timeout |
| UI | alert center, owner filter, status transitions |
| Performance | alert burst load, OpenSearch logging load |

Acceptance criteria:

- source SLA breach notification is delivered within configured max minutes;
- ITSM target is never hardcoded and is safe when unset;
- every alert links to process, owner and runbook.

### SUP-8. Lineage, Retention And DR/BC

Goal: implement Supplement sections E and F as production controls.

Functional scope:

- dataset lineage from raw source to published forecast/order;
- retention policy by data class;
- backup/restore rehearsal;
- degraded mode runbook and RPO/RTO checks.

Process Engine:

| Artifact | Description |
| --- | --- |
| BPMN | `dr_rehearsal_process` |
| DMN | `retention_policy_decision` |
| CMMN | `restore_exception_case` |

Tests:

| Test class | Required checks |
| --- | --- |
| Data | lineage completeness, retention policy, restore sample consistency |
| Process | quarterly DR rehearsal, failed restore, degraded mode |
| Performance | restore runtime and backup throughput |
| Security | encrypted backups, access to restore artifacts |

Acceptance criteria:

- every published forecast/order can be traced to source batch and model version;
- RPO/RTO evidence is recorded before production launch.

### SUP-9. Process Navigator Map

Goal: make business-process execution visible as a zoomable control map.

Functional scope:

- backend API `/process-navigator/map`, `/process-navigator/alerts`, `/process-navigator/processes/{key}/drilldown`;
- semantic zoom from domain cluster to process, BPMN step, task and audit timeline;
- overlays for BPMN quality, SLA, source breach, model drift and integration failures;
- UI module for Process Navigator.

Process Engine:

| Artifact | Description |
| --- | --- |
| BPMN | Reuses existing BPMN artifacts and deployment metadata |
| DMN | Reuses decision artifacts for route and gate explanation |
| CMMN | Reuses exception cases as alert drill-down target |

Tests:

| Test class | Required checks |
| --- | --- |
| API | map zoom levels, alerts, BPMN drill-down, non-BPMN rejection |
| UI | pan/zoom, filters, drill-down, alert overlay, keyboard navigation |
| Process | selected process has owner/SLA/audit evidence |
| Performance | map response under target latency for 100+ process artifacts |

Acceptance criteria:

- map shows where process execution is healthy, degraded or blocked;
- user can drill from domain to BPMN step and related task/audit;
- no new proprietary dependency is introduced.

### SUP-10. Pilot Production Gate

Goal: combine Supplement 1 gates into a pilot go/no-go decision.

Functional scope:

- pilot readiness aggregation;
- blocker/warning matrix;
- sign-off workflow;
- rollback package;
- final developer/user presentation with screenshots.

Process Engine:

| Artifact | Description |
| --- | --- |
| BPMN | `pilot_production_go_no_go_process` |
| DMN | `pilot_go_no_go_decision` |
| CMMN | `pilot_blocker_case` |

Tests:

| Test class | Required checks |
| --- | --- |
| E2E | source data to forecast to replenishment to export |
| UI | readiness board, process map, approvals, reports |
| Load | batch under SLA, API latency, Flowable throughput |
| Security | real roles, service accounts, object-level access |

Acceptance criteria:

- all mandatory Supplement 1 gates are passed or explicitly waived by accountable role;
- pilot scope, rollback and support runbook are signed;
- final presentation and test evidence are available.

## 6. Cross-Sprint Definition Of Done

- Code, migrations, process artifacts, API contracts and docs are committed.
- Backend, process and quality tests pass for touched areas.
- UI build and UI test report are produced when UI is changed.
- Business-process test report explains what was tested, why, expected result and actual result.
- New configuration is exposed through common settings and environment files.
- No hardcoded IP addresses, ports, credentials or external URLs.
- BPMN models pass cognitive quality checks before release.

## 7. Sources Considered For Process Navigation

- Flowable Open Source REST and History APIs: https://www.flowable.com/open-source/docs/bpmn/ch14-REST and https://www.flowable.com/open-source/docs/bpmn/ch10-History
- BPMN 2.0.2 official specification: https://www.omg.org/spec/BPMN/2.0.2
- bpmn-js toolkit for web BPMN rendering: https://bpmn.io/toolkit/bpmn-js
- Apache ECharts graph/roam and SVG map capabilities: https://echarts.apache.org/handbook/en/concepts/event/ and https://echarts.apache.org/handbook/en/how-to/component-types/geo/svg-base-map/
