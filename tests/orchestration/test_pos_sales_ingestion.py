from orchestration.airflow.dags.pos_sales_ingestion import build_pos_sales_manifest


def test_pos_sales_ingestion_manifest_is_idempotent_by_business_date() -> None:
    manifest = build_pos_sales_manifest("2026-05-28")

    assert manifest["batch_id"] == "pos-sales-2026-05-28-v1"
    assert manifest["source_system"] == "POS"
    assert manifest["contract_name"] == "pos_sales_line"
    assert manifest["contract_version"] == "v1"
    assert manifest["business_date"] == "2026-05-28"
    assert manifest["idempotency_key"] == "POS:pos_sales_line:v1:2026-05-28"
