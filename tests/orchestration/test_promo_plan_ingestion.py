from orchestration.airflow.dags.promo_plan_ingestion import build_promo_manifest


def test_promo_manifest_builder_keeps_plan_idempotency() -> None:
    manifest = build_promo_manifest("2026-05-28")

    assert manifest["batch_id"] == "promo-plan-2026-05-28-v1"
    assert manifest["source_system"] == "PROMO"
    assert manifest["contract_name"] == "promo_plan_line"
    assert manifest["contract_version"] == "v1"
    assert manifest["business_date"] == "2026-05-28"
    assert manifest["idempotency_key"] == "PROMO:promo_plan_line:v1:2026-05-28"
