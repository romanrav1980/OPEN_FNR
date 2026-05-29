from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException


@dataclass(frozen=True)
class Principal:
    subject: str
    roles: tuple[str, ...]
    regions: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    active: bool = True


def normalize_role(role: object) -> str:
    return str(getattr(role, "value", role))


def has_any_role(principal: Principal, allowed_roles: set[object], admin_role: object = "Admin") -> bool:
    principal_roles = {normalize_role(role) for role in principal.roles}
    allowed = {normalize_role(role) for role in allowed_roles}
    return normalize_role(admin_role) in principal_roles or bool(principal_roles & allowed)


def assert_any_role(principal: Principal, allowed_roles: set[object], detail: str) -> None:
    if not has_any_role(principal, allowed_roles):
        raise HTTPException(status_code=403, detail=detail)


def has_object_scope(principal: Principal, region: str, category: str) -> bool:
    if not principal.active:
        return False
    region_allowed = "all" in principal.regions or region in principal.regions
    category_allowed = "all" in principal.categories or category in principal.categories
    return region_allowed and category_allowed


def assert_object_scope(principal: Principal, region: str, category: str, detail: str) -> None:
    if not has_object_scope(principal, region, category):
        raise HTTPException(status_code=403, detail=detail)


def assert_service_account(actual: str, expected: str, detail: str) -> None:
    if actual != expected:
        raise HTTPException(status_code=403, detail=detail)
