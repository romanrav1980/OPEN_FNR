from orchestration.airflow.dags.promo_plan_ingestion import build_promo_manifest, build_promo_quality_plan


def test_promo_manifest_builder_keeps_plan_idempotency() -> None:
    manifest = build_promo_manifest("2026-05-28")

    assert manifest["batch_id"] == "promo-plan-2026-05-28-v1"
    assert manifest["source_system"] == "PROMO"
    assert manifest["contract_name"] == "promo_plan_line"
    assert manifest["contract_version"] == "v1"
    assert manifest["business_date"] == "2026-05-28"
    assert manifest["idempotency_key"] == "PROMO:promo_plan_line:v1:2026-05-28"


def test_promo_quality_plan_covers_price_display_capacity_and_overlap() -> None:
    plan = build_promo_quality_plan("2026-05-28")

    assert plan["source_system"] == "PROMO"
    assert plan["contract_name"] == "promo_plan_line"
    assert "promo_overlap" in plan["quality_checks"]
    assert "price_discount_consistency" in plan["quality_checks"]
    assert "display_location_presence" in plan["quality_checks"]
    assert "display_capacity_presence" in plan["quality_checks"]
    assert "promo_forecast" in plan["blocks"]
    assert "shelf_space" in plan["blocks"]
