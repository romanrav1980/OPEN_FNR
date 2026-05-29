from orchestration.airflow.dags.mdm_reference_ingestion import build_mdm_manifest, build_mdm_quality_plan


def test_mdm_manifest_builder_keeps_contract_specific_idempotency() -> None:
    manifest = build_mdm_manifest("mdm_product_line", "2026-05-28")

    assert manifest["batch_id"] == "mdm-product-line-2026-05-28-v1"
    assert manifest["source_system"] == "MDM"
    assert manifest["contract_name"] == "mdm_product_line"
    assert manifest["contract_version"] == "v1"
    assert manifest["business_date"] == "2026-05-28"
    assert manifest["idempotency_key"] == "MDM:mdm_product_line:v1:2026-05-28"


def test_mdm_quality_plan_covers_lifecycle_hierarchy_and_routing() -> None:
    plan = build_mdm_quality_plan("2026-05-28")

    assert plan["source_system"] == "MDM"
    assert plan["required_count"] == 2

    contracts = {contract["contract_name"]: contract for contract in plan["contracts"]}
    assert "hierarchy_integrity" in contracts["mdm_product_line"]["quality_checks"]
    assert "lifecycle_validity" in contracts["mdm_product_line"]["quality_checks"]
    assert "warehouse_routing" in contracts["mdm_store_line"]["quality_checks"]
    assert "replenishment_calendar" in contracts["mdm_store_line"]["quality_checks"]
    assert "replenishment" in contracts["mdm_store_line"]["blocks"]
