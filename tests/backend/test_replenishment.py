import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from open_fnr_api.main import app
from open_fnr_api.replenishment import StockOutRisk, StockSnapshot, calculate_projected_stock, classify_stock_out_risk


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
