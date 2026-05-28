# Sprint 11 Completion Context

Date: 2026-05-28

## Sprint

Sprint 11. Replenishment Foundation.

## Goal

Build the first replenishment foundation layer: current stock, open orders, in-transit receipts, lead time, demand projection and projected stock by day.

## Completed Functional Scope

- Added backend API module:
  - `apps/backend/open_fnr_api/replenishment.py`
- Added endpoints:
  - `GET /replenishment/stock-snapshots`
  - `GET /replenishment/open-orders`
  - `GET /replenishment/policies`
  - `GET /replenishment/inventory-projections`
  - `GET /replenishment/inventory-projections/{projection_id}`
- Added replenishment concepts:
  - stock snapshot;
  - available stock;
  - open order;
  - in-transit receipt;
  - lead time;
  - safety stock;
  - presentation stock;
  - demand projection;
  - projected stock;
  - stock-out risk.

## Business Process Artifacts

- BPMN: `processes/replenishment/replenishment_calculation_process.bpmn20.xml`
- DMN: `processes/replenishment/stock_projection_quality_decision.dmn.xml`
- CMMN: `processes/replenishment/stock_projection_issue_case.cmmn.xml`

## Business Process Steps

1. Projection is queued.
2. Process loads current stock snapshot.
3. Process loads open orders and in-transit receipts.
4. Process loads demand projection.
5. Process calculates projected stock by day.
6. DMN evaluates stock projection quality.
7. If stock-out or data issue exists, planner review task is created.
8. Projection is published for Order Proposal V1.

## UI Scope

- Added `Inventory Projection` section.
- Added projection summary card.
- Added stock-out warning card.
- Added filters for store, SKU, horizon and safety stock.
- Added projected stock graph.
- Added projection table with demand, open orders, in-transit and risk.

## Verification

- `python -m pytest` -> 87 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- UI screenshot captured:
  - `docs/test-reports/sprint-11-replenishment-foundation/screenshots/inventory-projection.png`

## Test Report

- `docs/test-reports/sprint-11-replenishment-foundation/index.html`

## Remaining Plan

The current execution plan contains Sprint 0 through Sprint 36.

After Sprint 11:

- Completed: 12 sprints.
- Remaining: 25 sprints.
- Approximate time remaining: 68%.

## Next Sprint

Sprint 12. Order Proposal V1.
