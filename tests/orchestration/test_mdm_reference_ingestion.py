from orchestration.airflow.dags.mdm_reference_ingestion import build_mdm_manifest


def test_mdm_manifest_builder_keeps_contract_specific_idempotency() -> None:
    manifest = build_mdm_manifest("mdm_product_line", "2026-05-28")

    assert manifest["batch_id"] == "mdm-product-line-2026-05-28-v1"
    assert manifest["source_system"] == "MDM"
    assert manifest["contract_name"] == "mdm_product_line"
    assert manifest["contract_version"] == "v1"
    assert manifest["business_date"] == "2026-05-28"
    assert manifest["idempotency_key"] == "MDM:mdm_product_line:v1:2026-05-28"
