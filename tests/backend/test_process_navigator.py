from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.process_navigator import build_process_map, build_process_navigator_alerts


client = TestClient(app)


def test_process_navigator_map_exposes_domain_clusters() -> None:
    response = client.get("/process-navigator/map", params={"zoom": 0})

    assert response.status_code == 200
    payload = response.json()
    assert payload["semantic_level"] == "domain_clusters"
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
