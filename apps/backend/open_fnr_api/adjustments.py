from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, model_validator

from .audit import AuditEventCreate, record_audit_event_if_enabled
from .repositories import OperationalDecisionRecord, operational_decision_repository


router = APIRouter(prefix="/adjustments", tags=["manual-adjustments"])


class AdjustmentTargetType(StrEnum):
    FORECAST = "forecast"
    ORDER_PROPOSAL = "order_proposal"
    PROMO_FORECAST = "promo_forecast"


class AdjustmentMode(StrEnum):
    PERCENT = "percent"
    ABSOLUTE = "absolute"


class AdjustmentStatus(StrEnum):
    DRAFT = "draft"
    PREVIEWED = "previewed"
    APPROVED = "approved"
    APPLIED = "applied"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ReasonCode(StrEnum):
    LOCAL_EVENT = "local_event"
    SUPPLY_CONSTRAINT = "supply_constraint"
    PROMO_CORRECTION = "promo_correction"
    BUSINESS_OVERRIDE = "business_override"


class AdjustmentScope(BaseModel):
    store_ids: list[str] = Field(min_length=1)
    sku_ids: list[str] = Field(min_length=1)
    date_from: date
    date_to: date

    @model_validator(mode="after")
    def validate_dates(self) -> "AdjustmentScope":
        if self.date_to < self.date_from:
            raise ValueError("date_to must be greater than or equal to date_from")
        return self


class ManualAdjustment(BaseModel):
    adjustment_id: str
    target_type: AdjustmentTargetType
    target_id: str
    status: AdjustmentStatus
    mode: AdjustmentMode
    value: float
    reason_code: ReasonCode
    reason_comment: str = Field(min_length=1)
    scope: AdjustmentScope
    valid_from: date
    valid_to: date
    created_by: str
    created_at: datetime
    approved_by: str | None = None

    @model_validator(mode="after")
    def validate_validity_period(self) -> "ManualAdjustment":
        if self.valid_to < self.valid_from:
            raise ValueError("valid_to must be greater than or equal to valid_from")
        return self


class AdjustmentPreview(BaseModel):
    adjustment_id: str
    base_value: float
    adjusted_value: float
    delta_value: float
    affected_rows: int = Field(ge=0)
    approval_required: bool
    impact_summary: str


class AdjustmentActionRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    comment: str = Field(min_length=1)


class AdjustmentAuditEvent(BaseModel):
    event_id: str
    adjustment_id: str
    actor: str
    actor_role: str
    action: str
    old_status: AdjustmentStatus
    new_status: AdjustmentStatus
    old_value: float
    new_value: float
    comment: str
    created_at: datetime


ADJUSTMENTS: tuple[ManualAdjustment, ...] = (
    ManualAdjustment(
        adjustment_id="adj-forecast-20260528-001",
        target_type=AdjustmentTargetType.FORECAST,
        target_id="regular-baseline-20260528-001",
        status=AdjustmentStatus.PREVIEWED,
        mode=AdjustmentMode.PERCENT,
        value=10,
        reason_code=ReasonCode.LOCAL_EVENT,
        reason_comment="Local event expected to lift demand.",
        scope=AdjustmentScope(
            store_ids=["S001", "S002"],
            sku_ids=["SKU001", "SKU002"],
            date_from=date(2026, 6, 1),
            date_to=date(2026, 6, 7),
        ),
        valid_from=date(2026, 6, 1),
        valid_to=date(2026, 6, 7),
        created_by="forecast.planner@example.org",
        created_at=datetime(2026, 5, 28, 15, 0, tzinfo=timezone.utc),
    ),
    ManualAdjustment(
        adjustment_id="adj-order-20260528-001",
        target_type=AdjustmentTargetType.ORDER_PROPOSAL,
        target_id="order-proposal-20260528-s001-sku001",
        status=AdjustmentStatus.APPLIED,
        mode=AdjustmentMode.ABSOLUTE,
        value=300,
        reason_code=ReasonCode.SUPPLY_CONSTRAINT,
        reason_comment="Raise order to cover projected promo stock-out.",
        scope=AdjustmentScope(
            store_ids=["S001"],
            sku_ids=["SKU001"],
            date_from=date(2026, 5, 30),
            date_to=date(2026, 5, 30),
        ),
        valid_from=date(2026, 5, 30),
        valid_to=date(2026, 5, 30),
        created_by="replenishment.planner@example.org",
        created_at=datetime(2026, 5, 28, 6, 0, tzinfo=timezone.utc),
        approved_by="supply.manager@example.org",
    ),
)

ADJUSTMENT_AUDIT_EVENTS: tuple[AdjustmentAuditEvent, ...] = (
    AdjustmentAuditEvent(
        event_id="adj-audit-20260528-001",
        adjustment_id="adj-order-20260528-001",
        actor="replenishment.planner@example.org",
        actor_role="Replenishment Planner",
        action="apply",
        old_status=AdjustmentStatus.APPROVED,
        new_status=AdjustmentStatus.APPLIED,
        old_value=276,
        new_value=300,
        comment="Applied after approval.",
        created_at=datetime(2026, 5, 28, 6, 10, tzinfo=timezone.utc),
    ),
)


def preview_adjusted_value(base_value: float, mode: AdjustmentMode, value: float) -> float:
    if mode == AdjustmentMode.PERCENT:
        return base_value * (1 + value / 100)
    return value


