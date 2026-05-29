from fastapi.testclient import TestClient

from open_fnr_api import capacity
from open_fnr_api.capacity import CALENDAR, detect_capacity_overload
from open_fnr_api.main import app


client = TestClient(app)


def test_capacity_plan_detects_overload_and_smoothing_preview() -> None:
    response = client.get("/capacity/plans")
    assert response.status_code == 200

    plan = response.json()["items"][0]
    assert plan["status"] == "smoothing_proposed"
    assert plan["overload_qty"] == 2400
    assert plan["moved_qty"] == 2400
    assert len(plan["affected_orders"]) == 2
    assert "Move medium and low priority" in plan["recommendation"]


def test_capacity_overload_helper() -> None:
    assert detect_capacity_overload(CALENDAR) == 2400


def test_capacity_approval_requires_capacity_role_and_audits_moves() -> None:
    denied = client.post(
        "/capacity/plans/capacity-plan-20260602-dc001/approve",
        json={"actor": "viewer@example.org", "actor_role": "Viewer", "reason": "not allowed"},
    )
    allowed = client.post(
        "/capacity/plans/capacity-plan-20260602-dc001/approve",
        json={
            "actor": "supply.manager@example.org",
            "actor_role": "Supply Chain Manager",
            "reason": "Move low priority orders to avoid overload.",
        },
    )

    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json()["plan"]["status"] == "approved"
    assert "avoid overload" in allowed.json()["audit_message"]


def test_tms_capacity_export_is_idempotent() -> None:
    response = client.get("/capacity/tms-export")
    assert response.status_code == 200

    payload = response.json()
    assert payload["target"] == "TMS capacity"
    assert payload["idempotency_key"] == "capacity-plan-20260602-dc001:tms:v1"
    assert len(payload["moved_orders"]) == 2
    assert payload["export_channel"] == "local_fallback"


def test_tms_capacity_export_send_uses_local_fallback_with_audit() -> None:
    response = client.post(
        "/capacity/tms-export/send",
        json={
            "actor": "supply.manager@example.org",
            "actor_role": "Supply Chain Manager",
            "service_account": "svc-open-fnr-tms-export",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["export"]["export_channel"] == "local_fallback"
    assert payload["response_code"] == "202"
    assert payload["audit_recorded"] is True


def test_tms_capacity_export_send_requires_service_account() -> None:
    response = client.post(
        "/capacity/tms-export/send",
        json={
            "actor": "supply.manager@example.org",
            "actor_role": "Supply Chain Manager",
            "service_account": "wrong-account",
        },
    )
    assert response.status_code == 403


def test_tms_capacity_export_can_post_to_configured_http_target(monkeypatch) -> None:
    calls = []
    original_url = capacity.settings.tms_capacity_export_url
    original_timeout = capacity.settings.publication_http_timeout_seconds

    class FakeResponse:
        status = 202

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b"accepted by tms"

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        return FakeResponse()

    monkeypatch.setattr("open_fnr_api.capacity.urlopen", fake_urlopen)
    capacity.settings.tms_capacity_export_url = "http://tms.integration.local/capacity"
    capacity.settings.publication_http_timeout_seconds = 29
    try:
        response = client.post(
            "/capacity/tms-export/send",
            json={
                "actor": "supply.manager@example.org",
                "actor_role": "Supply Chain Manager",
                "service_account": "svc-open-fnr-tms-export",
            },
        )
    finally:
        capacity.settings.tms_capacity_export_url = original_url
        capacity.settings.publication_http_timeout_seconds = original_timeout

    assert response.status_code == 200
    payload = response.json()
    assert payload["export"]["export_channel"] == "http_api"
    assert payload["response_message"] == "accepted by tms"
    assert calls[0][0].full_url == "http://tms.integration.local/capacity"
    assert calls[0][0].headers["Idempotency-key"] == "capacity-plan-20260602-dc001:tms:v1"
    assert calls[0][1] == 29
