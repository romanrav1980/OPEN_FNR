from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.performance import EPYC_PROFILE, build_epyc_performance_gate


client = TestClient(app)


def test_epyc_gate_covers_full_production_volume() -> None:
    response = client.get("/performance/epyc-gate")
    assert response.status_code == 200
    payload = response.json()

    assert payload["profile"]["stores"] == 30000
    assert payload["profile"]["skus_per_store"] == 5500
    assert payload["profile"]["horizon_days"] == 90
    assert payload["forecast_rows"] == 14_850_000_000
    assert payload["decision"] == "pass"


def test_epyc_gate_keeps_forecast_and_replenishment_under_two_hours() -> None:
    gate = build_epyc_performance_gate()

    assert gate.batch_runtime_minutes <= gate.batch_runtime_threshold_minutes
    assert gate.replenishment_runtime_minutes <= 120
    assert gate.blockers == ()


def test_epyc_gate_tracks_cluster_memory_budget() -> None:
    gate = build_epyc_performance_gate()

    assert gate.profile.nodes == 6
    assert gate.profile.cores_per_node == 96
    assert gate.memory_budget_gb == 4608
    assert gate.memory_peak_gb < gate.memory_budget_gb


def test_epyc_gate_blocks_memory_over_budget() -> None:
    tiny_profile = EPYC_PROFILE.model_copy(update={"nodes": 2, "memory_gb_per_node": 256})
    gate = build_epyc_performance_gate(tiny_profile)

    assert gate.decision == "fail"
    assert "memory_peak_above_cluster_budget" in gate.blockers
