# OPEN FNR MDM And Promo Ingestion Specification

Status: RI-5 foundation  
Date: 2026-05-29  
Related sprint: RI-5 MDM And Promo Ingestion

## 1. Purpose

This document fixes the MDM and Promo ingestion foundation required for active assortment, lifecycle, promo forecast, shelf space, display capacity and replenishment routing.

## 2. MDM Contracts

| Contract | Raw table | Critical checks | Downstream use |
| --- | --- | --- | --- |
| `mdm_product_line` | `open_fnr.raw_mdm_products` | hierarchy integrity, lifecycle validity, fresh attributes, supplier reference | assortment, fresh, lifecycle, forecast, replenishment |
| `mdm_store_line` | `open_fnr.raw_mdm_stores` | region integrity, timezone validity, warehouse routing, replenishment calendar | store scope, routing, forecast, replenishment |

## 3. Promo Contract

| Contract | Raw table | Critical checks | Downstream use |
| --- | --- | --- | --- |
| `promo_plan_line` | `open_fnr.raw_promo_plans` | SKU/store scope, date range, promo overlap, price/discount consistency, display location, display capacity | promo forecast, promo order impact, shelf space, capacity |

## 4. Orchestration

MDM DAG:

- `orchestration/airflow/dags/mdm_reference_ingestion.py`;
- manifest creation for product and store contracts;
- schema validation;
- master data DQ;
- quality plan through `build_mdm_quality_plan()`;
- reference publication placeholder.

Promo DAG:

- `orchestration/airflow/dags/promo_plan_ingestion.py`;
- promo plan manifest creation;
- schema validation;
- promo DQ;
- quality plan through `build_promo_quality_plan()`;
- promo publication placeholder.

## 5. Blocking Rules

| Failure | Action |
| --- | --- |
| Missing product MDM | Block active matrix, lifecycle and forecast/replenishment runs. |
| Missing store MDM | Block store scope, routing and replenishment calendar logic. |
| Invalid promo date or overlap | Block promo forecast and promo order impact. |
| Missing display capacity where display is required | Create Promo Planner and Shelf Space recovery task. |
| Invalid promo price or discount | Block promo publication for affected scope. |

## 6. Acceptance Criteria

RI-5 foundation is accepted when:

- MDM and Promo contracts are in `SOURCE_CONTRACT_REGISTRY`;
- raw ClickHouse tables exist for products, stores and promo plans;
- MDM quality plan covers hierarchy, lifecycle and routing;
- Promo quality plan covers overlap, price/discount, display location and display capacity;
- tests cover schemas, contracts and DAG helper behavior.
