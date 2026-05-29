# RI-4 Completion Note

Status: completed foundation  
Date: 2026-05-29  
Sprint: RI-4 ERP Prices, Suppliers And Order Status

## Scope Completed

- ERP supplier terms contract added:
  - `ErpSupplierTermLine`;
  - `erp_supplier_term_line`;
  - lead time, MOQ, pack size and order calendar fields.
- Raw ClickHouse schema added:
  - `open_fnr.raw_erp_supplier_terms`.
- ERP manifest endpoint added:
  - `GET /data/ingestion/manifests/erp-supplier-terms`.
- ERP Airflow DAG now includes:
  - price manifest;
  - supplier terms manifest;
  - order export status manifest;
  - reconciliation plan step.
- ERP ingestion specification added:
  - `ERP_COMMERCIAL_INGESTION_SPEC.md`.

## Evidence

- Targeted tests cover ERP manifests, supplier terms validation, reconciliation plan and raw schemas.
- Targeted tests: 33 passed.
- Full regression: 499 passed, 1 local `.pytest_cache` permission warning.

## Deferred

- Actual enterprise ERP connector.
- Real order status pull/push adapter.
- Supplier terms reconciliation against MDM supplier master.

These are deferred to RI-6 and production integration hardening because RI-4 establishes the contract, schema and orchestration boundary.
