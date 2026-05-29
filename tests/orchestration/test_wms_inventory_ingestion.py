from orchestration.airflow.dags.wms_inventory_ingestion import build_wms_manifest, build_wms_reconciliation_plan


def test_wms_manifest_builder_keeps_contract_specific_idempotency() -> None:
    manifest = build_wms_manifest("wms_open_order_line", "2026-05-28")

    assert manifest["batch_id"] == "wms-open-order-line-2026-05-28-v1"
    assert manifest["source_system"] == "WMS"
    assert manifest["contract_name"] == "wms_open_order_line"
    assert manifest["contract_version"] == "v1"
    assert manifest["business_date"] == "2026-05-28"
    assert manifest["idempotency_key"] == "WMS:wms_open_order_line:v1:2026-05-28"


def test_wms_reconciliation_plan_covers_projected_stock_inputs() -> None:
    plan = build_wms_reconciliation_plan("2026-05-28")

    assert plan["source_system"] == "WMS"
    assert plan["business_date"] == "2026-05-28"
    assert plan["required_count"] == 3

    contracts = {contract["contract_name"]: contract for contract in plan["contracts"]}
    assert set(contracts) == {"wms_stock_snapshot_line", "wms_open_order_line", "wms_in_transit_line"}
    assert "projected_stock" in contracts["wms_stock_snapshot_line"]["blocks"]
    assert "replenishment" in contracts["wms_open_order_line"]["blocks"]
    assert "capacity" in contracts["wms_in_transit_line"]["blocks"]
    assert contracts["wms_stock_snapshot_line"]["sla"] == "before_replenishment_cutoff"
