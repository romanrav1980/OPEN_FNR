from fastapi.testclient import TestClient

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
    assert share["export_channel"] == "api_csv_mock"
    assert share["idempotency_key"] == "supplier-share-20260602-sup-fast:v1"


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
