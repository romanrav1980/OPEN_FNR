from orchestration.airflow.dags.wms_inventory_ingestion import build_wms_manifest


def test_wms_manifest_builder_keeps_contract_specific_idempotency() -> None:
    manifest = build_wms_manifest("wms_open_order_line", "2026-05-28")

    assert manifest["batch_id"] == "wms-open-order-line-2026-05-28-v1"
    assert manifest["source_system"] == "WMS"
    assert manifest["contract_name"] == "wms_open_order_line"
    assert manifest["contract_version"] == "v1"
    assert manifest["business_date"] == "2026-05-28"
    assert manifest["idempotency_key"] == "WMS:wms_open_order_line:v1:2026-05-28"
