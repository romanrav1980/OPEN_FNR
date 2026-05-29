# OPEN FNR WMS Inventory Ingestion Specification

Status: RI-3 foundation  
Date: 2026-05-29  
Related sprint: RI-3 WMS Stock, In-Transit And Open Orders

## 1. Purpose

This document fixes the WMS ingestion foundation required for projected stock, replenishment, multi-echelon planning and capacity checks.

## 2. Covered Contracts

| Contract | Raw table | Downstream use | Reconciliation keys |
| --- | --- | --- | --- |
| `wms_stock_snapshot_line` | `open_fnr.raw_wms_stock_snapshots` | projected stock, replenishment, true inventory | `business_date`, `location_id`, `sku_id` |
| `wms_open_order_line` | `open_fnr.raw_wms_open_orders` | projected stock, replenishment, multi-echelon | `order_id`, `line_id`, `sku_id` |
| `wms_in_transit_line` | `open_fnr.raw_wms_in_transit` | projected stock, replenishment, capacity | `shipment_id`, `line_id`, `sku_id` |

## 3. Orchestration

The Airflow DAG `orchestration/airflow/dags/wms_inventory_ingestion.py` defines:

- manifest creation per WMS contract;
- schema validation step;
- DQ step;
- reconciliation step through `build_wms_reconciliation_plan()`;
- clean inventory publication placeholder.

## 4. Blocking Rules

| Failure | Action |
| --- | --- |
| Missing stock snapshot | Block projected stock and replenishment. |
| Missing open orders | Block replenishment and multi-echelon calculation. |
| Missing in-transit data | Block projected stock and capacity-sensitive order proposals. |
| Stale WMS input | Create Supply Chain Data Owner recovery task. |
| Reconciliation mismatch | Stop clean publication for the affected business date. |

## 5. Acceptance Criteria

RI-3 foundation is accepted when:

- all three WMS contracts are in `SOURCE_CONTRACT_REGISTRY`;
- raw ClickHouse tables exist for stock snapshots, open orders and in-transit;
- WMS DAG exposes an idempotent manifest per contract;
- WMS reconciliation plan defines keys, downstream blockers and SLA labels;
- tests cover schemas, contracts and DAG helper behavior.
