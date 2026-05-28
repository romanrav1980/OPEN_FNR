import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from open_fnr_api.main import app
from open_fnr_api.replenishment import (
    StockOutRisk,
    StockSnapshot,
    classify_spoilage_risk,
    calculate_net_requirement,
    calculate_projected_stock,
    classify_stock_out_risk,
    estimate_expected_waste,
    order_batches_fefo,
    preview_projected_stock_after_order,
    round_order_qty,
)
from open_fnr_api.replenishment import FreshBatch, SpoilageRisk


client = TestClient(app)


def test_inventory_projection_endpoint_contains_demand_and_stock_layers() -> None:
    response = client.get("/replenishment/inventory-projections/projection-20260528-s001-sku001")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "projection_warning"
    assert payload["forecast_version"] == "regular-baseline-20260528-001"
    assert payload["stock_snapshot_id"] == "stock-snap-20260528-s001-sku001"
    assert payload["days"][1]["open_order_receipt_qty"] == 80
    assert payload["days"][2]["in_transit_receipt_qty"] == 60
    assert payload["days"][3]["stock_out_risk"] == "stock_out"


def test_projected_stock_formula() -> None:
    assert calculate_projected_stock(
        opening_stock_qty=148,
        demand_projection_qty=65,
        open_order_receipt_qty=80,
        in_transit_receipt_qty=0,
    ) == 163


def test_stock_out_risk_classification() -> None:
    assert classify_stock_out_risk(projected_stock_qty=120, safety_stock_qty=90) == StockOutRisk.NONE
    assert classify_stock_out_risk(projected_stock_qty=40, safety_stock_qty=90) == StockOutRisk.WARNING
    assert classify_stock_out_risk(projected_stock_qty=-1, safety_stock_qty=90) == StockOutRisk.STOCK_OUT


def test_stock_snapshot_contract_validates_available_qty() -> None:
    with pytest.raises(ValidationError):
        StockSnapshot(
            snapshot_id="bad",
            store_id="S001",
            sku_id="SKU001",
            on_hand_qty=100,
            reserved_qty=10,
            available_qty=100,
            snapshot_at="2026-05-28T03:00:00Z",
        )


def test_replenishment_policy_endpoint_exposes_lead_time_and_order_constraints() -> None:
    response = client.get("/replenishment/policies")
    assert response.status_code == 200

    policy = response.json()["items"][0]
    assert policy["lead_time_days"] == 2
    assert policy["safety_stock_qty"] == 90
    assert policy["min_order_qty"] == 24
    assert policy["order_multiple"] == 12


def test_order_proposal_endpoint_exposes_explanation_and_constraints() -> None:
    response = client.get("/replenishment/order-proposals/order-proposal-20260528-s001-sku001")
    assert response.status_code == 200

    payload = response.json()
    explanation = payload["explanation"]
    assert payload["status"] == "manual_review"
    assert payload["recommended_order_qty"] == 276
    assert explanation["gross_requirement_qty"] == 321
    assert explanation["projected_stock_at_receipt_qty"] == 163
    assert explanation["net_requirement_qty"] == 273
    assert explanation["rounded_order_qty"] == 276
    assert explanation["constraint_flags"] == ["stock_out_risk", "manual_review_required"]


def test_order_proposal_list_contains_auto_manual_and_blocked_statuses() -> None:
    response = client.get("/replenishment/order-proposals")
    assert response.status_code == 200

    statuses = {item["status"] for item in response.json()["items"]}
    assert statuses == {"manual_review", "auto_approved", "blocked"}


def test_net_requirement_formula() -> None:
    assert calculate_net_requirement(
        projected_stock_at_receipt_qty=163,
        gross_requirement_qty=321,
        safety_stock_qty=90,
        presentation_stock_qty=25,
    ) == 273


def test_order_rounding_uses_moq_and_order_multiple() -> None:
    assert round_order_qty(raw_order_qty=0, min_order_qty=24, order_multiple=12) == 0
    assert round_order_qty(raw_order_qty=13, min_order_qty=24, order_multiple=12) == 24
    assert round_order_qty(raw_order_qty=273, min_order_qty=24, order_multiple=12) == 276


