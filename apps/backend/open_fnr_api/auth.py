from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Callable
from urllib.request import urlopen

from fastapi import APIRouter, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from .config import settings


PUBLIC_PATHS = (
    "/health",
    "/ready",
    "/metadata",
    "/docs",
    "/redoc",
    "/openapi.json",
)

router = APIRouter(prefix="/auth", tags=["auth"])


@dataclass(frozen=True)
class AuthContext:
    subject: str
    email: str
    roles: tuple[str, ...]
    scopes: tuple[str, ...]
    auth_mode: str


def is_public_path(path: str) -> bool:
    return path in PUBLIC_PATHS or path.startswith("/docs/") or path.startswith("/redoc/")


def decode_jwt_payload_without_signature(token: str) -> dict[str, object]:
    parts = token.split(".")
    if len(parts) < 2:
        raise ValueError("token must have header and payload")
    return json.loads(base64url_decode(parts[1]).decode("utf-8"))


def base64url_decode(segment: str) -> bytes:
    padded = segment + "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def decode_jwt_header(token: str) -> dict[str, object]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("token must have three segments")
    return json.loads(base64url_decode(parts[0]).decode("utf-8"))


def load_jwks() -> dict[str, object]:
    if not settings.oidc_jwks_url:
        raise ValueError("JWKS URL required")
    with urlopen(settings.oidc_jwks_url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def int_from_jwk_segment(segment: object) -> int:
    if not isinstance(segment, str):
        raise ValueError("invalid RSA JWK")
    return int.from_bytes(base64url_decode(segment), "big")


def verify_rs256_signature(signing_input: bytes, signature: bytes, jwk: dict[str, object]) -> bool:
    n = int_from_jwk_segment(jwk.get("n"))
    e = int_from_jwk_segment(jwk.get("e"))
    key_size = (n.bit_length() + 7) // 8
    decrypted = pow(int.from_bytes(signature, "big"), e, n).to_bytes(key_size, "big")
    digest_info_prefix = bytes.fromhex("3031300d060960864801650304020105000420")
    expected = digest_info_prefix + hashlib.sha256(signing_input).digest()
    padding_length = key_size - len(expected) - 3
    if padding_length < 8:
        return False
    encoded = b"\x00\x01" + (b"\xff" * padding_length) + b"\x00" + expected
    return hmac.compare_digest(decrypted, encoded)


def verify_jwt_signature(token: str, jwks: dict[str, object] | None = None) -> None:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("token must have three segments")
    header = decode_jwt_header(token)
    if header.get("alg") != "RS256":
        raise ValueError("only RS256 JWT is accepted")
    keys = (jwks or load_jwks()).get("keys")
    if not isinstance(keys, list):
        raise ValueError("JWKS keys missing")
    kid = header.get("kid")
    matching_keys = [key for key in keys if isinstance(key, dict) and (kid is None or key.get("kid") == kid)]
    if not matching_keys:
        raise ValueError("matching JWKS key not found")
    signing_input = f"{parts[0]}.{parts[1]}".encode("ascii")
    signature = base64url_decode(parts[2])
    if not any(verify_rs256_signature(signing_input, signature, key) for key in matching_keys):
        raise ValueError("signature verification failed")


def tuple_from_claim(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(item for item in value.split() if item)
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    return (str(value),)


def validate_jwt_claims(payload: dict[str, object]) -> AuthContext:
    now = int(time.time())
    exp = payload.get("exp")
    if isinstance(exp, int | float) and exp < now:
        raise ValueError("token expired")
    if settings.oidc_issuer and payload.get("iss") != settings.oidc_issuer:
        raise ValueError("issuer mismatch")
    audience = payload.get("aud")
    if settings.oidc_audience:
        if isinstance(audience, list):
            audience_valid = settings.oidc_audience in audience
        else:
            audience_valid = audience == settings.oidc_audience
        if not audience_valid:
            raise ValueError("audience mismatch")
    roles = tuple_from_claim(payload.get("roles") or payload.get("groups"))
    scopes = tuple_from_claim(payload.get("scope") or payload.get("scp"))
    subject = str(payload.get("sub") or "")
    if not subject:
        raise ValueError("subject missing")
    return AuthContext(
        subject=subject,
        email=str(payload.get("email") or subject),
        roles=roles,
        scopes=scopes,
        auth_mode="jwt",
    )


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method == "OPTIONS" or is_public_path(request.url.path) or not settings.auth_enabled:
            return await call_next(request)

        dev_user = request.headers.get("X-Open-FNR-Dev-User")
        if settings.auth_dev_bypass_enabled and settings.runtime_mode in {"dev", "test"} and dev_user:
            request.state.auth = AuthContext(
                subject=dev_user,
                email=dev_user,
                roles=tuple_from_claim(request.headers.get("X-Open-FNR-Dev-Roles", "Admin")),
                scopes=tuple_from_claim(request.headers.get("X-Open-FNR-Dev-Scopes", "open-fnr:*")),
                auth_mode="dev_bypass",
            )
            return await call_next(request)

        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Bearer token required"})
        token = authorization.removeprefix("Bearer ").strip()
        try:
            if settings.oidc_jwks_url:
                verify_jwt_signature(token)
            elif settings.runtime_mode in {"stage", "prod"} and not settings.auth_dev_bypass_enabled:
                raise ValueError("JWKS URL required for stage/prod")
            request.state.auth = validate_jwt_claims(decode_jwt_payload_without_signature(token))
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            return JSONResponse(status_code=401, content={"detail": f"invalid token: {exc}"})
        return await call_next(request)


@router.get("/context")
def get_auth_context(request: Request) -> dict[str, object]:
    context = getattr(request.state, "auth", None)
    if context is None:
        return {
            "auth_enabled": settings.auth_enabled,
            "auth_mode": "disabled",
            "subject": None,
            "roles": [],
            "scopes": [],
        }
    return {
        "auth_enabled": settings.auth_enabled,
        "auth_mode": context.auth_mode,
        "subject": context.subject,
        "email": context.email,
        "roles": list(context.roles),
        "scopes": list(context.scopes),
    }
