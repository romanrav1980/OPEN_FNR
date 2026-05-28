from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.performance import (
    PILOT_PROFILE,
    PerformanceGateDecision,
    PerformanceMetric,
    PerformanceRunStatus,
    calculate_synthetic_rows,
    evaluate_gate,
)


client = TestClient(app)


def test_performance_run_exposes_pilot_scale_metrics_and_gate() -> None:
    response = client.get("/performance/runs")
    assert response.status_code == 200

    run = response.json()["items"][0]
    assert run["profile"]["stores"] == 3000
    assert run["profile"]["skus_per_store"] == 5500
    assert run["status"] == "passed"
    assert run["gate_decision"] == "pass"
    metric_names = {metric["name"] for metric in run["metrics"]}
    assert "batch_runtime_minutes" in metric_names
    assert "api_p95_latency_ms" in metric_names
    assert "ui_lcp_ms" in metric_names
    assert "airflow_dag_runtime_minutes" in metric_names


def test_synthetic_scale_validates_forecast_row_count() -> None:
    response = client.get("/performance/runs/perf-run-20260528-pilot-001/synthetic-scale")
    assert response.status_code == 200

    payload = response.json()
    assert payload["synthetic_forecast_rows"] == 495_000_000
    assert payload["shard_count"] == 8


def test_performance_gate_fails_blocking_batch_runtime() -> None:
    metrics = (
        PerformanceMetric(name="batch_runtime_minutes", value=121, threshold=120, unit="minutes", status=PerformanceRunStatus.FAILED),
        PerformanceMetric(name="api_p95_latency_ms", value=180, threshold=500, unit="ms", status=PerformanceRunStatus.PASSED),
    )

    assert evaluate_gate(metrics) == PerformanceGateDecision.FAIL


def test_performance_gate_requires_waiver_for_non_blocking_latency_regression() -> None:
    metrics = (
        PerformanceMetric(name="api_p95_latency_ms", value=650, threshold=500, unit="ms", status=PerformanceRunStatus.FAILED),
        PerformanceMetric(name="ui_lcp_ms", value=2500, threshold=3000, unit="ms", status=PerformanceRunStatus.PASSED),
    )

    assert evaluate_gate(metrics) == PerformanceGateDecision.WAIVER_REQUIRED


def test_performance_helpers_calculate_synthetic_rows() -> None:
    assert calculate_synthetic_rows(PILOT_PROFILE) == 495_000_000


def test_architect_can_request_performance_waiver_with_audit() -> None:
    response = client.post(
        "/performance/runs/perf-run-20260528-pilot-001/waive",
        json={
            "actor": "architect@example.org",
            "actor_role": "Architect",
            "reason": "Temporary pilot waiver accepted with tracked bottleneck owner.",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["run"]["status"] == "waived"
    assert payload["audit_event"]["event_type"] == "performance_waiver_requested"


def test_performance_waiver_requires_architect_role() -> None:
    response = client.post(
        "/performance/runs/perf-run-20260528-pilot-001/waive",
        json={
            "actor": "engineer@example.org",
            "actor_role": "Performance Engineer",
            "reason": "not allowed",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "only Architect can waive performance gate"
