import pytest
from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.replenishment_optimization import OPTIMIZATION_RUNS, calculate_safety_stock, get_target_for_segment, optimization_gate


client = TestClient(app)


def test_service_level_targets_cover_abc_xyz_matrix() -> None:
    response = client.get("/replenishment/optimization/service-level-targets")
    assert response.status_code == 200
    payload = response.json()

    segments = {(item["abc_class"], item["xyz_class"]) for item in payload["items"]}
    assert len(segments) == 9
    assert ("A", "X") in segments
    assert ("C", "Z") in segments
    assert get_target_for_segment("A", "X").service_level_target > get_target_for_segment("C", "Z").service_level_target


def test_safety_stock_calculation_uses_segment_z_and_lead_time() -> None:
    target = get_target_for_segment("A", "X")
    assert calculate_safety_stock(demand_std_qty=12, lead_time_days=4, safety_stock_z=target.safety_stock_z) == 49.2

    with pytest.raises(ValueError):
        calculate_safety_stock(demand_std_qty=-1, lead_time_days=2, safety_stock_z=target.safety_stock_z)


def test_optimization_run_exposes_projected_stock_orders_and_business_impacts() -> None:
    response = client.get("/replenishment/optimization/runs")
    assert response.status_code == 200
    run = response.json()["items"][0]

    assert run["run_id"] == "repl-opt-20260528-001"
    assert run["source_readiness_status"] == "ready"
    assert run["projected_stock_rows"] > run["order_proposal_rows"]
    assert run["service_level_impact"] > 0
    assert run["stock_cost_impact"] < 0
    assert run["waste_impact"] < 0


def test_optimization_gate_blocks_missing_projection_or_sources() -> None:
    good = OPTIMIZATION_RUNS[0]
    assert optimization_gate(good).ready_for_export is True

    no_projection = good.model_copy(update={"projected_stock_rows": 0})
    assert "projected_stock_missing" in optimization_gate(no_projection).blockers

    source_blocked = good.model_copy(update={"source_readiness_status": "blocked"})
    assert "source_readiness_not_ready" in optimization_gate(source_blocked).blockers


def test_optimization_gate_endpoint() -> None:
    response = client.get("/replenishment/optimization/runs/repl-opt-20260528-001/gate")
    assert response.status_code == 200
    payload = response.json()

    assert payload["ready_for_export"] is True
    assert "fresh_waste_impact_calculated" in payload["gates"]