def test_replenishment_workbench_exposes_filters_final_orders_and_audit() -> None:
    response = client.get("/replenishment/workbench")
    assert response.status_code == 200

    payload = response.json()
    assert payload["filters"]["suppliers"] == ["SUP001", "SUP002"]
    assert payload["proposals"][0]["proposal_id"] == "order-proposal-20260528-s001-sku001"
    assert payload["final_orders"][0]["status"] == "manual_review"
    assert payload["audit_events"][0]["old_order_qty"] == 48


def test_adjust_order_proposal_returns_final_order_and_audit_event() -> None:
    response = client.post(
        "/replenishment/order-proposals/order-proposal-20260528-s001-sku001/adjust",
        json={
            "final_order_qty": 300,
            "actor": "replenishment.planner@example.org",
            "actor_role": "Replenishment Planner",
            "reason": "cover promo stock-out",
            "comment": "Raised quantity after projected stock preview.",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["final_order"]["status"] == "adjusted"
    assert payload["final_order"]["final_order_qty"] == 300
    assert payload["final_order"]["projected_stock_after_order_qty"] == 267
    assert payload["audit_event"]["old_order_qty"] == 276
    assert payload["audit_event"]["new_order_qty"] == 300


def test_viewer_cannot_adjust_order_proposal() -> None:
    response = client.post(
        "/replenishment/order-proposals/order-proposal-20260528-s001-sku001/adjust",
        json={
            "final_order_qty": 300,
            "actor": "viewer@example.org",
            "actor_role": "Viewer",
            "reason": "read only attempt",
            "comment": "Should be rejected.",
        },
    )
    assert response.status_code == 403


def test_approved_final_order_cannot_be_adjusted() -> None:
    response = client.post(
        "/replenishment/order-proposals/order-proposal-20260528-s001-sku002/adjust",
        json={
            "final_order_qty": 72,
            "actor": "replenishment.planner@example.org",
            "actor_role": "Replenishment Planner",
            "reason": "late change",
            "comment": "Should be rejected because order is approved.",
        },
    )
    assert response.status_code == 409


def test_projected_stock_preview_after_order() -> None:
    assert preview_projected_stock_after_order(current_projected_stock_qty=-33, final_order_qty=300) == 267


def test_fresh_workbench_exposes_batches_waste_and_availability_tradeoff() -> None:
    response = client.get("/replenishment/fresh/workbench/fresh-s001-sku001-20260528")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "spoilage_risk"
    assert payload["spoilage_risk"] == "high"
    assert payload["recommended_order_qty"] == 96
    assert payload["adjusted_order_qty"] == 72
    assert payload["expected_waste_before_qty"] == 34
    assert payload["expected_waste_after_qty"] == 14
    assert payload["service_level_before"] == 0.97
    assert payload["service_level_after"] == 0.95
    assert payload["batches"][0]["expiration_date"] == "2026-05-30"


def test_fefo_orders_batches_by_expiration_date() -> None:
    batches = [
        FreshBatch(batch_id="b2", store_id="S001", sku_id="SKU001", received_date="2026-05-27", expiration_date="2026-06-01", qty=10, remaining_shelf_life_days=4),
        FreshBatch(batch_id="b1", store_id="S001", sku_id="SKU001", received_date="2026-05-26", expiration_date="2026-05-30", qty=10, remaining_shelf_life_days=2),
    ]

    assert [batch.batch_id for batch in order_batches_fefo(batches)] == ["b1", "b2"]


def test_fresh_waste_estimation_and_spoilage_risk() -> None:
    assert estimate_expected_waste(available_qty=100, demand_qty=76) == 24
    assert classify_spoilage_risk(expected_waste_qty=30, available_qty=100) == SpoilageRisk.HIGH
    assert classify_spoilage_risk(expected_waste_qty=15, available_qty=100) == SpoilageRisk.MEDIUM
    assert classify_spoilage_risk(expected_waste_qty=5, available_qty=100) == SpoilageRisk.LOW
