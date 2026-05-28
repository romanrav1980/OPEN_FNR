from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.store_management import calculate_virtual_stock


client = TestClient(app)


def test_true_inventory_has_virtual_stock_confidence_and_suggestion() -> None:
    response = client.get("/store-management/true-inventory", params={"store_id": "S001"})
    assert response.status_code == 200

    inventory = response.json()[0]
    assert inventory["virtual_stock"] == 40
    assert inventory["confidence"] == 0.58
    assert inventory["status"] == "low_confidence"
    assert inventory["suggestion"] == "Create store stock check and correct stock if count differs."


def test_virtual_stock_calculation_uses_movements_deliveries_and_corrections() -> None:
    assert calculate_virtual_stock(system_stock=120, pos_movements=72, deliveries=0, corrections=-8) == 40
    assert calculate_virtual_stock(system_stock=4, pos_movements=20, deliveries=0, corrections=0) == 0


def test_store_tasks_are_scoped_by_store_and_include_display_confirmation() -> None:
    response = client.get("/store-management/tasks", params={"store_id": "S001"})
    assert response.status_code == 200

    tasks = response.json()
    assert {task["task_type"] for task in tasks} == {"stock_check", "promo_display_confirmation"}
    assert all(task["store_id"] == "S001" for task in tasks)


def test_store_task_completion_requires_role_scope_and_returns_audit() -> None:
    denied_role = client.post(
        "/store-management/tasks/store-task-stock-s001-sku001/complete",
        json={
            "actor": "viewer@example.org",
            "actor_role": "Viewer",
            "store_id": "S001",
            "counted_qty": 38,
            "comment": "No scope.",
        },
    )
    assert denied_role.status_code == 403

    denied_store = client.post(
        "/store-management/tasks/store-task-stock-s001-sku001/complete",
        json={
            "actor": "store.ops@example.org",
            "actor_role": "Store Operations",
            "store_id": "S002",
            "counted_qty": 38,
            "comment": "Wrong store.",
        },
    )
    assert denied_store.status_code == 403

    response = client.post(
        "/store-management/tasks/store-task-stock-s001-sku001/complete",
        json={
            "actor": "store.ops@example.org",
            "actor_role": "Store Operations",
            "store_id": "S001",
            "counted_qty": 38,
            "comment": "Shelf count completed.",
            "photo_reference": "store-photo-placeholder-001",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "corrected"
    assert payload["quality_flag"] == "store_feedback_received"
    assert payload["audit"]["photo_reference"] == "store-photo-placeholder-001"
