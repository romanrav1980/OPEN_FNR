# OPEN FNR Real Integration Operations Specification

Status: RI-6 foundation  
Date: 2026-05-29  
Related sprint: RI-6 Reconciliation, Retries And Source SLA

## 1. Purpose

This document defines the operational gate that connects real source contracts, shadow-load discovery, source-contract DQ, retries, reconciliation and downstream blocking decisions.

## 2. Covered Sources

The operational gate covers all frozen source contracts:

- `pos_sales_line`;
- `dwh_sales_history_line`;
- `wms_stock_snapshot_line`;
- `wms_open_order_line`;
- `wms_in_transit_line`;
- `erp_price_line`;
- `erp_order_export_status_line`;
- `erp_supplier_term_line`;
- `mdm_product_line`;
- `mdm_store_line`;
- `promo_plan_line`.

## 3. API Contracts

| Endpoint | Purpose |
| --- | --- |
| `GET /integration/operations/source-readiness` | Returns per-source readiness, SLA label, owner, blocker/warning counts and recovery action. |
| `GET /integration/operations/retry-plan` | Returns retry plan for blocked sources using the same idempotency key strategy. |
| `GET /integration/operations/reconciliation` | Returns reconciliation keys, downstream blockers and readiness per contract. |

All endpoints accept `business_date` and optional `landing_root_path`. Runtime source paths remain configured through `OPEN_FNR_LANDING_ROOT_PATH`; explicit request override is for controlled tests and rehearsals.

## 4. Process Behavior

| Condition | Status | Process action |
| --- | --- | --- |
| Source files missing | blocked | Create source batch recovery task and request resend. |
| Source files empty | blocked | Create DQ blocker task and stop clean publication. |
| Source files present and DQ passes | ready | Allow clean publication gate. |
| Warning-only DQ | warning | Allow controlled continuation with monitoring. |
| Reconciliation blocked | blocked | Stop downstream forecast/replenishment/publication for affected contract. |

## 5. Retry And Idempotency

Retries must use the same idempotency key format:

```text
source_system:contract_name:contract_version:business_date
```

The retry strategy is `same_idempotency_key_no_duplicate_clean_rows`. Clean publication must remain idempotent through delete-by-source-batch-then-insert or an equivalent repository transaction.

## 6. Acceptance Criteria

RI-6 foundation is accepted when:

- source readiness includes all frozen contracts;
- DWH sales history and ERP supplier terms are included in shadow-load and DQ gates;
- retry plan is generated for blocked sources;
- reconciliation response exposes keys and downstream blockers;
- tests cover missing-source and complete-pilot-pack paths;
- no host, port, IP address or service URL is hardcoded.
