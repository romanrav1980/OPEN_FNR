# OPEN FNR Source Contracts Freeze

Status: RI-1 frozen baseline  
Date: 2026-05-29  
Scope: real source contracts for POS, ERP, WMS, DWH, MDM and Promo ingestion

## 1. Purpose

This document freezes the source contract baseline required before production ingestion sprints RI-2..RI-6. It complements `DATA_INTEGRATION_SPEC.md` and `REAL_DATA_INGESTION_PIPELINES.md`.

The frozen baseline is machine-checkable through:

- `apps/backend/open_fnr_api/data_contracts.py`;
- `SOURCE_CONTRACT_REGISTRY`;
- `/data/contracts`;
- `tests/data/test_source_contract_freeze.py`.

## 2. Freeze Principles

| Rule | Decision |
| --- | --- |
| One contract name per inbound object | Every pilot source object has a stable `contract_name`. |
| Versioned contracts | The first frozen version is `v1`. Breaking changes require a new version. |
| Idempotent batches | Every batch uses source system, contract name, version, business date and checksum. |
| Reconciliation-ready | Every contract defines reconciliation keys before ingestion implementation. |
| Owner assigned | Every contract has business and technical owner roles. |
| SLA explicit | Every contract declares a source SLA label used by source readiness gates. |
| No network hardcode | Landing locations, hosts, ports and URLs remain in env/config only. |

## 3. Frozen Contract Matrix

| Source | Contract | Model | Primary key | Business owner | Technical owner | Required for |
| --- | --- | --- | --- | --- | --- | --- |
| POS | `pos_sales_line` | `PosSalesLine` | `receipt_id`, `line_id` | Sales Data Owner | Data Engineering | regular forecast, promo forecast, demand projection |
| DWH | `dwh_sales_history_line` | `DwhSalesHistoryLine` | `history_id` | Sales Data Owner | Data Engineering | training history, backtesting, regular forecast, promo forecast |
| WMS | `wms_stock_snapshot_line` | `WmsStockSnapshotLine` | `snapshot_id`, `location_id`, `sku_id` | Supply Chain Data Owner | Data Engineering | projected stock, replenishment, true inventory |
| WMS | `wms_open_order_line` | `WmsOpenOrderLine` | `order_id`, `line_id` | Supply Chain Data Owner | Data Engineering | projected stock, replenishment, multi-echelon |
| WMS | `wms_in_transit_line` | `WmsInTransitLine` | `shipment_id`, `line_id` | Supply Chain Data Owner | Data Engineering | projected stock, replenishment, capacity |
| ERP | `erp_price_line` | `ErpPriceLine` | `price_id` | Commercial Data Owner | Integration Owner | regular forecast, promo forecast, procurement |
| ERP | `erp_order_export_status_line` | `ErpOrderExportStatusLine` | `export_id` | Integration Owner | Integration Owner | publication reconciliation, order status monitoring |
| ERP | `erp_supplier_term_line` | `ErpSupplierTermLine` | `supplier_term_id` | Commercial Data Owner | Integration Owner | replenishment, procurement, supplier collaboration |
| MDM | `mdm_product_line` | `MdmProductLine` | `sku_id` | MDM Data Owner | Data Engineering | assortment, fresh, lifecycle, hierarchy |
| MDM | `mdm_store_line` | `MdmStoreLine` | `store_id` | MDM Data Owner | Data Engineering | store scope, replenishment calendar, routing |
| Promo | `promo_plan_line` | `PromoPlanLine` | `promo_id`, `sku_id`, `store_scope_id` | Promo Planner | Data Engineering | promo forecast, shelf space, display capacity |

## 4. SLA And Blocking Gates

| Contract | SLA label | Blocking checks |
| --- | --- | --- |
| `pos_sales_line` | `before_forecast_cutoff` | schema, row count, checksum, duplicates, referential integrity, freshness |
| `dwh_sales_history_line` | `before_backtesting_cutoff` | schema, row count, checksum, duplicates, referential integrity, date range |
| `wms_stock_snapshot_line` | `before_replenishment_cutoff` | schema, row count, checksum, duplicates, referential integrity, freshness, negative stock |
| `wms_open_order_line` | `before_replenishment_cutoff` | schema, row count, checksum, duplicates, referential integrity, date order |
| `wms_in_transit_line` | `before_replenishment_cutoff` | schema, row count, checksum, duplicates, referential integrity, date order |
| `erp_price_line` | `before_forecast_and_replenishment_cutoff` | schema, row count, checksum, duplicates, referential integrity, price validity |
| `erp_order_export_status_line` | `before_export_reconciliation_cutoff` | schema, row count, checksum, duplicates, status validity, export reconciliation |
| `erp_supplier_term_line` | `before_replenishment_cutoff` | schema, row count, checksum, duplicates, referential integrity, commercial terms validity |
| `mdm_product_line` | `before_master_data_cutoff` | schema, row count, checksum, duplicates, hierarchy integrity, lifecycle validity |
| `mdm_store_line` | `before_master_data_cutoff` | schema, row count, checksum, duplicates, region integrity, calendar integrity |
| `promo_plan_line` | `before_promo_forecast_cutoff` | schema, row count, checksum, duplicates, promo overlap, display capacity |

## 5. DWH Scope

DWH is treated as a historical source during RI-1 freeze and RI-2 implementation. Its pilot role is to provide validated historical extracts aligned to the same canonical sales semantics:

- sales history is frozen as `dwh_sales_history_line`;
- historical prices map to `erp_price_line` where ERP backfill is incomplete;
- historical promo facts map to `promo_plan_line` and downstream promo backtesting marts.

DWH-specific sales history ingestion is implemented in RI-2 through `orchestration/airflow/dags/dwh_sales_history_ingestion.py` and `open_fnr.raw_dwh_sales_history`.

## 6. Acceptance Criteria

RI-1 is accepted when:

- every pilot-required source contract is present in `SOURCE_CONTRACT_REGISTRY`;
- `/data/contracts` exposes the frozen source contract list;
- each contract has owner roles, SLA label, primary key, required fields, idempotency fields and reconciliation keys;
- tests prove the registry matches `PILOT_REQUIRED_SOURCE_CONTRACTS`;
- no host, port, IP address or service URL is hardcoded in the source contract freeze.
