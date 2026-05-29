# OPEN FNR Forecast And Replenishment Workbenches Specification

Status: UI-2 foundation  
Date: 2026-05-29  
Related sprint: UI-2 Forecast And Replenishment Workbenches

## 1. Purpose

This document fixes the UI-2 productization scope for the planner workbenches that connect forecast review, promo uplift, demand projection, order proposal review and replenishment actions.

## 2. Functional Scope

| Area | UI capability | Backend contract | Process/audit expectation |
| --- | --- | --- | --- |
| Forecast review | Forecast Workbench route section with KPI cards, forecast rows and planner review context | `/forecast/workbench` | Forecast review uses process task context and preserves ML baseline separately from manual overlays. |
| Promo uplift review | Promo workbench and promo forecast sections with required promo fields, reference promos and regular/uplift/total split | `/promo/forecasts` | Promo cannot progress when mandatory SKU, store, price, discount, period or display attributes are incomplete. |
| Demand projection | Inventory projection section with demand, stock, open orders, in-transit and safety threshold | `/replenishment/inventory-projections` | Projection blockers create review tasks and linked exception cases. |
| Order proposal approval | Order Proposal V1 and Replenishment Workbench sections with formula, constraints, adjusted quantity and approval state | `/replenishment/order-proposals`, `/replenishment/workbench` | Planner changes must keep original proposal, adjusted final order and audit event. |
| Exception handling | Exception Center and Manual Adjustments sections with linked objects and reason/comment requirements | `/adjustments`, process task APIs | Every action requires actor, role, reason where needed and audit trail. |

## 3. UI Requirements

- Workbench sections must be reachable through `#/forecast` and `#/replenishment`.
- API calls must use the shared `apiUrl(...)` helper from `apps/frontend/src/app_config.ts`.
- Planner actions must expose loading, denied, validation or conflict states in the UI flow.
- Help footnotes must link relevant controls to the technical specification, business process documentation, BPMN/DMN/CMMN artifacts or sprint evidence.
- Tables must show stable identifiers for forecast version, promo id, projection id, order proposal id and audit event linkage.
- UI text must avoid hardcoded service URLs, IP addresses, hostnames and port numbers.

## 4. Business Process Coverage

| Process | User journey | Required evidence |
| --- | --- | --- |
| Forecast review | Forecast Planner reviews baseline, KPI status, SKU detail and adjustment impact before publication. | UI section, API contract, audit/process note. |
| Promo uplift approval | Promo Planner validates commercial and display attributes, reviews uplift and resolves conflicts. | Required-field table, reference promo panel, approval timeline. |
| Replenishment review | Replenishment Planner reviews projected stock, constraints and final order before approval/export. | Projection chart, order formula, adjustment/audit trail. |
| Exception resolution | Owner reviews linked exception, enters reason/comment and resolves or escalates. | Exception panel and audit trail. |

## 5. Test Requirements

| Test class | Required checks |
| --- | --- |
| UI smoke | Forecast/replenishment route sections and critical headings are present. |
| API wiring | Workbenches call only shared config helpers and existing API contracts. |
| Process audit | UI contains audit trail, reason/comment and original-vs-adjusted evidence. |
| Validation | Promo required fields, order constraints and denied/blocked states are visible. |
| Accessibility smoke | Sections have accessible labels and action context. |
| Quality gate | No hardcoded network configuration in frontend source. |

## 6. Acceptance Criteria

UI-2 foundation is accepted when:

- forecast and replenishment workbenches are represented in the routed UI;
- core planner workflows are connected to backend API contracts;
- promo uplift, projected stock, order proposals, adjustments and exceptions are visible in one planner journey;
- process and audit expectations are explicit;
- automated static UI coverage and frontend build pass.
