from pathlib import Path

from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.process_navigator import (
    build_bpmn_flow_model,
    build_process_map,
    build_process_navigator_alerts,
    build_process_performance,
    evaluate_bpmn_trace,
)


client = TestClient(app)


def test_process_navigator_map_exposes_domain_clusters() -> None:
    response = client.get("/process-navigator/map", params={"zoom": 0})

    assert response.status_code == 200
    payload = response.json()
    assert payload["semantic_level"] == "domain_clusters"
    assert payload["environment"] == "dev"
    assert payload["mode"] == "live"
    assert payload["generated_at"]
    assert any(node["id"] == "domain:forecast" for node in payload["nodes"])
    assert any(node["id"] == "domain:replenishment" for node in payload["nodes"])
    assert all(node["level"] == 0 for node in payload["nodes"])


def test_process_navigator_map_semantic_zoom_adds_bpmn_steps() -> None:
    zoom_one = build_process_map(zoom_level=1)
    zoom_three = build_process_map(zoom_level=3)

    assert zoom_one.semantic_level == "process_definitions"
    assert zoom_three.semantic_level == "bpmn_steps"
    assert zoom_three.node_count > zoom_one.node_count
    assert any(node.node_type == "bpmn_step" for node in zoom_three.nodes)
    assert any(edge.edge_type == "bpmn_sequence" for edge in zoom_three.edges)


def test_process_navigator_alerts_include_quality_challenges_and_sla() -> None:
    alerts = build_process_navigator_alerts()

    assert any(alert.source == "bpmn_quality_gate" and alert.severity == "challenge" for alert in alerts)
    assert any(alert.source == "process_task_sla" and alert.process_key == "replenishment_approval_process" for alert in alerts)
    assert all(alert.alert_key for alert in alerts)
    assert all(alert.cause_chain for alert in alerts)
    assert all(alert.occurrence_count >= 1 for alert in alerts)


def test_process_navigator_drilldown_returns_bpmn_graph() -> None:
    response = client.get("/process-navigator/processes/forecast_review_process/drilldown")

    assert response.status_code == 200
    payload = response.json()
    assert payload["process_key"] == "forecast_review_process"
    assert payload["domain"] == "forecast"
    assert payload["bpmn_node_count"] > 0
    assert payload["bpmn_edge_count"] > 0
    assert any(node["node_type"] == "bpmn_step" for node in payload["nodes"])


def test_process_navigator_rejects_non_bpmn_drilldown() -> None:
    response = client.get("/process-navigator/processes/source_batch_gate_decision/drilldown")

    assert response.status_code == 400


def test_process_navigator_rejects_unknown_environment() -> None:
    response = client.get("/process-navigator/map", params={"env": "unknown"})

    assert response.status_code == 422


def test_process_navigator_snapshot_mode_uses_business_date() -> None:
    response = client.get("/process-navigator/map", params={"zoom": 0, "business_date": "2026-05-01"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "snapshot"
    assert payload["business_date"] == "2026-05-01"


def test_process_navigator_alerts_are_paginated() -> None:
    response = client.get("/process-navigator/alerts", params={"limit": 1})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) <= 1
    assert payload["total_count"] >= len(payload["items"])


def test_process_navigator_conformance_async_contract() -> None:
    started = client.post("/process-navigator/processes/forecast_review_process/conformance/check")

    assert started.status_code == 200
    job = started.json()
    assert job["status"] == "queued"
    assert job["estimated_seconds"] > 0

    completed = client.get(
        f"/process-navigator/processes/forecast_review_process/conformance/status/{job['job_id']}"
    )

    assert completed.status_code == 200
    payload = completed.json()
    assert payload["job_status"] == "done"
    assert payload["conformance_score"] >= 0


def test_process_navigator_bpmn_trace_detects_skipped_mandatory_step() -> None:
    model = build_bpmn_flow_model(
        path=Path("processes/forecast/forecast_review_process.bpmn20.xml"),
        process_key="forecast_review_process",
    )

    result = evaluate_bpmn_trace(
        process_key="forecast_review_process",
        model=model,
        executed_step_ids=("accept_forecast_slice",),
        required_step_ids=("review_forecast_anomaly", "accept_forecast_slice"),
        instance_id="trace-skipped-review",
    )

    assert result.mandatory_steps_skipped == 1
    assert any(item.deviation_type == "skipped_mandatory_step" for item in result.deviations)
    assert result.conformance_score is not None
    assert result.conformance_score < 100


def test_process_navigator_bpmn_trace_detects_unexpected_sequence() -> None:
    model = build_bpmn_flow_model(
        path=Path("processes/forecast/forecast_review_process.bpmn20.xml"),
        process_key="forecast_review_process",
    )

    result = evaluate_bpmn_trace(
        process_key="forecast_review_process",
        model=model,
        executed_step_ids=("accept_forecast_slice", "review_forecast_anomaly"),
        required_step_ids=("review_forecast_anomaly", "accept_forecast_slice"),
        instance_id="trace-reversed-review",
    )

    assert result.unexpected_sequences == 1
    assert any(item.deviation_type == "unexpected_sequence" for item in result.deviations)
    assert result.conformance_score is not None
    assert result.conformance_score < 100


def test_process_navigator_conformance_summary_only_does_not_fail_without_cache() -> None:
    response = client.get(
        "/process-navigator/processes/replenishment_calculation_process/conformance",
        params={"summary_only": True},
    )

    assert response.status_code == 200
    assert response.json()["job_status"] in {"pending", "done"}


def test_process_navigator_performance_contract() -> None:
    response = client.get("/process-navigator/processes/forecast_review_process/performance")

    assert response.status_code == 200
    payload = response.json()
    assert payload["cycle_time_p95_minutes"] >= payload["cycle_time_median_minutes"]
    assert payload["sla_thresholds"]["red_minutes"] > payload["sla_thresholds"]["green_minutes"]
    assert payload["human_task_metrics"][0]["processing_time_p95_minutes"] > 0
    assert payload["throughput_by_business_day"]


def test_process_navigator_performance_uses_task_timing() -> None:
    performance = build_process_performance("forecast_review_process", "dev", 30)

    assert performance.cycle_time_median_minutes > 0
    assert performance.human_task_metrics[0].processing_time_p95_minutes > 0
    assert performance.rework_rate == 0
    assert any(day.started >= 1 for day in performance.throughput_by_business_day)


def test_process_navigator_versions_contract() -> None:
    response = client.get(
        "/process-navigator/processes/forecast_review_process/versions",
        params={"include_instances": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["active_version_count"] >= 1
    assert payload["versions"][0]["instance_list"]


def test_process_navigator_infrastructure_health_contract() -> None:
    response = client.get("/process-navigator/infrastructure/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["components"]
    assert all("component_id" in component for component in payload["components"])


def test_process_navigator_tracking_contract() -> None:
    response = client.get(
        "/process-navigator/tracking",
        params={"business_key_type": "sku-store", "sku_id": "SKU-1", "store_id": "STORE-1"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["business_key_type"] == "sku-store"
    assert payload["trail"]


def test_process_navigator_weekly_report_contract() -> None:
    response = client.get("/process-navigator/reports/weekly", params={"business_week": "2026-W22"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["business_week"] == "2026-W22"
    assert payload["superset_dataset_ref"] == "process_alert_history"
