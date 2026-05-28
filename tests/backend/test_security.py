from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.security import (
    RoleName,
    USERS,
    has_role,
    has_scope,
)


client = TestClient(app)


def test_admin_can_view_users_and_service_accounts() -> None:
    users_response = client.get("/security/users", params={"actor_role": "Admin"})
    service_response = client.get("/security/service-accounts", params={"actor_role": "Admin"})

    assert users_response.status_code == 200
    assert service_response.status_code == 200
    assert users_response.json()["total"] == 2
    assert service_response.json()["items"][0]["secret_rotation_days"] == 90


def test_non_admin_cannot_view_admin_console_data() -> None:
    response = client.get("/security/users", params={"actor_role": "Viewer"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin role required"


def test_access_check_enforces_role_region_and_category_scope() -> None:
    allowed = client.get(
        "/security/access-check",
        params={"user_id": "u-viewer-001", "region": "north", "category": "fresh", "role": "Viewer"},
    )
    denied = client.get(
        "/security/access-check",
        params={"user_id": "u-viewer-001", "region": "south", "category": "fresh", "role": "Viewer"},
    )

    assert allowed.status_code == 200
    assert allowed.json()["allowed"] is True
    assert denied.status_code == 200
    assert denied.json()["allowed"] is False


def test_security_owner_can_approve_access_request_with_audit() -> None:
    response = client.post(
        "/security/access-requests/access-20260528-001/approve",
        json={
            "actor": "security.owner@example.org",
            "actor_role": "Security Owner",
            "reason": "Business owner confirmed regional supply role.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["request"]["status"] == "approved"
    assert payload["audit_event"]["event_type"] == "access_approve"


def test_user_manager_can_provision_after_approval_step() -> None:
    response = client.post(
        "/security/access-requests/access-20260528-001/provision",
        json={
            "actor": "user.manager@example.org",
            "actor_role": "User Manager",
            "reason": "Role provisioned in local IdP mock.",
        },
    )

    assert response.status_code == 200
    assert response.json()["request"]["status"] == "provisioned"


def test_access_request_rejects_wrong_actor_role() -> None:
    response = client.post(
        "/security/access-requests/access-20260528-001/approve",
        json={
            "actor": "viewer@example.org",
            "actor_role": "Viewer",
            "reason": "Trying to self-approve.",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Security Owner role required"


def test_security_helpers_cover_role_and_scope() -> None:
    admin = USERS[0]
    viewer = USERS[1]

    assert has_role(admin, RoleName.SECURITY_OWNER) is True
    assert has_role(viewer, RoleName.SUPPLY_CHAIN_MANAGER) is False
    assert has_scope(viewer, region="north", category="fresh") is True
    assert has_scope(viewer, region="north", category="grocery") is False
