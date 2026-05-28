from datetime import date

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from open_fnr_api.lifecycle import (
    ClearanceRisk,
    LifecycleStatus,
    SkuLifecycle,
    calculate_cold_start_forecast,
    classify_clearance_risk,
    order_allowed_on_date,
)
from open_fnr_api.main import app


client = TestClient(app)


def test_lifecycle_list_contains_phase_in_and_phase_out_skus() -> None:
    response = client.get("/lifecycle/skus")
    assert response.status_code == 200

    payload = response.json()
    statuses = {item["status"] for item in payload["items"]}
    assert statuses == {"planned", "phase_out"}
    assert payload["items"][0]["reference_sku_id"] == "SKU001"
    assert payload["items"][1]["replacement_sku_id"] == "SKU_NEW_001"


def test_new_sku_has_cold_start_reference_forecast() -> None:
    response = client.get("/lifecycle/skus/SKU_NEW_001")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "planned"
    assert payload["reference_sku_id"] == "SKU001"
    assert payload["cold_start_forecast_qty"] == 12.4


def test_order_after_termination_date_is_blocked() -> None:
    response = client.get("/lifecycle/skus/SKU_OLD_001/order-allowed", params={"order_date": "2026-06-06"})
    assert response.status_code == 200

    assert response.json()["allowed"] is False


def test_lifecycle_action_requires_category_manager() -> None:
    response = client.post(
        "/lifecycle/skus/SKU_NEW_001/activate",
        json={
            "actor": "viewer@example.org",
            "actor_role": "Viewer",
            "reason": "not allowed",
        },
    )
    assert response.status_code == 403


def test_category_manager_can_activate_sku_and_audit_change() -> None:
    response = client.post(
        "/lifecycle/skus/SKU_NEW_001/activate",
        json={
            "actor": "category.manager@example.org",
            "actor_role": "Category Manager",
            "reason": "phase-in ready before launch date",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["sku"]["status"] == "active"
    assert payload["audit_event"]["old_status"] == "planned"
    assert payload["audit_event"]["new_status"] == "active"


def test_lifecycle_helpers() -> None:
    sku = SkuLifecycle(
        sku_id="SKU_TEST",
        status=LifecycleStatus.PHASE_OUT,
        launch_date=date(2024, 1, 1),
        termination_date=date(2026, 6, 5),
        reference_sku_id=None,
        replacement_sku_id="SKU_NEW",
        cold_start_forecast_qty=0,
        remaining_stock_qty=10,
        clearance_risk=ClearanceRisk.LOW,
        owner_role="Category Manager",
        updated_at="2026-05-28T09:00:00Z",
    )

    assert order_allowed_on_date(sku, date(2026, 6, 5)) is True
    assert order_allowed_on_date(sku, date(2026, 6, 6)) is False
    assert calculate_cold_start_forecast(reference_forecast_qty=20, similarity_factor=0.8) == 16
    assert classify_clearance_risk(remaining_stock_qty=420, days_to_termination=7) == ClearanceRisk.HIGH


def test_lifecycle_contract_requires_phase_out_termination_date() -> None:
    with pytest.raises(ValidationError):
        SkuLifecycle(
            sku_id="BAD",
            status=LifecycleStatus.PHASE_OUT,
            launch_date=date(2024, 1, 1),
            termination_date=None,
            reference_sku_id=None,
            replacement_sku_id="SKU_NEW",
            cold_start_forecast_qty=0,
            remaining_stock_qty=1,
            clearance_risk=ClearanceRisk.LOW,
            owner_role="Category Manager",
            updated_at="2026-05-28T09:00:00Z",
        )
