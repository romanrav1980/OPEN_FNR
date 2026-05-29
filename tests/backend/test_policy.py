import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.policy import Principal, assert_any_role, assert_object_scope, assert_service_account, has_any_role, has_object_scope


client = TestClient(app)


def test_shared_policy_allows_admin_and_matching_role() -> None:
    admin = Principal(subject="admin", roles=("Admin",), regions=("all",), categories=("all",))
    planner = Principal(
        subject="planner",
        roles=("Forecast Planner",),
        regions=("north",),
        categories=("fresh",),
        suppliers=("SUP001",),
    )

    assert has_any_role(admin, {"Security Owner"}) is True
    assert has_any_role(planner, {"Forecast Planner"}) is True
    assert has_object_scope(planner, "north", "fresh") is True
    assert has_object_scope(planner, "north", "fresh", "SUP001") is True
    assert has_object_scope(planner, "north", "fresh", "SUP002") is False


def test_shared_policy_denies_role_scope_and_service_account() -> None:
    viewer = Principal(subject="viewer", roles=("Viewer",), regions=("north",), categories=("fresh",))

    with pytest.raises(HTTPException) as role_error:
        assert_any_role(viewer, {"Supply Chain Manager"}, "role denied")
    with pytest.raises(HTTPException) as scope_error:
        assert_object_scope(viewer, "south", "fresh", "scope denied")
    with pytest.raises(HTTPException) as service_error:
        assert_service_account("wrong", "expected", "service denied")

    assert role_error.value.status_code == 403
    assert scope_error.value.detail == "scope denied"
    assert service_error.value.detail == "service denied"


def test_security_policy_check_endpoint_returns_allowed_for_scoped_viewer() -> None:
    response = client.get(
        "/security/policy-check",
        params={"user_id": "u-viewer-001", "region": "north", "category": "fresh", "allowed_role": "Viewer"},
    )

    assert response.status_code == 200
    assert response.json()["policy"] == "shared_policy_v1"


def test_security_policy_check_endpoint_denies_out_of_scope_object() -> None:
    response = client.get(
        "/security/policy-check",
        params={"user_id": "u-viewer-001", "region": "south", "category": "fresh", "allowed_role": "Viewer"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "object scope policy denied"


def test_security_object_access_check_allows_scoped_supplier_object() -> None:
    response = client.get(
        "/security/object-access-check",
        params={
            "user_id": "u-viewer-001",
            "region": "north",
            "category": "fresh",
            "supplier_id": "SUP001",
            "object_type": "supplier_forecast",
            "object_id": "SUP001:SKU001",
            "allowed_role": "Viewer",
        },
    )

    assert response.status_code == 200
    assert response.json()["policy"] == "shared_policy_v2_supplier_scope"


def test_security_object_access_check_denies_wrong_supplier_object() -> None:
    response = client.get(
        "/security/object-access-check",
        params={
            "user_id": "u-viewer-001",
            "region": "north",
            "category": "fresh",
            "supplier_id": "SUP002",
            "object_type": "supplier_forecast",
            "object_id": "SUP002:SKU001",
            "allowed_role": "Viewer",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "object scope policy denied"