def adjustment_approval_required(mode: AdjustmentMode, value: float, actor_role: str) -> bool:
    if actor_role == "Category Manager":
        return False
    if mode == AdjustmentMode.PERCENT and abs(value) > 5:
        return True
    if mode == AdjustmentMode.ABSOLUTE and value > 250:
        return True
    return False


def build_adjustment_preview(adjustment: ManualAdjustment, base_value: float) -> AdjustmentPreview:
    adjusted_value = preview_adjusted_value(base_value, adjustment.mode, adjustment.value)
    affected_rows = len(adjustment.scope.store_ids) * len(adjustment.scope.sku_ids)
    return AdjustmentPreview(
        adjustment_id=adjustment.adjustment_id,
        base_value=base_value,
        adjusted_value=adjusted_value,
        delta_value=adjusted_value - base_value,
        affected_rows=affected_rows,
        approval_required=adjustment_approval_required(adjustment.mode, adjustment.value, "Forecast Planner"),
        impact_summary=f"{affected_rows} store x SKU pairs adjusted from {base_value} to {adjusted_value:.2f}.",
    )


def transition_adjustment(adjustment: ManualAdjustment, action: str, payload: AdjustmentActionRequest) -> ManualAdjustment:
    allowed_roles = {"Forecast Planner", "Replenishment Planner", "Category Manager", "Admin"}
    if payload.actor_role not in allowed_roles:
        raise HTTPException(status_code=403, detail="actor role cannot manage adjustments")
    status_by_action = {
        "approve": AdjustmentStatus.APPROVED,
        "apply": AdjustmentStatus.APPLIED,
        "cancel": AdjustmentStatus.CANCELLED,
    }
    if action not in status_by_action:
        raise HTTPException(status_code=400, detail="unsupported adjustment action")
    if adjustment.status == AdjustmentStatus.APPLIED and action != "cancel":
        raise HTTPException(status_code=409, detail="applied adjustment cannot be changed")
    return adjustment.model_copy(update={"status": status_by_action[action]})


@router.get("")
def list_adjustments(target_type: AdjustmentTargetType | None = Query(default=None)) -> dict[str, object]:
    items = ADJUSTMENTS
    if target_type is not None:
        items = tuple(item for item in items if item.target_type == target_type)
    return {"items": [item.model_dump(mode="json") for item in items], "total": len(items)}


@router.get("/{adjustment_id}")
def get_adjustment(adjustment_id: str) -> dict[str, object]:
    for adjustment in ADJUSTMENTS:
        if adjustment.adjustment_id == adjustment_id:
            return adjustment.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="adjustment not found")


@router.get("/{adjustment_id}/preview")
def get_adjustment_preview(adjustment_id: str, base_value: float = Query(gt=0)) -> dict[str, object]:
    adjustment = next((item for item in ADJUSTMENTS if item.adjustment_id == adjustment_id), None)
    if adjustment is None:
        raise HTTPException(status_code=404, detail="adjustment not found")
    return build_adjustment_preview(adjustment, base_value).model_dump(mode="json")


@router.post("/{adjustment_id}/{action}")
def act_on_adjustment(adjustment_id: str, action: str, payload: AdjustmentActionRequest) -> dict[str, object]:
    adjustment = next((item for item in ADJUSTMENTS if item.adjustment_id == adjustment_id), None)
    if adjustment is None:
        raise HTTPException(status_code=404, detail="adjustment not found")
    updated = transition_adjustment(adjustment, action, payload)
    event = AdjustmentAuditEvent(
        event_id=f"adj-audit-{adjustment_id}-{action}",
        adjustment_id=adjustment_id,
        actor=payload.actor,
        actor_role=payload.actor_role,
        action=action,
        old_status=adjustment.status,
        new_status=updated.status,
        old_value=adjustment.value,
        new_value=adjustment.value,
        comment=payload.comment,
        created_at=datetime(2026, 5, 28, 15, 30, tzinfo=timezone.utc),
    )
    record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="manual_adjustment_action",
            actor=payload.actor,
            actor_role=payload.actor_role,
            object_type="manual_adjustment",
            object_id=adjustment_id,
            action=action,
            reason=payload.comment,
            correlation_id=event.event_id,
            payload={
                "old_status": adjustment.status,
                "new_status": updated.status,
                "target_type": adjustment.target_type,
                "target_id": adjustment.target_id,
            },
        )
    )
    operational_decision_repository.upsert_decision(
        OperationalDecisionRecord(
            decision_id=f"manual-adjustment-{adjustment_id}-{action}",
            decision_type="manual_adjustment_action",
            object_type="manual_adjustment",
            object_id=adjustment_id,
            status=updated.status.value,
            actor=payload.actor,
            actor_role=payload.actor_role,
            idempotency_key=f"{adjustment_id}:{action}:{payload.actor}",
            correlation_id=event.event_id,
            payload={
                "old_status": adjustment.status.value,
                "new_status": updated.status.value,
                "target_type": adjustment.target_type.value,
                "target_id": adjustment.target_id,
                "comment": payload.comment,
            },
            created_at=event.created_at,
            updated_at=event.created_at,
        )
    )
    return {"adjustment": updated.model_dump(mode="json"), "audit_event": event.model_dump(mode="json")}


@router.get("/{adjustment_id}/audit")
def get_adjustment_audit(adjustment_id: str) -> dict[str, object]:
    events = tuple(event for event in ADJUSTMENT_AUDIT_EVENTS if event.adjustment_id == adjustment_id)
    return {"items": [event.model_dump(mode="json") for event in events], "total": len(events)}
