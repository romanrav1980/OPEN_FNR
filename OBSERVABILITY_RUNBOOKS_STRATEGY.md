# OPEN FNR Observability And Runbooks Strategy

Status: DEP-3 foundation  
Date: 2026-05-29  
License posture: self-hosted open-source components only, Apache-2.0 compatible for project code

## 1. Purpose

This document fixes the operational observability scope for OPEN FNR production readiness. It connects metrics, logs, traces, alerts, SLOs, incidents and runbooks into one support model for forecasting, replenishment, integrations, process execution and publication exports.

DEP-3 does not introduce proprietary monitoring tools. The stack remains:

| Layer | Tooling |
| --- | --- |
| Metrics | Prometheus |
| Alerts | Alertmanager |
| Traces | OpenTelemetry |
| Logs | OpenSearch |
| Dashboards | Apache Superset, Apache ECharts UI panels, Prometheus UI |
| Incident workflow | OPEN FNR Process Engine BPMN/CMMN plus `/observability/*` API |

## 2. Operational Coverage

| Domain | What Must Be Observable | Primary Owner | Required Evidence |
| --- | --- | --- | --- |
| Source ingestion | source SLA, row counts, DQ blockers, retries | Data Platform Lead | source readiness, reconciliation, trace id |
| Feature mart | build freshness, dependency status, data version | Data Engineering Lead | feature build run, DQ severity, lineage |
| Forecasting | batch runtime, WAPE/Bias, fallback activation | ML Lead | model run id, backtest id, release gate |
| Replenishment | order proposal completeness, blocked constraints | Replenishment Lead | demand projection, order proposal status |
| Process Engine | active incidents, stuck tasks, SLA breach | Process Owner | process instance id, task owner, audit trail |
| Publication | ERP/WMS/DWH export status, retries, idempotency | Integration Lead | export package id, idempotency key, trace id |

## 3. SLO Catalogue

The backend exposes the current SLO catalogue through:

```text
GET /observability/slo-targets
```

The initial mandatory SLOs are:

| Service | Indicator | Target | Window |
| --- | --- | --- | --- |
| daily-pipeline | successful daily cycle | 99.0% | rolling 30 days |
| forecasting | forecast batch runtime | P95 under the two hour production gate | rolling 14 days |
| publication-export | ERP export latency | P95 under the configured export gate | business day |

All SLO targets must have an owner role and dashboard panel id. Panel ids are logical ids, not network URLs.

## 4. Alert Rules

The backend exposes production alert rule metadata through:

```text
GET /observability/alert-rules
```

Every alert rule must include:

| Field | Requirement |
| --- | --- |
| `rule_id` | Stable unique rule key |
| `service` | Service or business module |
| `severity` | `sev1`, `sev2` or `sev3` |
| `expression` | Human-readable condition or query key |
| `runbook_url` | Relative path under `docs/runbooks/` |
| `owner_role` | Accountable support or business role |
| `process_key` | Related BPMN process key |

No alert rule may depend on a hardcoded host, IP address, port or external dashboard URL.

## 5. Trace And Log Propagation

Each critical daily cycle must propagate:

| Identifier | Why It Matters |
| --- | --- |
| `trace_id` | Connects API, batch, process and export logs |
| `correlation_id` | Connects one business operation across modules |
| `business_key` | Connects incident evidence to SKU/store/date, forecast run or export package |
| `idempotency_key` | Prevents duplicate publication and repeated source loads |

DEP-3 smoke endpoint:

```text
GET /observability/trace-propagation
```

The smoke result must prove that a failed publication export can be traced from alert to log search and incident timeline.

## 6. Incident Runbooks

Runbooks are stored in `docs/runbooks/` and must include:

| Section | Required Content |
| --- | --- |
| Annotation | What is tested or recovered and why |
| Symptoms | How the incident appears to support |
| Evidence | API endpoints, trace/log ids, process instance ids |
| Step-by-step recovery | What the operator does and expected result |
| Escalation | Role, condition and SLA |
| Closure | Audit/timeline evidence required before resolving |

Runbook drill endpoint:

```text
GET /observability/runbook-drills
```

Each drill must document steps, expected result and last result.

## 7. Process Engine Alignment

Runtime BPMN artifact:

- `processes/observability/incident_management_process.bpmn20.xml`

DMN/CMMN remain governed at API layer unless a runtime adapter is explicitly approved. The process must keep the following cognitive control points:

| Control Point | Required Logic |
| --- | --- |
| Severity classification | Always occurs before incident creation |
| Acknowledgement | Human task owned by support |
| Runbook execution | Human task before resolution or escalation |
| Escalation loop | Allows unresolved incidents to return to runbook work |
| Timeline write | Service task before incident closure |

## 8. DEP-3 Acceptance Criteria

DEP-3 is accepted when:

- `/observability/slo-targets`, `/observability/alert-rules`, `/observability/trace-propagation` and `/observability/runbook-drills` are available.
- Alert rules link to runbooks and related process keys.
- Runbook drill proves failed ERP export recovery without duplicate publication.
- Tests verify SLO coverage, alert rule metadata, trace propagation and runbook drill structure.
- Full regression remains green.
