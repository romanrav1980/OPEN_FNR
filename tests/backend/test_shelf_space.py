from fastapi.testclient import TestClient

from open_fnr_api import shelf_space
from open_fnr_api.main import app
from open_fnr_api.shelf_space import PLANOGRAMS, ShelfStatus, validate_display_capacity


client = TestClient(app)


def test_planogram_filter_by_store_zone() -> None:
    response = client.get("/shelf-space/planograms", params={"zone": "front"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["zone"] == "front"


def test_display_capacity_warning_and_direct_to_shelf_recommendation() -> None:
    warning = validate_display_capacity(PLANOGRAMS[0], requested_display_qty=140)
    direct = validate_display_capacity(PLANOGRAMS[0], requested_display_qty=50)

    assert warning.status == ShelfStatus.CAPACITY_WARNING
    assert warning.warning == "requested display stock exceeds display capacity"
    assert warning.direct_to_shelf_recommended is False
    assert direct.status == ShelfStatus.VALID
    assert direct.direct_to_shelf_recommended is True


def test_shelf_validations_api_contains_warning_and_valid_rows() -> None:
    response = client.get("/shelf-space/validations")
    assert response.status_code == 200

    statuses = {item["status"] for item in response.json()["items"]}
    assert statuses == {"capacity_warning", "valid"}


def test_category_or_store_role_can_approve_shelf_exception_with_audit() -> None:
    response = client.post(
        "/shelf-space/validations/S001/SKU001/approve",
        json={
            "actor": "category.manager@example.org",
            "actor_role": "Category Manager",
            "reason": "Temporary display approved for promo island.",
        },
    )

    assert response.status_code == 200
    assert response.json()["validation"]["status"] == "approved"
    assert "Temporary display approved" in response.json()["audit_message"]


def test_shelf_approval_rejects_wrong_role() -> None:
    response = client.post(
        "/shelf-space/validations/S001/SKU001/approve",
        json={"actor": "viewer@example.org", "actor_role": "Viewer", "reason": "not allowed"},
    )

    assert response.status_code == 403


def test_planogram_export_preview_is_idempotent_and_uses_local_fallback() -> None:
    response = client.get("/shelf-space/planogram-export/S001/SKU001")
    assert response.status_code == 200

    payload = response.json()
    assert payload["target"] == "Planogram system"
    assert payload["idempotency_key"] == "S001:SKU001:planogram:v1"
    assert payload["export_channel"] == "local_fallback"
    assert payload["status"] == "capacity_warning"


def test_planogram_export_send_requires_service_account() -> None:
    response = client.post(
        "/shelf-space/planogram-export/S001/SKU001/send",
        json={
            "actor": "category.manager@example.org",
            "actor_role": "Category Manager",
            "service_account": "wrong-account",
        },
    )

    assert response.status_code == 403


def test_planogram_export_send_uses_local_fallback_with_audit() -> None:
    response = client.post(
        "/shelf-space/planogram-export/S001/SKU001/send",
        json={
            "actor": "category.manager@example.org",
            "actor_role": "Category Manager",
            "service_account": "svc-open-fnr-planogram-export",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["export"]["export_channel"] == "local_fallback"
    assert payload["response_code"] == "202"
    assert payload["audit_recorded"] is True


def test_planogram_export_can_post_to_configured_http_target(monkeypatch) -> None:
    calls = []
    original_url = shelf_space.settings.planogram_export_url
    original_timeout = shelf_space.settings.publication_http_timeout_seconds

    class FakeResponse:
        status = 202

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b"accepted by planogram"

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        return FakeResponse()

    monkeypatch.setattr("open_fnr_api.shelf_space.urlopen", fake_urlopen)
    shelf_space.settings.planogram_export_url = "http://planogram.integration.local/decisions"
    shelf_space.settings.publication_http_timeout_seconds = 19
    try:
        response = client.post(
            "/shelf-space/planogram-export/S001/SKU001/send",
            json={
                "actor": "category.manager@example.org",
                "actor_role": "Category Manager",
                "service_account": "svc-open-fnr-planogram-export",
            },
        )
    finally:
        shelf_space.settings.planogram_export_url = original_url
        shelf_space.settings.publication_http_timeout_seconds = original_timeout

    assert response.status_code == 200
    payload = response.json()
    assert payload["export"]["export_channel"] == "http_api"
    assert payload["response_message"] == "accepted by planogram"
    assert calls[0][0].full_url == "http://planogram.integration.local/decisions"
    assert calls[0][0].headers["Idempotency-key"] == "S001:SKU001:planogram:v1"
    assert calls[0][1] == 19
