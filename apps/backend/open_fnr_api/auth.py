from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass
from typing import Callable

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
    payload_segment = parts[1]
    padded = payload_segment + "=" * (-len(payload_segment) % 4)
    return json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))


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
