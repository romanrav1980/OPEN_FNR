# Sprint 12 Completion Context

Date: 2026-05-28

## Sprint

Sprint 12. Order Proposal V1.

## Goal

Generate explainable order proposals from inventory projection, with gross requirement, net requirement, safety stock, presentation stock, MOQ/rounding, constraint flags and auto/manual/blocked statuses.

## Completed Functional Scope

- Added order proposal API:
  - `GET /replenishment/order-proposals`
  - `GET /replenishment/order-proposals/{proposal_id}`
- Added formula components:
  - gross requirement;
  - projected stock at receipt;
  - safety stock;
  - presentation stock;
  - net requirement;
  - raw order quantity;
  - rounded order quantity;
  - MOQ;
  - order multiple;
  - constraint flags.
- Added proposal statuses:
  - `draft`;
  - `auto_approved`;
  - `manual_review`;
  - `blocked`.

## Business Process Artifacts

- BPMN: `processes/replenishment/order_proposal_generation_process.bpmn20.xml`
- DMN: `processes/replenishment/order_auto_approval_decision.dmn.xml`
- DMN: `processes/replenishment/order_constraint_decision.dmn.xml`
- CMMN: `processes/replenishment/supplier_constraint_case.cmmn.xml`

## Business Process Steps

1. Inventory projection is published.
2. Process calculates gross requirement.
3. Process calculates net requirement.
4. DMN evaluates supplier and calendar constraints.
5. Process applies MOQ and order multiple rounding.
6. DMN routes proposal to auto-approved, manual review or blocked.
7. Manual review task is created if risk flags exist.
8. Supplier constraint case is opened if supplier/calendar blocks order.

## UI Scope

- Added `Order Proposal V1` section.
- Added selected proposal card.
- Added formula breakdown card.
- Added proposal table with statuses and flags.
- Added explanation drawer.
- Added constraint/action panel.

## Verification

- `python -m pytest` -> 94 passed.
- `npm.cmd run build` in `apps/frontend` -> completed.
- UI screenshot captured:
  - `docs/test-reports/sprint-12-order-proposal-v1/screenshots/order-proposal-v1.png`

## Test Report

- `docs/test-reports/sprint-12-order-proposal-v1/index.html`

## Remaining Plan

The current execution plan contains Sprint 0 through Sprint 36.

After Sprint 12:

- Completed: 13 sprints.
- Remaining: 24 sprints.
- Approximate time remaining: 65%.

## Next Sprint

Sprint 13. Replenishment Workbench V1.
