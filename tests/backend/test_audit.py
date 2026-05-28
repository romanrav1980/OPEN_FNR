from fastapi.testclient import TestClient

from open_fnr_api import audit
from open_fnr_api.audit import AuditEventCreate, record_audit_event_if_enabled
from open_fnr_api.main import app


client = TestClient(app)


def test_audit_event_can_be_recorded_and_listed() -> None:
    response = client.post(
        "/audit/events",
        json={
            "event_type": "manual_adjustment",
            "actor": "planner@example.org",
            "actor_role": "Forecast Planner",
            "object_type": "forecast",
            "object_id": "forecast-s001-sku001",
            "action": "preview",
            "reason": "local event",
            "correlation_id": "corr-audit-001",
            "payload": {"delta": "+10%"},
        },
    )
    assert response.status_code == 200
    event = response.json()
    assert event["event_id"].startswith("audit-")
    assert event["payload"] == {"delta": "+10%"}

    listed = client.get("/audit/events", params={"limit": 1})
    assert listed.status_code == 200
    assert listed.json()[0]["event_id"] == event["event_id"]


def test_metadata_exposes_runtime_and_mock_mode() -> None:
    response = client.get("/metadata")
    assert response.status_code == 200

    payload = response.json()
    assert payload["runtime_mode"] == "dev"
    assert payload["mock_mode"] is True
    assert payload["audit_enabled"] is True
    assert "audit" in payload["modules"]


def test_business_audit_recording_is_enabled_by_default() -> None:
    event = record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="enabled_by_default",
            actor="planner@example.org",
            actor_role="Forecast Planner",
            object_type="forecast",
            object_id="forecast-1",
            action="approve",
            reason="audit enabled",
        )
    )

    assert event is not None
    assert event.event_type == "enabled_by_default"


def test_business_audit_recording_can_be_disabled_by_setting() -> None:
    original_value = audit.settings.audit_enabled
    audit.settings.audit_enabled = False
    try:
        event = record_audit_event_if_enabled(
            AuditEventCreate(
                event_type="disabled_by_setting",
                actor="planner@example.org",
                actor_role="Forecast Planner",
                object_type="forecast",
                object_id="forecast-2",
                action="approve",
                reason="audit disabled by config",
            )
        )
    finally:
        audit.settings.audit_enabled = original_value

    assert event is None
