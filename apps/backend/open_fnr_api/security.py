import json
from datetime import datetime, timezone
from enum import StrEnum
from urllib.error import URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .audit import AuditEventCreate, record_audit_event_if_enabled
from .config import settings
from .policy import Principal, assert_any_role, assert_object_scope, assert_service_account, has_any_role, has_object_scope


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
    suppliers: tuple[str, ...] = ()
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


class IdpProvisionRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: RoleName = RoleName.USER_MANAGER
    service_account: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class SecurityAuditEvent(BaseModel):
    event_id: str
    object_id: str
    actor: str
    event_type: str
    message: str
    created_at: datetime


class AccessReviewItem(BaseModel):
    user_id: str
    email: str
    roles: tuple[RoleName, ...]
    regions: tuple[str, ...]
    categories: tuple[str, ...]
    suppliers: tuple[str, ...]
    status: str
    recommendation: str
    evidence: tuple[str, ...]


class AccessReviewReport(BaseModel):
    review_id: str
    business_date: str
    status: str
    reviewer_role: RoleName
    total_users: int = Field(ge=0)
    excessive_access_count: int = Field(ge=0)
    inactive_access_count: int = Field(ge=0)
    items: tuple[AccessReviewItem, ...]
    process_key: str = "access_review_process"


class IdpProvisionPreview(BaseModel):
    target: str
    request_id: str
    user_id: str
    requested_role: RoleName
    requested_regions: tuple[str, ...]
    idempotency_key: str
    export_channel: str


class IdpProvisionResponse(BaseModel):
    provision: IdpProvisionPreview
    response_code: str
    response_message: str
    audit_recorded: bool


USERS: tuple[UserPermission, ...] = (
    UserPermission(
        user_id="u-admin-001",
        email="admin@example.org",
        roles=(RoleName.ADMIN,),
        regions=("all",),
        categories=("all",),
        suppliers=("all",),
        active=True,
    ),
    UserPermission(
        user_id="u-viewer-001",
        email="viewer@example.org",
        roles=(RoleName.VIEWER,),
        regions=("north",),
        categories=("fresh",),
        suppliers=("SUP001",),
        active=True,
    ),
)

