from datetime import datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/security", tags=["security"])


class AccessRequestStatus(StrEnum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROVISIONED = "provisioned"
    REVOKED = "revoked"


class RoleName(StrEnum):
    ADMIN = "Admin"
    SECURITY_OWNER = "Security Owner"
    USER_MANAGER = "User Manager"
    SUPPLY_CHAIN_MANAGER = "Supply Chain Manager"
    VIEWER = "Viewer"


class UserPermission(BaseModel):
    user_id: str
    email: str
    roles: tuple[RoleName, ...]
    regions: tuple[str, ...]
    categories: tuple[str, ...]
    active: bool


class ServiceAccount(BaseModel):
    account_id: str
    purpose: str
    scopes: tuple[str, ...]
    owner_role: RoleName
    secret_rotation_days: int = Field(gt=0)


class AccessRequest(BaseModel):
    request_id: str
    user_id: str
    requested_role: RoleName
    requested_regions: tuple[str, ...]
    status: AccessRequestStatus
    requester: str
    approver_role: RoleName
    created_at: datetime
    updated_at: datetime


class AccessActionRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: RoleName
    reason: str = Field(min_length=1)


class SecurityAuditEvent(BaseModel):
    event_id: str
    object_id: str
    actor: str
    event_type: str
    message: str
    created_at: datetime


USERS: tuple[UserPermission, ...] = (
    UserPermission(
        user_id="u-admin-001",
        email="admin@example.org",
        roles=(RoleName.ADMIN,),
        regions=("all",),
        categories=("all",),
        active=True,
    ),
    UserPermission(
        user_id="u-viewer-001",
        email="viewer@example.org",
        roles=(RoleName.VIEWER,),
        regions=("north",),
        categories=("fresh",),
        active=True,
    ),
)

SERVICE_ACCOUNTS: tuple[ServiceAccount, ...] = (
    ServiceAccount(
        account_id="svc-airflow-export",
        purpose="Airflow export to DWH and ERP mocks",
        scopes=("forecast:read", "publication:write"),
        owner_role=RoleName.ADMIN,
        secret_rotation_days=90,
    ),
)

ACCESS_REQUESTS: tuple[AccessRequest, ...] = (
    AccessRequest(
        request_id="access-20260528-001",
        user_id="u-viewer-001",
        requested_role=RoleName.SUPPLY_CHAIN_MANAGER,
        requested_regions=("north",),
        status=AccessRequestStatus.REQUESTED,
        requester="viewer@example.org",
        approver_role=RoleName.SECURITY_OWNER,
        created_at=datetime(2026, 5, 28, 13, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 28, 13, 0, tzinfo=timezone.utc),
    ),
)


def has_role(user: UserPermission, role: RoleName) -> bool:
    return role in user.roles or RoleName.ADMIN in user.roles


def has_scope(user: UserPermission, region: str, category: str) -> bool:
    region_allowed = "all" in user.regions or region in user.regions
    category_allowed = "all" in user.categories or category in user.categories
    return user.active and region_allowed and category_allowed


def assert_admin(actor_role: RoleName) -> None:
    if actor_role != RoleName.ADMIN:
        raise HTTPException(status_code=403, detail="Admin role required")


def transition_access_request(access_request: AccessRequest, action: str, payload: AccessActionRequest) -> AccessRequest:
    if action in {"approve", "reject"} and payload.actor_role != RoleName.SECURITY_OWNER:
        raise HTTPException(status_code=403, detail="Security Owner role required")
    if action == "provision" and payload.actor_role != RoleName.USER_MANAGER:
        raise HTTPException(status_code=403, detail="User Manager role required")
    if action == "revoke" and payload.actor_role != RoleName.ADMIN:
        raise HTTPException(status_code=403, detail="Admin role required")
    status_by_action = {
        "approve": AccessRequestStatus.APPROVED,
        "reject": AccessRequestStatus.REJECTED,
        "provision": AccessRequestStatus.PROVISIONED,
        "revoke": AccessRequestStatus.REVOKED,
    }
    if action not in status_by_action:
        raise HTTPException(status_code=400, detail="unsupported access action")
    return access_request.model_copy(update={"status": status_by_action[action], "updated_at": datetime(2026, 5, 28, 13, 30, tzinfo=timezone.utc)})


@router.get("/users")
def list_users(actor_role: RoleName = RoleName.ADMIN) -> dict[str, object]:
    assert_admin(actor_role)
    return {"items": [item.model_dump(mode="json") for item in USERS], "total": len(USERS)}


@router.get("/service-accounts")
def list_service_accounts(actor_role: RoleName = RoleName.ADMIN) -> dict[str, object]:
    assert_admin(actor_role)
    return {"items": [item.model_dump(mode="json") for item in SERVICE_ACCOUNTS], "total": len(SERVICE_ACCOUNTS)}


@router.get("/access-requests")
def list_access_requests(actor_role: RoleName = RoleName.SECURITY_OWNER) -> dict[str, object]:
    if actor_role not in {RoleName.ADMIN, RoleName.SECURITY_OWNER, RoleName.USER_MANAGER}:
        raise HTTPException(status_code=403, detail="access request visibility denied")
    return {"items": [item.model_dump(mode="json") for item in ACCESS_REQUESTS], "total": len(ACCESS_REQUESTS)}


@router.post("/access-requests/{request_id}/{action}")
def act_on_access_request(request_id: str, action: str, payload: AccessActionRequest) -> dict[str, object]:
    access_request = next((item for item in ACCESS_REQUESTS if item.request_id == request_id), None)
    if access_request is None:
        raise HTTPException(status_code=404, detail="access request not found")
    updated = transition_access_request(access_request, action, payload)
    audit_event = SecurityAuditEvent(
        event_id=f"security-audit-{request_id}-{action}",
        object_id=request_id,
        actor=payload.actor,
        event_type=f"access_{action}",
        message=payload.reason,
        created_at=datetime(2026, 5, 28, 13, 30, tzinfo=timezone.utc),
    )
    return {"request": updated.model_dump(mode="json"), "audit_event": audit_event.model_dump(mode="json")}


@router.get("/access-check")
def check_access(user_id: str, region: str, category: str, role: RoleName) -> dict[str, object]:
    user = next((item for item in USERS if item.user_id == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    allowed = has_role(user, role) and has_scope(user, region, category)
    return {"user_id": user_id, "allowed": allowed, "region": region, "category": category, "role": role}
