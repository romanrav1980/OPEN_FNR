from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from open_fnr_api.main import app
from open_fnr_api.promo import (
    PromoDisplayLocation,
    PromoMechanic,
    PromoPlan,
    PromoRiskLevel,
    PromoStatus,
    build_total_forecast,
    classify_promo_risk,
    validate_promo,
)


client = TestClient(app)


def test_promo_plans_endpoint_lists_required_business_fields() -> None:
    response = client.get("/promo/plans")
    assert response.status_code == 200

    promo = response.json()["items"][0]
    assert promo["sku_ids"]
    assert promo["store_ids"]
    assert promo["discount_percent"] == 20.0
    assert promo["display_location"] == "end_cap"
    assert promo["display_capacity_units"] == 120


def test_promo_validation_ready_for_forecast() -> None:
    response = client.get("/promo/plans/promo-20260601-fresh-001/validation")
    assert response.status_code == 200

    payload = response.json()
    assert payload["ready_for_forecast"] is True
    assert payload["status"] == "ready_for_forecast"


def test_promo_contract_rejects_invalid_dates() -> None:
    with pytest.raises(ValidationError):
        PromoPlan(
            promo_id="bad",
            sku_ids=["SKU001"],
            store_ids=["S001"],
            start_date=date(2026, 6, 10),
            end_date=date(2026, 6, 1),
            mechanic=PromoMechanic.DISCOUNT,
            regular_price=100,
            promo_price=80,
            discount_percent=20,
            display_location=PromoDisplayLocation.END_CAP,
            display_capacity_units=50,
            status=PromoStatus.DRAFT,
            created_by="Promo Planner",
            updated_at=datetime(2026, 5, 28, tzinfo=timezone.utc),
        )


def test_promo_overlap_detection() -> None:
    plan = PromoPlan(
        promo_id="promo-overlap-test",
        sku_ids=["SKU001"],
        store_ids=["S001"],
        start_date=date(2026, 6, 3),
        end_date=date(2026, 6, 5),
        mechanic=PromoMechanic.DISCOUNT,
        regular_price=100,
        promo_price=80,
        discount_percent=20,
        display_location=PromoDisplayLocation.END_CAP,
        display_capacity_units=50,
        status=PromoStatus.DRAFT,
        created_by="Promo Planner",
        updated_at=datetime(2026, 5, 28, tzinfo=timezone.utc),
    )

    validation = validate_promo(plan)
    assert validation.ready_for_forecast is False
    assert validation.errors == ["overlaps with promo-20260601-fresh-001"]


def test_promo_forecast_endpoint_separates_regular_and_uplift() -> None:
    response = client.get("/promo/forecasts/promo-20260601-fresh-001")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "forecasted"
    first_day = payload["days"][0]
    assert first_day["regular_forecast_qty"] == 120
    assert first_day["promo_uplift_qty"] == 48
    assert first_day["total_forecast_qty"] == 168
    assert payload["reference_promos"][0]["similarity_score"] == 0.91


def test_total_forecast_formula() -> None:
    assert build_total_forecast(120, 48) == 168


def test_promo_approval_endpoint_exposes_route_and_actions() -> None:
    response = client.get("/promo/approvals/promo-20260601-fresh-001")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "category_review"
    assert payload["risk_level"] == "medium"
    assert payload["route"] == ["Category Manager", "Supply Chain Manager"]
    assert payload["steps"][0]["allowed_actions"] == ["approve", "reject", "request_rework", "comment"]
    assert payload["publication_ready"] is False


def test_promo_approval_rework_contains_blocking_errors() -> None:
    response = client.get("/promo/approvals/promo-20260605-grocery-002")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "rework"
    assert payload["risk_level"] == "high"
    assert payload["blocking_errors"] == ["overlaps with promo-20260601-fresh-001"]


def test_promo_risk_classification() -> None:
    assert classify_promo_risk(discount_percent=10, uplift_factor=0.2, post_promo_stock_qty=250) == PromoRiskLevel.LOW
    assert classify_promo_risk(discount_percent=20, uplift_factor=0.2, post_promo_stock_qty=250) == PromoRiskLevel.MEDIUM
    assert classify_promo_risk(discount_percent=10, uplift_factor=0.8, post_promo_stock_qty=250) == PromoRiskLevel.HIGH