SERVICE_ACCOUNTS: tuple[ServiceAccount, ...] = (
    ServiceAccount(
        account_id="svc-airflow-export",
        purpose="Airflow export to DWH and ERP configured targets",
        scopes=("forecast:read", "publication:write"),
        owner_role=RoleName.ADMIN,
        secret_rotation_days=90,
    ),
    ServiceAccount(
        account_id="svc-open-fnr-idp-provisioning",
        purpose="Provision approved access requests in configured IdP or IAM target",
        scopes=("security:provision", "users:write"),
        owner_role=RoleName.ADMIN,
        secret_rotation_days=60,
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
    return has_any_role(user_principal(user), {role})


def has_scope(user: UserPermission, region: str, category: str, supplier_id: str | None = None) -> bool:
    return has_object_scope(user_principal(user), region, category, supplier_id)


def user_principal(user: UserPermission) -> Principal:
    return Principal(
        subject=user.user_id,
        roles=tuple(role.value for role in user.roles),
        regions=user.regions,
        categories=user.categories,
        suppliers=user.suppliers,
        active=user.active,
    )


def role_principal(actor_role: RoleName, actor: str = "api-request") -> Principal:
    return Principal(subject=actor, roles=(actor_role.value,), regions=("all",), categories=("all",), suppliers=("all",), active=True)


def assert_admin(actor_role: RoleName) -> None:
    assert_any_role(role_principal(actor_role), {RoleName.ADMIN}, "Admin role required")


def transition_access_request(access_request: AccessRequest, action: str, payload: AccessActionRequest) -> AccessRequest:
    if action in {"approve", "reject"}:
        assert_any_role(role_principal(payload.actor_role, payload.actor), {RoleName.SECURITY_OWNER}, "Security Owner role required")
    if action == "provision":
        assert_any_role(role_principal(payload.actor_role, payload.actor), {RoleName.USER_MANAGER}, "User Manager role required")
    if action == "revoke":
        assert_any_role(role_principal(payload.actor_role, payload.actor), {RoleName.ADMIN}, "Admin role required")
    status_by_action = {
        "approve": AccessRequestStatus.APPROVED,
        "reject": AccessRequestStatus.REJECTED,
        "provision": AccessRequestStatus.PROVISIONED,
        "revoke": AccessRequestStatus.REVOKED,
    }
    if action not in status_by_action:
        raise HTTPException(status_code=400, detail="unsupported access action")
    return access_request.model_copy(update={"status": status_by_action[action], "updated_at": datetime(2026, 5, 28, 13, 30, tzinfo=timezone.utc)})


def find_access_request(request_id: str) -> AccessRequest:
    access_request = next((item for item in ACCESS_REQUESTS if item.request_id == request_id), None)
    if access_request is None:
        raise HTTPException(status_code=404, detail="access request not found")
    return access_request


def idp_provisioning_channel() -> str:
    return "http_api" if settings.idp_provisioning_url else "local_fallback"


def build_idp_provision(access_request: AccessRequest) -> IdpProvisionPreview:
    return IdpProvisionPreview(
        target="IdP provisioning",
        request_id=access_request.request_id,
        user_id=access_request.user_id,
        requested_role=access_request.requested_role,
        requested_regions=access_request.requested_regions,
        idempotency_key=f"{access_request.request_id}:idp:v1",
        export_channel=idp_provisioning_channel(),
    )


def build_access_review_report(business_date: str, reviewer_role: RoleName) -> AccessReviewReport:
    assert_any_role(role_principal(reviewer_role), {RoleName.ADMIN, RoleName.SECURITY_OWNER}, "access review requires Security Owner or Admin role")
    items: list[AccessReviewItem] = []
    for user in USERS:
        evidence = [
            f"roles={','.join(role.value for role in user.roles)}",
            f"regions={','.join(user.regions)}",
            f"categories={','.join(user.categories)}",
            f"suppliers={','.join(user.suppliers)}",
        ]
        excessive = RoleName.ADMIN in user.roles and "all" in user.regions and "all" in user.categories
        status = "review_required" if excessive else "ok"
        recommendation = "confirm_admin_need_or_reduce_scope" if excessive else "keep_current_access"
        items.append(
            AccessReviewItem(
                user_id=user.user_id,
                email=user.email,
                roles=user.roles,
                regions=user.regions,
                categories=user.categories,
                suppliers=user.suppliers,
                status=status,
                recommendation=recommendation,
                evidence=tuple(evidence),
            )
        )
    excessive_count = sum(1 for item in items if item.status == "review_required")
    inactive_count = sum(1 for user in USERS if not user.active)
    return AccessReviewReport(
        review_id=f"access-review-{business_date}",
        business_date=business_date,
        status="action_required" if excessive_count or inactive_count else "passed",
        reviewer_role=reviewer_role,
        total_users=len(items),
        excessive_access_count=excessive_count,
        inactive_access_count=inactive_count,
        items=tuple(items),
    )


def send_idp_provision_to_target(provision: IdpProvisionPreview) -> tuple[str, str]:
    if not settings.idp_provisioning_url:
        return "202", "sent to local IdP fallback"
    request = Request(
        settings.idp_provisioning_url,
        data=json.dumps(provision.model_dump(mode="json"), ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Idempotency-Key": provision.idempotency_key,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=settings.publication_http_timeout_seconds) as response:
            response_body = response.read().decode("utf-8", errors="replace").strip()
            return str(response.status), response_body or "sent to IdP provisioning target"
    except URLError as exc:
        raise HTTPException(status_code=503, detail=f"IdP provisioning target unavailable: {exc}") from exc


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
    assert_any_role(
        role_principal(actor_role),
        {RoleName.ADMIN, RoleName.SECURITY_OWNER, RoleName.USER_MANAGER},
        "access request visibility denied",
    )
    return {"items": [item.model_dump(mode="json") for item in ACCESS_REQUESTS], "total": len(ACCESS_REQUESTS)}


@router.get("/access-review/report", response_model=AccessReviewReport)
def get_access_review_report(business_date: str, reviewer_role: RoleName = RoleName.SECURITY_OWNER) -> AccessReviewReport:
    return build_access_review_report(business_date, reviewer_role)


@router.post("/access-requests/{request_id}/{action}")
def act_on_access_request(request_id: str, action: str, payload: AccessActionRequest) -> dict[str, object]:
    access_request = find_access_request(request_id)
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


@router.get("/access-requests/{request_id}/idp-provision")
def get_idp_provision(request_id: str) -> dict[str, object]:
    access_request = find_access_request(request_id)
    return build_idp_provision(access_request).model_dump(mode="json")


@router.post("/access-requests/{request_id}/idp-provision/send", response_model=IdpProvisionResponse)
def send_idp_provision(request_id: str, request: IdpProvisionRequest) -> IdpProvisionResponse:
    assert_any_role(role_principal(request.actor_role, request.actor), {RoleName.USER_MANAGER}, "User Manager role required")
    assert_service_account(
        request.service_account,
        "svc-open-fnr-idp-provisioning",
        "service account is not allowed to provision IdP access",
    )
    access_request = find_access_request(request_id)
    provision = build_idp_provision(access_request)
    response_code, response_message = send_idp_provision_to_target(provision)
    event = record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="idp_provision_sent",
            actor=request.actor,
            actor_role=request.actor_role,
            object_type="access_request",
            object_id=request_id,
            action="provision",
            reason=request.reason,
            correlation_id=provision.idempotency_key,
            payload={
                "user_id": provision.user_id,
                "requested_role": provision.requested_role,
                "requested_regions": provision.requested_regions,
                "export_channel": provision.export_channel,
            },
        )
    )
    return IdpProvisionResponse(
        provision=provision,
        response_code=response_code,
        response_message=response_message,
        audit_recorded=event is not None,
    )


@router.get("/access-check")
def check_access(user_id: str, region: str, category: str, role: RoleName, supplier_id: str | None = None) -> dict[str, object]:
    user = next((item for item in USERS if item.user_id == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    principal = user_principal(user)
    allowed = has_any_role(principal, {role}) and has_object_scope(principal, region, category, supplier_id)
    return {
        "user_id": user_id,
        "allowed": allowed,
        "region": region,
        "category": category,
        "supplier_id": supplier_id,
        "role": role,
    }


@router.get("/policy-check")
def check_policy(user_id: str, region: str, category: str, allowed_role: RoleName) -> dict[str, object]:
    user = next((item for item in USERS if item.user_id == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    principal = user_principal(user)
    assert_any_role(principal, {allowed_role}, "role policy denied")
    assert_object_scope(principal, region, category, "object scope policy denied")
    return {
        "user_id": user_id,
        "allowed": True,
        "role": allowed_role,
        "region": region,
        "category": category,
        "policy": "shared_policy_v1",
    }


@router.get("/object-access-check")
def check_object_access(
    user_id: str,
    region: str,
    category: str,
    object_type: str,
    object_id: str,
    allowed_role: RoleName,
    supplier_id: str | None = None,
) -> dict[str, object]:
    user = next((item for item in USERS if item.user_id == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    principal = user_principal(user)
    assert_any_role(principal, {allowed_role}, "role policy denied")
    assert_object_scope(principal, region, category, "object scope policy denied", supplier_id=supplier_id)
    return {
        "user_id": user_id,
        "allowed": True,
        "object_type": object_type,
        "object_id": object_id,
        "region": region,
        "category": category,
        "supplier_id": supplier_id,
        "policy": "shared_policy_v2_supplier_scope",
    }
