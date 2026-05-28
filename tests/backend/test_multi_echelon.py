from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.multi_echelon import (
    DC_STOCKS,
    STORE_DEMANDS,
    aggregate_store_demand,
    allocate_dc_stock,
    calculate_available_dc_qty,
    calculate_dc_shortage,
)


client = TestClient(app)


def test_dc_plan_aggregates_store_demand_and_shortage() -> None:
    response = client.get("/multi-echelon/dc-plans")
    assert response.status_code == 200

    payload = response.json()
    plan = payload["items"][0]
    assert plan["total_store_demand_qty"] == 270
    assert plan["available_dc_qty"] == 210
    assert plan["shortage_qty"] == 60
    assert plan["status"] == "shortage"


def test_dc_demand_equals_lower_level_store_demand() -> None:
    total_demand = aggregate_store_demand(STORE_DEMANDS, dc_id="DC001", sku_id="SKU001")

    assert total_demand == sum(row.demand_qty for row in STORE_DEMANDS)


def test_dc_allocation_is_priority_and_service_risk_explainable() -> None:
    response = client.get("/multi-echelon/dc-plans/dc-plan-20260528-dc001-sku001/allocations")
    assert response.status_code == 200

    payload = response.json()
    assert payload["allocation_rule"] == "priority_service_risk_first"
    assert payload["items"][0]["store_id"] == "S001"
    assert payload["items"][0]["allocated_qty"] == 120
    assert payload["items"][1]["store_id"] == "S002"
    assert payload["items"][1]["allocated_qty"] == 90
    assert payload["items"][2]["store_id"] == "S003"
    assert payload["items"][2]["unfilled_qty"] == 60
    assert payload["items"][2]["reason"] == "DC shortage after higher priority allocation"


def test_multi_echelon_helpers_calculate_stock_shortage_and_allocation() -> None:
    stock = DC_STOCKS[0]
    available = calculate_available_dc_qty(stock)
    shortage = calculate_dc_shortage(total_demand_qty=270, available_qty=available)
    allocations = allocate_dc_stock(STORE_DEMANDS, available_qty=available)

    assert available == 210
    assert shortage == 60
    assert sum(item.allocated_qty for item in allocations) == 210
    assert sum(item.unfilled_qty for item in allocations) == 60


def test_dc_scope_blocks_other_region() -> None:
    response = client.get("/multi-echelon/dc-plans", params={"actor_region": "south"})

    assert response.status_code == 403
    assert response.json()["detail"] == "actor is not allowed to access this DC region"


def test_supply_chain_manager_can_approve_dc_allocation_with_audit() -> None:
    response = client.post(
        "/multi-echelon/dc-plans/dc-plan-20260528-dc001-sku001/approve",
        json={
            "actor": "supply.manager@example.org",
            "actor_role": "Supply Chain Manager",
            "comment": "Allocation approved before store order cutoff.",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["plan"]["status"] == "approved"
    assert payload["audit_event"]["event_type"] == "allocation_approved"
    assert payload["audit_event"]["message"] == "Allocation approved before store order cutoff."


def test_dc_allocation_approval_requires_supply_chain_manager() -> None:
    response = client.post(
        "/multi-echelon/dc-plans/dc-plan-20260528-dc001-sku001/approve",
        json={
            "actor": "viewer@example.org",
            "actor_role": "Viewer",
            "comment": "not allowed",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "only Supply Chain Manager can approve DC allocation"
