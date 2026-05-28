from datetime import datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field


router = APIRouter(prefix="/exceptions", tags=["exception-center"])


class ExceptionType(StrEnum):
    STOCK_OUT_RISK = "stock_out_risk"
    OVERSTOCK_RISK = "overstock_risk"
    PROMO_SHORTAGE_RISK = "promo_shortage_risk"
    SUPPLIER_CONSTRAINT = "supplier_constraint"
    DATA_QUALITY = "data_quality"
    FORECAST_ANOMALY = "forecast_anomaly"
    EXPORT_FAILURE = "export_failure"


class ExceptionSeverity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ExceptionStatus(StrEnum):
    NEW = "new"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    IGNORED = "ignored"
    ESCALATED = "escalated"
    AUTO_RESOLVED = "auto_resolved"


class LinkedObject(BaseModel):
    object_type: str
    object_id: str
    label: str


class ExceptionItem(BaseModel):
    exception_id: str
    exception_type: ExceptionType
    severity: ExceptionSeverity
    status: ExceptionStatus
    owner_role: str
    owner_user: str | None
    title: str
    description: str
    recommended_action: str
    linked_objects: list[LinkedObject]
    sla_due_at: datetime
    created_at: datetime


class ExceptionActionRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    action: str
    reason: str = Field(min_length=1)
    comment: str = Field(min_length=1)


class ExceptionAuditEvent(BaseModel):
    event_id: str
    exception_id: str
    actor: str
    actor_role: str
    action: str
    reason: str
    comment: str
    created_at: datetime


class ExceptionActionResponse(BaseModel):
    exception: ExceptionItem
    audit_event: ExceptionAuditEvent


EXCEPTIONS: tuple[ExceptionItem, ...] = (
    ExceptionItem(
        exception_id="exc-stockout-20260528-001",
        exception_type=ExceptionType.STOCK_OUT_RISK,
        severity=ExceptionSeverity.HIGH,
        status=ExceptionStatus.NEW,
        owner_role="Replenishment Planner",
        owner_user=None,
        title="Projected stock-out on promo start",
        description="Store S001 SKU001 projected stock is -33 on 2026-06-01.",
        recommended_action="Review final order and raise quantity before cutoff.",
        linked_objects=[
            LinkedObject(object_type="inventory_projection", object_id="projection-20260528-s001-sku001", label="Projection S001 SKU001"),
            LinkedObject(object_type="order_proposal", object_id="order-proposal-20260528-s001-sku001", label="Order proposal S001 SKU001"),
        ],
        sla_due_at=datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc),
        created_at=datetime(2026, 5, 28, 13, 45, tzinfo=timezone.utc),
    ),
    ExceptionItem(
        exception_id="exc-promo-shortage-20260528-001",
        exception_type=ExceptionType.PROMO_SHORTAGE_RISK,
        severity=ExceptionSeverity.CRITICAL,
        status=ExceptionStatus.ESCALATED,
        owner_role="Supply Chain Manager",
        owner_user="supply.manager@example.org",
        title="Promo supply shortage risk",
        description="Promo forecast uplift exceeds confirmed receipt capacity.",
        recommended_action="Escalate to supply manager and approve mitigation plan.",
        linked_objects=[
            LinkedObject(object_type="promo", object_id="promo-20260601-fresh-001", label="Fresh promo"),
            LinkedObject(object_type="promo_forecast", object_id="promo-20260601-fresh-001", label="Promo uplift forecast"),
        ],
        sla_due_at=datetime(2026, 5, 28, 16, 0, tzinfo=timezone.utc),
        created_at=datetime(2026, 5, 28, 12, 25, tzinfo=timezone.utc),
    ),
    ExceptionItem(
        exception_id="exc-supplier-20260528-001",
        exception_type=ExceptionType.SUPPLIER_CONSTRAINT,
        severity=ExceptionSeverity.MEDIUM,
        status=ExceptionStatus.IN_REVIEW,
        owner_role="Replenishment Planner",
        owner_user="replenishment.planner@example.org",
        title="Supplier calendar closed",
        description="Supplier SUP002 calendar is closed for expected delivery date.",
        recommended_action="Find alternative supplier or postpone order.",
        linked_objects=[
            LinkedObject(object_type="order_proposal", object_id="order-proposal-20260528-s001-sku003", label="Blocked order proposal"),
        ],
        sla_due_at=datetime(2026, 5, 29, 10, 0, tzinfo=timezone.utc),
        created_at=datetime(2026, 5, 28, 5, 10, tzinfo=timezone.utc),
    ),
    ExceptionItem(
        exception_id="exc-dq-20260528-001",
        exception_type=ExceptionType.DATA_QUALITY,
        severity=ExceptionSeverity.HIGH,
        status=ExceptionStatus.NEW,
        owner_role="Data Owner",
        owner_user=None,
        title="Missing store_id in sales rows",
        description="128 inbound sales rows failed referential integrity.",
        recommended_action="Fix source file or approve audited waiver.",
        linked_objects=[
            LinkedObject(object_type="dq_incident", object_id="dq-20260528-sales-001", label="Sales DQ incident"),
        ],
        sla_due_at=datetime(2026, 5, 28, 10, 0, tzinfo=timezone.utc),
        created_at=datetime(2026, 5, 28, 3, 20, tzinfo=timezone.utc),
    ),
)

