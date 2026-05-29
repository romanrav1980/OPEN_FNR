# OPEN FNR Pilot Shadow Mode Specification

Status: PILOT-2 foundation  
Date: 2026-05-29

## 1. Purpose

Shadow mode compares OPEN FNR forecasts and replenishment decisions with the current legacy process without sending operational exports to ERP or auto-order systems.

The goal is to prove forecast/replenishment value, expose business exceptions and collect planner feedback before controlled export is enabled.

## 2. Backend Contract

Shadow mode endpoints:

```text
GET /pilot/shadow-runs
GET /pilot/shadow-runs/{run_id}
```

Every shadow run must include:

| Field | Requirement |
| --- | --- |
| `mode` | Must be `shadow` |
| `export_enabled` | Must be `false` |
| `compared_orders` | Number of order lines compared with legacy/current process |
| `metrics` | WAPE, Bias, service-level proxy and order quantity delta |
| `exceptions` | SKU/store business exceptions for planner review |
| `planner_actions` | Required user actions before business review |
| `ready_for_business_review` | True only when comparison can be reviewed by business |

## 3. Business Process

Shadow mode follows the existing `pilot_operational_process`:

1. Review pilot forecast.
2. Review order proposal differences against current process.
3. Collect planner feedback.
4. Evaluate pilot thresholds.
5. Triage issues or prepare acceptance evidence.

Operational exports remain blocked throughout PILOT-2.

## 4. Test Requirements

PILOT-2 tests must verify:

- shadow runs never enable exports;
- OPEN FNR metrics are compared with legacy/current process values;
- WAPE, Bias, service-level proxy and order quantity delta are present;
- planner exceptions include store, SKU, reason, recommended action and owner role;
- unknown run ids return a controlled 404;
- full regression remains green.

## 5. Acceptance Criteria

PILOT-2 is accepted when:

- `/pilot/shadow-runs` and `/pilot/shadow-runs/{run_id}` are available;
- shadow report is ready for business review;
- critical export paths remain disabled;
- exceptions are visible for planner review;
- tests and full regression pass.
