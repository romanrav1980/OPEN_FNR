import base64
import json
import time

from fastapi.testclient import TestClient

from open_fnr_api import auth
from open_fnr_api.main import app


client = TestClient(app)


def make_unsigned_jwt(payload: dict[str, object]) -> str:
    header = {"alg": "none", "typ": "JWT"}

    def encode(segment: dict[str, object]) -> str:
        raw = json.dumps(segment, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    return f"{encode(header)}.{encode(payload)}."


def restore_auth_settings(original: tuple[bool, bool, str, str, str, str]) -> None:
    (
        auth.settings.auth_enabled,
        auth.settings.auth_dev_bypass_enabled,
        auth.settings.runtime_mode,
        auth.settings.oidc_issuer,
        auth.settings.oidc_audience,
        auth.settings.oidc_jwks_url,
    ) = original


def test_auth_disabled_keeps_context_open() -> None:
    original = (
        auth.settings.auth_enabled,
        auth.settings.auth_dev_bypass_enabled,
        auth.settings.runtime_mode,
        auth.settings.oidc_issuer,
        auth.settings.oidc_audience,
        auth.settings.oidc_jwks_url,
    )
    auth.settings.auth_enabled = False
    try:
        response = client.get("/auth/context")
    finally:
        restore_auth_settings(original)

    assert response.status_code == 200
    assert response.json()["auth_mode"] == "disabled"


def test_auth_enabled_rejects_api_without_bearer_token() -> None:
    original = (
        auth.settings.auth_enabled,
        auth.settings.auth_dev_bypass_enabled,
        auth.settings.runtime_mode,
        auth.settings.oidc_issuer,
        auth.settings.oidc_audience,
        auth.settings.oidc_jwks_url,
    )
    auth.settings.auth_enabled = True
    auth.settings.auth_dev_bypass_enabled = False
    try:
        response = client.get("/data/contracts")
        metadata = client.get("/metadata")
    finally:
        restore_auth_settings(original)

    assert response.status_code == 401
    assert response.json()["detail"] == "Bearer token required"
    assert metadata.status_code == 200


def test_dev_bypass_allows_dev_and_test_when_enabled() -> None:
    original = (
        auth.settings.auth_enabled,
        auth.settings.auth_dev_bypass_enabled,
        auth.settings.runtime_mode,
        auth.settings.oidc_issuer,
        auth.settings.oidc_audience,
        auth.settings.oidc_jwks_url,
    )
    auth.settings.auth_enabled = True
    auth.settings.auth_dev_bypass_enabled = True
    auth.settings.runtime_mode = "test"
    try:
        response = client.get(
            "/auth/context",
            headers={
                "X-Open-FNR-Dev-User": "planner@example.org",
                "X-Open-FNR-Dev-Roles": "Forecast Planner,Admin",
                "X-Open-FNR-Dev-Scopes": "forecast:read replenishment:write",
            },
        )
    finally:
        restore_auth_settings(original)

    assert response.status_code == 200
    payload = response.json()
    assert payload["auth_mode"] == "dev_bypass"
    assert payload["subject"] == "planner@example.org"
    assert "forecast:read" in payload["scopes"]


def test_jwt_claims_allow_request_when_issuer_and_audience_match() -> None:
    original = (
        auth.settings.auth_enabled,
        auth.settings.auth_dev_bypass_enabled,
        auth.settings.runtime_mode,
        auth.settings.oidc_issuer,
        auth.settings.oidc_audience,
        auth.settings.oidc_jwks_url,
    )
    auth.settings.auth_enabled = True
    auth.settings.auth_dev_bypass_enabled = False
    auth.settings.runtime_mode = "stage"
    auth.settings.oidc_issuer = "https://idp.example.org"
    auth.settings.oidc_audience = "open-fnr-api"
    token = make_unsigned_jwt(
        {
            "sub": "u-123",
            "email": "planner@example.org",
            "roles": ["Forecast Planner"],
            "scope": "forecast:read",
            "iss": "https://idp.example.org",
            "aud": "open-fnr-api",
            "exp": int(time.time()) + 300,
        }
    )
    try:
        response = client.get("/auth/context", headers={"Authorization": f"Bearer {token}"})
    finally:
        restore_auth_settings(original)

    assert response.status_code == 200
    payload = response.json()
    assert payload["auth_mode"] == "jwt"
    assert payload["email"] == "planner@example.org"
    assert payload["roles"] == ["Forecast Planner"]


def test_jwt_claims_reject_wrong_audience() -> None:
    original = (
        auth.settings.auth_enabled,
        auth.settings.auth_dev_bypass_enabled,
        auth.settings.runtime_mode,
        auth.settings.oidc_issuer,
        auth.settings.oidc_audience,
        auth.settings.oidc_jwks_url,
    )
    auth.settings.auth_enabled = True
    auth.settings.auth_dev_bypass_enabled = False
    auth.settings.runtime_mode = "stage"
    auth.settings.oidc_audience = "open-fnr-api"
    token = make_unsigned_jwt(
        {
            "sub": "u-123",
            "aud": "wrong-api",
            "exp": int(time.time()) + 300,
        }
    )
    try:
        response = client.get("/auth/context", headers={"Authorization": f"Bearer {token}"})
    finally:
        restore_auth_settings(original)

    assert response.status_code == 401
    assert "audience mismatch" in response.json()["detail"]
