from fastapi.testclient import TestClient

from open_fnr_api.diagnostics import EVIDENCE, RootCause, classify_root_cause
from open_fnr_api.main import app


client = TestClient(app)


def test_diagnostic_insight_shows_root_cause_evidence_and_links() -> None:
    response = client.get("/diagnostics/insights")
    assert response.status_code == 200

    payload = response.json()
    insight = payload[0]
    assert insight["status"] == "classified"
    assert insight["root_cause"] == "late_delivery"
    assert insight["confidence"] == 0.88
    assert insight["affected_store"] == "S001"
    assert "inbound-po-001" in insight["linked_objects"]
    assert len(insight["evidence"]) == 3
    assert insight["recommended_action"] == "Create supply exception and expedite replacement delivery."


def test_root_cause_classifier_detects_late_delivery() -> None:
    assert classify_root_cause(EVIDENCE) == RootCause.LATE_DELIVERY


def test_create_exception_from_insight_requires_scope_role_and_returns_audit() -> None:
    denied = client.post(
        "/diagnostics/insights/diagnostic-20260602-s001-sku001/exception",
        json={"actor": "viewer@example.org", "actor_role": "Viewer", "comment": "Create exception"},
    )
    assert denied.status_code == 403

    response = client.post(
        "/diagnostics/insights/diagnostic-20260602-s001-sku001/exception",
        json={
            "actor": "supply.manager@example.org",
            "actor_role": "Supply Chain Manager",
            "comment": "Expedite replacement delivery.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "converted_to_exception"
    assert payload["exception_id"] == "exc-diagnostic-20260602-s001-sku001"
    assert payload["audit"]["evidence_ids"] == ["ev-wms-001", "ev-stock-001", "ev-forecast-001"]


def test_create_exception_from_unknown_insight_returns_404() -> None:
    response = client.post(
        "/diagnostics/insights/unknown/exception",
        json={
            "actor": "supply.manager@example.org",
            "actor_role": "Supply Chain Manager",
            "comment": "Unknown insight.",
        },
    )
    assert response.status_code == 404
