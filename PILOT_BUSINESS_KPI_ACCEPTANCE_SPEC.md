# OPEN FNR Pilot Business KPI Acceptance Specification

Status: PILOT-4 foundation  
Date: 2026-05-29

## 1. Purpose

PILOT-4 converts pilot results into a business acceptance pack. The pack must show whether OPEN FNR delivers measurable value on forecast accuracy, availability, lost sales, overstock and fresh waste.

## 2. Backend Contract

Acceptance endpoint:

```text
GET /kpi/pilot-acceptance
```

The response must include:

| Field | Requirement |
| --- | --- |
| `scope_id` | Signed pilot scope |
| `period_start`, `period_end` | Pilot measurement window |
| `metrics` | WAPE, service level, lost sales, overstock, waste |
| `reproducibility_evidence` | Scope, data version, run ids and formula test evidence |
| `sign_off_roles` | Business and technical acceptance roles |
| `blockers` | Failed metrics or evidence gaps |
| `decision` | `accepted` or `blocked` |

## 3. Metric Rules

| Metric | Direction |
| --- | --- |
| WAPE | Value must be less than or equal to threshold |
| Service level | Value must be greater than or equal to threshold |
| Lost sales reduction | Value must be greater than or equal to threshold |
| Overstock reduction | Value must be greater than or equal to threshold |
| Waste reduction | Value must be greater than or equal to threshold |

## 4. Reproducibility

The acceptance pack must record enough evidence to reproduce the calculation:

- frozen pilot scope id;
- source data version;
- forecast run id;
- order proposal run id;
- automated KPI formula tests.

## 5. Acceptance Criteria

PILOT-4 is accepted when:

- `/kpi/pilot-acceptance` is available;
- all required business metrics are present;
- failed metrics become blockers;
- sign-off roles are visible;
- full regression remains green.
