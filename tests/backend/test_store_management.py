from fastapi.testclient import TestClient

from open_fnr_api import store_management
from open_fnr_api.main import app
from open_fnr_api.store_management import calculate_virtual_stock


client = TestClient(app)


class CapturingOperationalDecisionRepository:
    mode = "in_memory"

    def __init__(self) -> None:
        self.decisions = []

    def upsert_decision(self, decision):
        self.decisions.append(decision)
        return decision


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


def test_store_task_completion_writes_operational_decision_boundary(monkeypatch) -> None:
    repository = CapturingOperationalDecisionRepository()
    monkeypatch.setattr(store_management, "operational_decision_repository", repository)

    response = client.post(
        "/store-management/tasks/store-task-stock-s001-sku001/complete",
        json={
            "actor": "store.ops@example.org",
            "actor_role": "Store Operations",
            "store_id": "S001",
            "counted_qty": 38,
            "comment": "Repository boundary check.",
            "photo_reference": "store-photo-placeholder-001",
        },
    )

    assert response.status_code == 200
    assert repository.decisions[0].decision_type == "store_task_completion"
    assert repository.decisions[0].object_id == "store-task-stock-s001-sku001"
    assert repository.decisions[0].status == "corrected"
    assert repository.decisions[0].payload["photo_reference"] == "store-photo-placeholder-001"


def test_store_task_dispatch_preview_is_idempotent_and_uses_local_fallback() -> None:
    response = client.get("/store-management/tasks/store-task-stock-s001-sku001/dispatch")
    assert response.status_code == 200

    payload = response.json()
    assert payload["target"] == "Store App task"
    assert payload["idempotency_key"] == "store-task-stock-s001-sku001:store-app:v1"
    assert payload["export_channel"] == "local_fallback"


def test_store_task_dispatch_send_requires_service_account() -> None:
    response = client.post(
        "/store-management/tasks/store-task-stock-s001-sku001/dispatch/send",
        json={
            "actor": "store.ops@example.org",
            "actor_role": "Store Operations",
            "service_account": "wrong-account",
        },
    )

    assert response.status_code == 403


def test_store_task_dispatch_send_uses_local_fallback_with_audit() -> None:
    response = client.post(
        "/store-management/tasks/store-task-stock-s001-sku001/dispatch/send",
        json={
            "actor": "store.ops@example.org",
            "actor_role": "Store Operations",
            "service_account": "svc-open-fnr-store-app",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["dispatch"]["export_channel"] == "local_fallback"
    assert payload["response_code"] == "202"
    assert payload["audit_recorded"] is True


def test_store_task_dispatch_can_post_to_configured_http_target(monkeypatch) -> None:
    calls = []
    original_url = store_management.settings.store_app_task_export_url
    original_timeout = store_management.settings.publication_http_timeout_seconds

    class FakeResponse:
        status = 202

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b"accepted by store app"

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        return FakeResponse()

    monkeypatch.setattr("open_fnr_api.store_management.urlopen", fake_urlopen)
    store_management.settings.store_app_task_export_url = "http://store-app.integration.local/tasks"
    store_management.settings.publication_http_timeout_seconds = 17
    try:
        response = client.post(
            "/store-management/tasks/store-task-stock-s001-sku001/dispatch/send",
            json={
                "actor": "store.ops@example.org",
                "actor_role": "Store Operations",
                "service_account": "svc-open-fnr-store-app",
            },
        )
    finally:
        store_management.settings.store_app_task_export_url = original_url
        store_management.settings.publication_http_timeout_seconds = original_timeout

    assert response.status_code == 200
    payload = response.json()
    assert payload["dispatch"]["export_channel"] == "http_api"
    assert payload["response_message"] == "accepted by store app"
    assert calls[0][0].full_url == "http://store-app.integration.local/tasks"
    assert calls[0][0].headers["Idempotency-key"] == "store-task-stock-s001-sku001:store-app:v1"
    assert calls[0][1] == 17
