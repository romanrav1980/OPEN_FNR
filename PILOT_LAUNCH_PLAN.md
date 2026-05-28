# OPEN FNR Pilot Launch Plan

Date: 2026-05-28

## Goal

Prepare and run a controlled OPEN FNR pilot on a limited set of stores, categories and SKU before industrial rollout.

## Pilot Scope Recommendation

| Dimension | Recommended scope |
| --- | --- |
| Stores | 30-100 stores |
| Categories | 2-4 categories, including one fresh category if data is ready |
| SKU | 500-2,000 active SKU |
| Suppliers | 5-20 key suppliers |
| Forecast horizon | 14 and 30 days first |
| Run mode | shadow mode first, controlled export second |
| Duration | 8-12 weeks |

## Pilot Phases

| Phase | Duration | Goal | Exit criteria |
| --- | --- | --- | --- |
| P0 Readiness | 2 weeks | data, security, UI and process readiness | stage go/no-go signed |
| P1 Shadow | 3-4 weeks | compare forecasts/orders with current process | KPI baseline measured |
| P2 Assisted Planning | 2-3 weeks | planners use UI, exports still controlled | business workflow accepted |
| P3 Controlled Export | 2-4 weeks | limited real exports to ERP/WMS | no critical incidents, KPI uplift visible |
| P4 Scale Decision | 1 week | decide next rollout wave | go/no-go signed |

## Required Inputs

- Pilot store list.
- Pilot SKU/category list.
- Historical sales for 12-24 months.
- Stock snapshots and in-transit/open orders.
- Price history.
- Promo history and future promo plans.
- Product/store MDM.
- Supplier contracts and lead times.
- Current baseline process metrics.

## Pilot KPIs

| KPI | Measurement |
| --- | --- |
| WAPE | forecast error by store/SKU/day and aggregate levels |
| Bias | systematic over/under forecast |
| Service level | availability improvement |
| Lost sales | reduction vs baseline |
| Overstock | excess inventory reduction |
| Waste | fresh spoilage reduction |
| Planner adoption | accepted proposals, manual adjustments, task completion |
| Process SLA | tasks completed before cutoff |

## Pilot Governance

| Role | Responsibility |
| --- | --- |
| Product Owner | pilot scope and acceptance |
| Forecast Owner | forecast quality and model approval |
| Replenishment Owner | order proposal acceptance |
| Data Owner | data quality and source corrections |
| IT Owner | environments, integrations and security |
| Store Operations | store tasks and stock feedback |
| Supplier Coordinator | supplier confirmation and shortage handling |

## Go/No-Go Checklist

- Real data loads are stable.
- DQ blockers are below agreed threshold.
- Users can authenticate and access only their scope.
- Core UI workflows pass UAT.
- Process Engine tasks and audits are visible.
- ERP/WMS exports are tested in dry run.
- Rollback plan is approved.
- Support runbook is ready.

## Pilot Exit Criteria

- Business confirms usability.
- KPI impact is measured against baseline.
- Critical incidents are resolved or accepted.
- Integration reliability is acceptable.
- Security and audit requirements pass.
- Next rollout wave is approved or remediation plan is created.
