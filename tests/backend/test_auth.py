import base64
import hashlib
import json
import time

from fastapi.testclient import TestClient
import pytest

from open_fnr_api import auth
from open_fnr_api.main import app


client = TestClient(app)


def make_unsigned_jwt(payload: dict[str, object]) -> str:
    header = {"alg": "none", "typ": "JWT"}

    def encode(segment: dict[str, object]) -> str:
        raw = json.dumps(segment, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    return f"{encode(header)}.{encode(payload)}."


RSA_N = 812353529305625301795291781665081048715245910406602999871294860206990169569901233349416236618592954912065331503518262347884059398030024464102231122003132141898486636541795850096111081466334357765047662658393940543649468394982657873
RSA_D = 701142520792417950105294408195146398531789445994621338903517002114964049952263046285452941457965889415154423859751091490924584147981816290238671987083620457456761981113000554722255102083175117975822603056492774899486438362171184373
RSA_E = 65537


def encode_segment(segment: dict[str, object]) -> str:
    raw = json.dumps(segment, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def encode_int(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def make_rs256_jwt(payload: dict[str, object], kid: str = "test-key") -> str:
    header = {"alg": "RS256", "typ": "JWT", "kid": kid}
    signing_input = f"{encode_segment(header)}.{encode_segment(payload)}".encode("ascii")
    digest_info_prefix = bytes.fromhex("3031300d060960864801650304020105000420")
    expected = digest_info_prefix + hashlib.sha256(signing_input).digest()
    key_size = (RSA_N.bit_length() + 7) // 8
    padding = b"\xff" * (key_size - len(expected) - 3)
    encoded = b"\x00\x01" + padding + b"\x00" + expected
    signature = pow(int.from_bytes(encoded, "big"), RSA_D, RSA_N).to_bytes(key_size, "big")
    signature_segment = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    return f"{signing_input.decode('ascii')}.{signature_segment}"


def jwks() -> dict[str, object]:
    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": "test-key",
                "alg": "RS256",
                "use": "sig",
                "n": encode_int(RSA_N),
                "e": encode_int(RSA_E),
            }
        ]
    }


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


def test_idp_readiness_reports_blocked_when_required_settings_are_missing() -> None:
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
    auth.settings.oidc_issuer = ""
    auth.settings.oidc_audience = "open-fnr-api"
    auth.settings.oidc_jwks_url = ""
    try:
        response = client.get("/auth/idp-readiness")
    finally:
        restore_auth_settings(original)

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "blocked"
    assert any(check["check"] == "jwks_configured" and check["status"] == "blocked" for check in payload["checks"])


def test_idp_readiness_reports_ready_when_stage_oidc_is_complete() -> None:
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
    auth.settings.oidc_jwks_url = "https://idp.example.org/.well-known/jwks.json"
    try:
        response = client.get("/auth/idp-readiness")
    finally:
        restore_auth_settings(original)

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


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
    auth.settings.runtime_mode = "test"
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


def test_stage_requires_jwks_url_when_dev_bypass_disabled() -> None:
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
    auth.settings.oidc_jwks_url = ""
    token = make_unsigned_jwt({"sub": "u-123", "exp": int(time.time()) + 300})
    try:
        response = client.get("/auth/context", headers={"Authorization": f"Bearer {token}"})
    finally:
        restore_auth_settings(original)

    assert response.status_code == 401
    assert "JWKS URL required" in response.json()["detail"]


def test_jwks_rs256_signature_allows_valid_token(monkeypatch: pytest.MonkeyPatch) -> None:
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
    auth.settings.runtime_mode = "test"
    auth.settings.oidc_issuer = "https://idp.example.org"
    auth.settings.oidc_audience = "open-fnr-api"
    auth.settings.oidc_jwks_url = "https://idp.example.org/.well-known/jwks.json"
    monkeypatch.setattr(auth, "load_jwks", jwks)
    token = make_rs256_jwt(
        {
            "sub": "u-123",
            "email": "planner@example.org",
            "roles": ["Forecast Planner"],
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
    assert response.json()["email"] == "planner@example.org"


def test_jwks_rs256_signature_rejects_tampered_token(monkeypatch: pytest.MonkeyPatch) -> None:
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
    auth.settings.oidc_jwks_url = "https://idp.example.org/.well-known/jwks.json"
    monkeypatch.setattr(auth, "load_jwks", jwks)
    token = make_rs256_jwt({"sub": "u-123", "exp": int(time.time()) + 300})
    tampered = token[:-2] + "xx"
    try:
        response = client.get("/auth/context", headers={"Authorization": f"Bearer {tampered}"})
    finally:
        restore_auth_settings(original)

    assert response.status_code == 401
    assert "signature verification failed" in response.json()["detail"]


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
    auth.settings.runtime_mode = "test"
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


def test_jwt_claims_reject_missing_expiration() -> None:
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
    auth.settings.runtime_mode = "test"
    token = make_unsigned_jwt({"sub": "u-123"})
    try:
        response = client.get("/auth/context", headers={"Authorization": f"Bearer {token}"})
    finally:
        restore_auth_settings(original)

    assert response.status_code == 401
    assert "expiration missing" in response.json()["detail"]


def test_jwt_claims_reject_token_before_nbf_outside_clock_skew() -> None:
    original = (
        auth.settings.auth_enabled,
        auth.settings.auth_dev_bypass_enabled,
        auth.settings.runtime_mode,
        auth.settings.oidc_issuer,
        auth.settings.oidc_audience,
        auth.settings.oidc_jwks_url,
    )
    original_skew = auth.settings.oidc_clock_skew_seconds
    auth.settings.auth_enabled = True
    auth.settings.auth_dev_bypass_enabled = False
    auth.settings.runtime_mode = "test"
    auth.settings.oidc_clock_skew_seconds = 5
    token = make_unsigned_jwt(
        {
            "sub": "u-123",
            "exp": int(time.time()) + 300,
            "nbf": int(time.time()) + 60,
        }
    )
    try:
        response = client.get("/auth/context", headers={"Authorization": f"Bearer {token}"})
    finally:
        restore_auth_settings(original)
        auth.settings.oidc_clock_skew_seconds = original_skew

    assert response.status_code == 401
    assert "token not yet valid" in response.json()["detail"]


def test_stage_rejects_dev_bypass_header_even_if_bypass_flag_is_true() -> None:
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
    auth.settings.runtime_mode = "stage"
    try:
        response = client.get("/auth/context", headers={"X-Open-FNR-Dev-User": "admin@example.org"})
    finally:
        restore_auth_settings(original)

    assert response.status_code == 401
    assert response.json()["detail"] == "Bearer token required"
