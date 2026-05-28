from orchestration.airflow.dags.erp_commercial_ingestion import build_erp_manifest


def test_erp_manifest_builder_keeps_contract_specific_idempotency() -> None:
    manifest = build_erp_manifest("erp_order_export_status_line", "2026-05-28")

    assert manifest["batch_id"] == "erp-order-export-status-line-2026-05-28-v1"
    assert manifest["source_system"] == "ERP"
    assert manifest["contract_name"] == "erp_order_export_status_line"
    assert manifest["contract_version"] == "v1"
    assert manifest["business_date"] == "2026-05-28"
    assert manifest["idempotency_key"] == "ERP:erp_order_export_status_line:v1:2026-05-28"
