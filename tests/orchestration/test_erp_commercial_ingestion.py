from orchestration.airflow.dags.erp_commercial_ingestion import build_erp_manifest, build_erp_reconciliation_plan


def test_erp_manifest_builder_keeps_contract_specific_idempotency() -> None:
    manifest = build_erp_manifest("erp_order_export_status_line", "2026-05-28")

    assert manifest["batch_id"] == "erp-order-export-status-line-2026-05-28-v1"
    assert manifest["source_system"] == "ERP"
    assert manifest["contract_name"] == "erp_order_export_status_line"
    assert manifest["contract_version"] == "v1"
    assert manifest["business_date"] == "2026-05-28"
    assert manifest["idempotency_key"] == "ERP:erp_order_export_status_line:v1:2026-05-28"


def test_erp_reconciliation_plan_covers_prices_terms_and_export_status() -> None:
    plan = build_erp_reconciliation_plan("2026-05-28")

    assert plan["source_system"] == "ERP"
    assert plan["required_count"] == 3

    contracts = {contract["contract_name"]: contract for contract in plan["contracts"]}
    assert set(contracts) == {"erp_price_line", "erp_supplier_term_line", "erp_order_export_status_line"}
    assert "regular_forecast" in contracts["erp_price_line"]["blocks"]
    assert "replenishment" in contracts["erp_supplier_term_line"]["blocks"]
    assert "publication_reconciliation" in contracts["erp_order_export_status_line"]["blocks"]
