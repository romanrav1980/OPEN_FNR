from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.observability import ALERTS, AlertSeverity, incident_sla_minutes, transition_incident


client = TestClient(app)


def test_alerts_require_ops_role_and_include_runbook() -> None:
    denied = client.get("/observability/alerts", params={"actor_role": "Viewer"})
    allowed = client.get("/observability/alerts", params={"actor_role": "L1"})

    assert denied.status_code == 403
    assert allowed.status_code == 200
    alert = allowed.json()["items"][0]
    assert alert["severity"] == "sev2"
    assert alert["runbook_url"] == "runbooks/publication-export-failure.md"


def test_incident_lifecycle_acknowledge_escalate_resolve_with_roles() -> None:
    ack = client.post(
        "/observability/incidents/inc-20260528-001/acknowledge",
        json={"actor": "l1@example.org", "actor_role": "L1", "comment": "Acknowledged alert."},
    )
    escalate = client.post(
        "/observability/incidents/inc-20260528-001/escalate",
        json={"actor": "l2@example.org", "actor_role": "L2", "comment": "Escalating after runbook step."},
    )
    resolve = client.post(
        "/observability/incidents/inc-20260528-001/resolve",
        json={"actor": "im@example.org", "actor_role": "Incident Manager", "comment": "ERP export recovered."},
    )

    assert ack.status_code == 200
    assert ack.json()["status"] == "acknowledged"
    assert escalate.status_code == 200
    assert escalate.json()["status"] == "escalated"
    assert resolve.status_code == 200
    assert resolve.json()["status"] == "resolved"


def test_incident_action_rejects_wrong_role() -> None:
    response = client.post(
        "/observability/incidents/inc-20260528-001/resolve",
        json={"actor": "l1@example.org", "actor_role": "L1", "comment": "not allowed"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Incident Manager role required"


def test_logs_are_searchable_by_trace_context() -> None:
    response = client.get("/observability/logs/search", params={"query": "ERP export failed"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["trace_id"] == "trace-export-001"


def test_incident_helpers_cover_severity_sla_and_transition() -> None:
    assert incident_sla_minutes(AlertSeverity.SEV1) == 15
    assert incident_sla_minutes(AlertSeverity.SEV2) == 60
    incident = client.get("/observability/incidents").json()["items"][0]
    assert incident["sla_minutes"] == incident_sla_minutes(ALERTS[0].severity)