EXCEPTION_AUDIT_EVENTS: tuple[ExceptionAuditEvent, ...] = (
    ExceptionAuditEvent(
        event_id="exception-audit-20260528-001",
        exception_id="exc-supplier-20260528-001",
        actor="replenishment.planner@example.org",
        actor_role="Replenishment Planner",
        action="take",
        reason="supplier calendar issue",
        comment="Checking alternative delivery calendar.",
        created_at=datetime(2026, 5, 28, 5, 20, tzinfo=timezone.utc),
    ),
)


def route_exception_owner(exception_type: ExceptionType) -> str:
    if exception_type in {ExceptionType.STOCK_OUT_RISK, ExceptionType.OVERSTOCK_RISK, ExceptionType.SUPPLIER_CONSTRAINT}:
        return "Replenishment Planner"
    if exception_type == ExceptionType.PROMO_SHORTAGE_RISK:
        return "Supply Chain Manager"
    if exception_type == ExceptionType.DATA_QUALITY:
        return "Data Owner"
    if exception_type == ExceptionType.FORECAST_ANOMALY:
        return "Forecast Planner"
    return "Integration Owner"


def decide_exception_severity(exception_type: ExceptionType, impact_qty: float) -> ExceptionSeverity:
    if exception_type == ExceptionType.PROMO_SHORTAGE_RISK or impact_qty >= 1000:
        return ExceptionSeverity.CRITICAL
    if impact_qty >= 100:
        return ExceptionSeverity.HIGH
    if impact_qty >= 10:
        return ExceptionSeverity.MEDIUM
    return ExceptionSeverity.LOW


def apply_exception_action(item: ExceptionItem, payload: ExceptionActionRequest) -> ExceptionItem:
    allowed_roles = {item.owner_role, "Admin"}
    if payload.actor_role not in allowed_roles:
        raise HTTPException(status_code=403, detail="actor role is not allowed for exception")
    status_by_action = {
        "take": ExceptionStatus.IN_REVIEW,
        "resolve": ExceptionStatus.RESOLVED,
        "ignore": ExceptionStatus.IGNORED,
        "escalate": ExceptionStatus.ESCALATED,
    }
    if payload.action not in status_by_action:
        raise HTTPException(status_code=400, detail="unsupported exception action")
    return item.model_copy(update={"status": status_by_action[payload.action], "owner_user": payload.actor})


@router.get("")
def list_exceptions(
    exception_type: ExceptionType | None = Query(default=None),
    severity: ExceptionSeverity | None = Query(default=None),
    owner_role: str | None = Query(default=None),
) -> dict[str, object]:
    items = EXCEPTIONS
    if exception_type is not None:
        items = tuple(item for item in items if item.exception_type == exception_type)
    if severity is not None:
        items = tuple(item for item in items if item.severity == severity)
    if owner_role is not None:
        items = tuple(item for item in items if item.owner_role == owner_role)
    return {"items": [item.model_dump(mode="json") for item in items], "total": len(items)}


@router.get("/{exception_id}")
def get_exception(exception_id: str) -> dict[str, object]:
    for item in EXCEPTIONS:
        if item.exception_id == exception_id:
            return item.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="exception not found")


@router.post("/{exception_id}/actions")
def act_on_exception(exception_id: str, payload: ExceptionActionRequest) -> dict[str, object]:
    item = next((exception for exception in EXCEPTIONS if exception.exception_id == exception_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="exception not found")
    updated = apply_exception_action(item, payload)
    event = ExceptionAuditEvent(
        event_id=f"exception-audit-{exception_id}-{payload.action}",
        exception_id=exception_id,
        actor=payload.actor,
        actor_role=payload.actor_role,
        action=payload.action,
        reason=payload.reason,
        comment=payload.comment,
        created_at=datetime(2026, 5, 28, 14, 0, tzinfo=timezone.utc),
    )
    return ExceptionActionResponse(exception=updated, audit_event=event).model_dump(mode="json")


@router.get("/{exception_id}/audit")
def get_exception_audit(exception_id: str) -> dict[str, object]:
    events = tuple(event for event in EXCEPTION_AUDIT_EVENTS if event.exception_id == exception_id)
    return {"items": [event.model_dump(mode="json") for event in events], "total": len(events)}
