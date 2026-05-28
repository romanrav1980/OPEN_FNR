from fastapi.testclient import TestClient

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
