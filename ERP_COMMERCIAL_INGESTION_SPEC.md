# OPEN FNR ERP Commercial Ingestion Specification

Status: RI-4 foundation  
Date: 2026-05-29  
Related sprint: RI-4 ERP Prices, Suppliers And Order Status

## 1. Purpose

This document fixes the ERP ingestion foundation required for forecast price features, replenishment commercial parameters, procurement optimization and export reconciliation.

## 2. Covered Contracts

| Contract | Raw table | Downstream use | Reconciliation keys |
| --- | --- | --- | --- |
| `erp_price_line` | `open_fnr.raw_erp_prices` | regular forecast, promo forecast, replenishment | `sku_id`, `location_scope`, `valid_from` |
| `erp_supplier_term_line` | `open_fnr.raw_erp_supplier_terms` | replenishment, procurement, supplier collaboration | `supplier_id`, `sku_id`, `location_scope`, `valid_from` |
| `erp_order_export_status_line` | `open_fnr.raw_erp_order_export_statuses` | publication reconciliation, order status monitoring | `export_id`, `proposal_id`, `external_order_id` |

## 3. Orchestration

The Airflow DAG `orchestration/airflow/dags/erp_commercial_ingestion.py` defines:

- manifest creation per ERP contract;
- schema validation step;
- DQ step;
- reconciliation step through `build_erp_reconciliation_plan()`;
- commercial data publication placeholder.

## 4. Blocking Rules

| Failure | Action |
| --- | --- |
| Missing prices | Block forecast price features and replenishment price-sensitive calculations. |
| Missing supplier terms | Block order proposal publication and procurement optimization. |
| Missing order export status | Block export reconciliation and create Integration Owner recovery task. |
| Invalid lead time, MOQ or pack size | Stop replenishment publication for affected supplier/SKU/scope. |

## 5. Acceptance Criteria

RI-4 foundation is accepted when:

- ERP price, supplier term and order export status contracts are in `SOURCE_CONTRACT_REGISTRY`;
- raw ClickHouse tables exist for prices, supplier terms and order export statuses;
- ERP DAG exposes idempotent manifests per contract;
- ERP reconciliation plan defines keys, downstream blockers and SLA labels;
- tests cover schemas, contracts and DAG helper behavior.
