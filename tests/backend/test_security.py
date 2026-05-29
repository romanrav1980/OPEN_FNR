from fastapi.testclient import TestClient

from open_fnr_api import security
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
    assert service_response.json()["total"] == 2
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


def test_access_check_enforces_supplier_scope_when_present() -> None:
    allowed = client.get(
        "/security/access-check",
        params={
            "user_id": "u-viewer-001",
            "region": "north",
            "category": "fresh",
            "supplier_id": "SUP001",
            "role": "Viewer",
        },
    )
    denied = client.get(
        "/security/access-check",
        params={
            "user_id": "u-viewer-001",
            "region": "north",
            "category": "fresh",
            "supplier_id": "SUP002",
            "role": "Viewer",
        },
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
            "reason": "Role provisioned through configured IdP path.",
        },
    )

    assert response.status_code == 200
    assert response.json()["request"]["status"] == "provisioned"


def test_idp_provision_preview_is_idempotent_and_uses_local_fallback() -> None:
    response = client.get("/security/access-requests/access-20260528-001/idp-provision")
    assert response.status_code == 200

    payload = response.json()
    assert payload["target"] == "IdP provisioning"
    assert payload["idempotency_key"] == "access-20260528-001:idp:v1"
    assert payload["export_channel"] == "local_fallback"


def test_idp_provision_send_requires_service_account() -> None:
    response = client.post(
        "/security/access-requests/access-20260528-001/idp-provision/send",
        json={
            "actor": "user.manager@example.org",
            "actor_role": "User Manager",
            "service_account": "wrong-account",
            "reason": "Provision role.",
        },
    )

    assert response.status_code == 403


def test_idp_provision_send_uses_local_fallback_with_audit() -> None:
    response = client.post(
        "/security/access-requests/access-20260528-001/idp-provision/send",
        json={
            "actor": "user.manager@example.org",
            "actor_role": "User Manager",
            "service_account": "svc-open-fnr-idp-provisioning",
            "reason": "Provision approved role.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["provision"]["export_channel"] == "local_fallback"
    assert payload["response_code"] == "202"
    assert payload["audit_recorded"] is True


def test_idp_provision_can_post_to_configured_http_target(monkeypatch) -> None:
    calls = []
    original_url = security.settings.idp_provisioning_url
    original_timeout = security.settings.publication_http_timeout_seconds

    class FakeResponse:
        status = 202

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b"accepted by idp"

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        return FakeResponse()

    monkeypatch.setattr("open_fnr_api.security.urlopen", fake_urlopen)
    security.settings.idp_provisioning_url = "http://idp.integration.local/provision"
    security.settings.publication_http_timeout_seconds = 23
    try:
        response = client.post(
            "/security/access-requests/access-20260528-001/idp-provision/send",
            json={
                "actor": "user.manager@example.org",
                "actor_role": "User Manager",
                "service_account": "svc-open-fnr-idp-provisioning",
                "reason": "Provision approved role.",
            },
        )
    finally:
        security.settings.idp_provisioning_url = original_url
        security.settings.publication_http_timeout_seconds = original_timeout

    assert response.status_code == 200
    payload = response.json()
    assert payload["provision"]["export_channel"] == "http_api"
    assert payload["response_message"] == "accepted by idp"
    assert calls[0][0].full_url == "http://idp.integration.local/provision"
    assert calls[0][0].headers["Idempotency-key"] == "access-20260528-001:idp:v1"
    assert calls[0][1] == 23


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


def test_access_review_report_requires_security_owner_or_admin() -> None:
    response = client.get(
        "/security/access-review/report",
        params={"business_date": "2026-05-29", "reviewer_role": "Viewer"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "access review requires Security Owner or Admin role"


def test_access_review_report_flags_excessive_admin_access() -> None:
    response = client.get(
        "/security/access-review/report",
        params={"business_date": "2026-05-29", "reviewer_role": "Security Owner"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["review_id"] == "access-review-2026-05-29"
    assert payload["process_key"] == "access_review_process"
    assert payload["status"] == "action_required"
    assert payload["excessive_access_count"] >= 1
    admin_item = next(item for item in payload["items"] if item["user_id"] == "u-admin-001")
    assert admin_item["status"] == "review_required"
    assert admin_item["recommendation"] == "confirm_admin_need_or_reduce_scope"


def test_security_helpers_cover_role_and_scope() -> None:
    admin = USERS[0]
    viewer = USERS[1]

    assert has_role(admin, RoleName.SECURITY_OWNER) is True
    assert has_role(viewer, RoleName.SUPPLY_CHAIN_MANAGER) is False
    assert has_scope(viewer, region="north", category="fresh", supplier_id="SUP001") is True
    assert has_scope(viewer, region="north", category="fresh", supplier_id="SUP002") is False
    assert has_scope(viewer, region="north", category="grocery") is False
