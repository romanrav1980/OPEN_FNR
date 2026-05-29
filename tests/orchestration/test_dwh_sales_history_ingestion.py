from orchestration.airflow.dags.dwh_sales_history_ingestion import build_dwh_sales_history_manifest


def test_dwh_sales_history_manifest_is_idempotent_by_business_date() -> None:
    manifest = build_dwh_sales_history_manifest("2026-05-28")

    assert manifest["batch_id"] == "dwh-sales-history-2026-05-28-v1"
    assert manifest["source_system"] == "DWH"
    assert manifest["contract_name"] == "dwh_sales_history_line"
    assert manifest["contract_version"] == "v1"
    assert manifest["business_date"] == "2026-05-28"
    assert manifest["idempotency_key"] == "DWH:dwh_sales_history_line:v1:2026-05-28"
    assert manifest["history_window"] == "rolling_24_months"
