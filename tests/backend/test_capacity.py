from fastapi.testclient import TestClient

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
    assert payload["target"] == "TMS capacity mock"
    assert payload["idempotency_key"] == "capacity-plan-20260602-dc001:tms:v1"
    assert len(payload["moved_orders"]) == 2
