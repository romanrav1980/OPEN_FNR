from fastapi.testclient import TestClient

from open_fnr_api import supplier_collaboration
from open_fnr_api.main import app
from open_fnr_api.supplier_collaboration import SupplierCollaborationStatus, decide_supplier_risk


client = TestClient(app)


def test_supplier_forecast_share_can_be_exported_with_idempotency_key() -> None:
    response = client.get("/supplier-collaboration/forecast-share")
    assert response.status_code == 200

    share = response.json()[0]
    assert share["supplier_id"] == "SUP_FAST"
    assert share["status"] == "forecast_sent"
    assert share["forecast_qty"] == 18400
    assert share["order_forecast_qty"] == 12000
    assert share["export_channel"] == "local_fallback"
    assert share["idempotency_key"] == "supplier-share-20260602-sup-fast:v1"


def test_supplier_forecast_share_send_uses_local_fallback_with_audit() -> None:
    response = client.post(
        "/supplier-collaboration/forecast-share/supplier-share-20260602-sup-fast/send",
        json={
            "actor": "supplier.coordinator@example.org",
            "actor_role": "Internal Supplier Coordinator",
            "service_account": "svc-open-fnr-supplier-share",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["package"]["export_channel"] == "local_fallback"
    assert payload["response_code"] == "202"
    assert payload["audit_recorded"] is True


def test_supplier_forecast_share_send_requires_service_account() -> None:
    response = client.post(
        "/supplier-collaboration/forecast-share/supplier-share-20260602-sup-fast/send",
        json={
            "actor": "supplier.coordinator@example.org",
            "actor_role": "Internal Supplier Coordinator",
            "service_account": "wrong-account",
        },
    )
    assert response.status_code == 403


def test_supplier_forecast_share_can_post_to_configured_http_target(monkeypatch) -> None:
    calls = []
    original_url = supplier_collaboration.settings.supplier_forecast_share_url
    original_timeout = supplier_collaboration.settings.publication_http_timeout_seconds

    class FakeResponse:
        status = 202

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b"accepted by supplier"

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        return FakeResponse()

    monkeypatch.setattr("open_fnr_api.supplier_collaboration.urlopen", fake_urlopen)
    supplier_collaboration.settings.supplier_forecast_share_url = "http://supplier.integration.local/share"
    supplier_collaboration.settings.publication_http_timeout_seconds = 19
    try:
        response = client.post(
            "/supplier-collaboration/forecast-share/supplier-share-20260602-sup-fast/send",
            json={
                "actor": "supplier.coordinator@example.org",
                "actor_role": "Internal Supplier Coordinator",
                "service_account": "svc-open-fnr-supplier-share",
            },
        )
    finally:
        supplier_collaboration.settings.supplier_forecast_share_url = original_url
        supplier_collaboration.settings.publication_http_timeout_seconds = original_timeout

    assert response.status_code == 200
    payload = response.json()
    assert payload["package"]["export_channel"] == "http_api"
    assert payload["response_message"] == "accepted by supplier"
    assert calls[0][0].full_url == "http://supplier.integration.local/share"
    assert calls[0][0].headers["Idempotency-key"] == "supplier-share-20260602-sup-fast:v1"
    assert calls[0][1] == 19


def test_supplier_performance_is_visible_for_dashboard() -> None:
    response = client.get("/supplier-collaboration/performance")
    assert response.status_code == 200

    performance = response.json()[0]
    assert performance["fill_rate"] == 0.96
    assert performance["on_time_rate"] == 0.91
    assert performance["confirmation_rate"] == 0.88
    assert performance["open_exceptions"] == 1


def test_supplier_confirmation_changes_supply_risk_and_audits_response() -> None:
    denied = client.post(
        "/supplier-collaboration/forecast-share/supplier-share-20260602-sup-fast/confirm",
        json={"actor": "viewer@example.org", "actor_role": "Viewer", "confirmed_qty": 9000, "comment": "No scope"},
    )
    assert denied.status_code == 403

    response = client.post(
        "/supplier-collaboration/forecast-share/supplier-share-20260602-sup-fast/confirm",
        json={
            "actor": "supplier.user@example.org",
            "actor_role": "Supplier User",
            "confirmed_qty": 9000,
            "comment": "Can confirm only 9000 units before cutoff.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "escalated"
    assert payload["supply_exception"] is True
    assert payload["audit"]["idempotency_key"] == "supplier-share-20260602-sup-fast:v1"


def test_supplier_risk_decision_thresholds() -> None:
    assert decide_supplier_risk(12000, 12000) == SupplierCollaborationStatus.CONFIRMED
    assert decide_supplier_risk(10000, 12000) == SupplierCollaborationStatus.RISK_REPORTED
    assert decide_supplier_risk(9000, 12000) == SupplierCollaborationStatus.ESCALATED
