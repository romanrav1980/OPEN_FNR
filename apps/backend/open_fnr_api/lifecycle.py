from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field, model_validator


router = APIRouter(prefix="/lifecycle", tags=["sku-lifecycle"])


class LifecycleStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    REPLACING = "replacing"
    PHASE_OUT = "phase_out"
    TERMINATED = "terminated"


class LifecycleEventType(StrEnum):
    PHASE_IN = "phase_in"
    PHASE_OUT = "phase_out"
    REPLACEMENT = "replacement"
    TERMINATION = "termination"


class ClearanceRisk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SkuLifecycle(BaseModel):
    sku_id: str
    status: LifecycleStatus
    launch_date: date | None = None
    termination_date: date | None = None
    reference_sku_id: str | None = None
    replacement_sku_id: str | None = None
    cold_start_forecast_qty: float = Field(ge=0)
    remaining_stock_qty: float = Field(ge=0)
    clearance_risk: ClearanceRisk
    owner_role: str
    updated_at: datetime

    @model_validator(mode="after")
    def validate_lifecycle_dates_and_links(self) -> "SkuLifecycle":
        if self.status == LifecycleStatus.PLANNED and self.launch_date is None:
            raise ValueError("planned SKU requires launch_date")
        if self.status in {LifecycleStatus.PHASE_OUT, LifecycleStatus.TERMINATED} and self.termination_date is None:
            raise ValueError("phase-out or terminated SKU requires termination_date")
        if self.status == LifecycleStatus.REPLACING and self.replacement_sku_id is None:
            raise ValueError("replacing SKU requires replacement_sku_id")
        return self


class LifecycleAuditEvent(BaseModel):
    event_id: str
    sku_id: str
    event_type: LifecycleEventType
    actor: str
    old_status: LifecycleStatus
    new_status: LifecycleStatus
    reason: str
    created_at: datetime


class LifecycleActionRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    reason: str = Field(min_length=1)


SKU_LIFECYCLES: tuple[SkuLifecycle, ...] = (
    SkuLifecycle(
        sku_id="SKU_NEW_001",
        status=LifecycleStatus.PLANNED,
        launch_date=date(2026, 6, 10),
        termination_date=None,
        reference_sku_id="SKU001",
        replacement_sku_id=None,
        cold_start_forecast_qty=12.4,
        remaining_stock_qty=0,
        clearance_risk=ClearanceRisk.LOW,
        owner_role="Category Manager",
        updated_at=datetime(2026, 5, 28, 8, 0, tzinfo=timezone.utc),
    ),
    SkuLifecycle(
        sku_id="SKU_OLD_001",
        status=LifecycleStatus.PHASE_OUT,
        launch_date=date(2024, 1, 15),
        termination_date=date(2026, 6, 5),
        reference_sku_id=None,
        replacement_sku_id="SKU_NEW_001",
        cold_start_forecast_qty=0,
        remaining_stock_qty=420,
        clearance_risk=ClearanceRisk.HIGH,
        owner_role="Category Manager",
        updated_at=datetime(2026, 5, 28, 8, 15, tzinfo=timezone.utc),
    ),
)

LIFECYCLE_AUDIT: tuple[LifecycleAuditEvent, ...] = (
    LifecycleAuditEvent(
        event_id="life-audit-20260528-001",
        sku_id="SKU_OLD_001",
        event_type=LifecycleEventType.PHASE_OUT,
        actor="category.manager@example.org",
        old_status=LifecycleStatus.ACTIVE,
        new_status=LifecycleStatus.PHASE_OUT,
        reason="Replacement SKU_NEW_001 approved.",
        created_at=datetime(2026, 5, 28, 8, 15, tzinfo=timezone.utc),
    ),
)


def order_allowed_on_date(lifecycle: SkuLifecycle, order_date: date) -> bool:
    if lifecycle.termination_date is None:
        return True
    return order_date <= lifecycle.termination_date


def calculate_cold_start_forecast(reference_forecast_qty: float, similarity_factor: float) -> float:
    return reference_forecast_qty * similarity_factor


def classify_clearance_risk(remaining_stock_qty: float, days_to_termination: int) -> ClearanceRisk:
    if days_to_termination <= 0 and remaining_stock_qty > 0:
        return ClearanceRisk.HIGH
    if days_to_termination <= 7 and remaining_stock_qty > 100:
        return ClearanceRisk.HIGH
    if days_to_termination <= 14 and remaining_stock_qty > 50:
        return ClearanceRisk.MEDIUM
    return ClearanceRisk.LOW


def transition_lifecycle(sku: SkuLifecycle, action: str, payload: LifecycleActionRequest) -> SkuLifecycle:
    if payload.actor_role != "Category Manager":
        raise HTTPException(status_code=403, detail="only Category Manager can change SKU lifecycle")
    status_by_action = {
        "activate": LifecycleStatus.ACTIVE,
        "phase_out": LifecycleStatus.PHASE_OUT,
        "terminate": LifecycleStatus.TERMINATED,
    }
    if action not in status_by_action:
        raise HTTPException(status_code=400, detail="unsupported lifecycle action")
    if sku.status == LifecycleStatus.TERMINATED:
        raise HTTPException(status_code=409, detail="terminated SKU cannot be changed")
    return sku.model_copy(update={"status": status_by_action[action], "updated_at": datetime(2026, 5, 28, 9, 0, tzinfo=timezone.utc)})


@router.get("/skus")
def list_sku_lifecycles() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in SKU_LIFECYCLES], "total": len(SKU_LIFECYCLES)}


@router.get("/skus/{sku_id}")
def get_sku_lifecycle(sku_id: str = Path(min_length=1)) -> dict[str, object]:
    sku = next((item for item in SKU_LIFECYCLES if item.sku_id == sku_id), None)
    if sku is None:
        raise HTTPException(status_code=404, detail="SKU lifecycle not found")
    return sku.model_dump(mode="json")


@router.get("/skus/{sku_id}/order-allowed")
def get_order_allowed(sku_id: str, order_date: date) -> dict[str, object]:
    sku = next((item for item in SKU_LIFECYCLES if item.sku_id == sku_id), None)
    if sku is None:
        raise HTTPException(status_code=404, detail="SKU lifecycle not found")
    return {"sku_id": sku_id, "order_date": order_date.isoformat(), "allowed": order_allowed_on_date(sku, order_date)}


@router.post("/skus/{sku_id}/{action}")
def act_on_sku_lifecycle(sku_id: str, action: str, payload: LifecycleActionRequest) -> dict[str, object]:
    sku = next((item for item in SKU_LIFECYCLES if item.sku_id == sku_id), None)
    if sku is None:
        raise HTTPException(status_code=404, detail="SKU lifecycle not found")
    updated = transition_lifecycle(sku, action, payload)
    audit = LifecycleAuditEvent(
        event_id=f"life-audit-{sku_id}-{action}",
        sku_id=sku_id,
        event_type=LifecycleEventType.TERMINATION if action == "terminate" else LifecycleEventType.PHASE_IN,
        actor=payload.actor,
        old_status=sku.status,
        new_status=updated.status,
        reason=payload.reason,
        created_at=datetime(2026, 5, 28, 9, 0, tzinfo=timezone.utc),
    )
    return {"sku": updated.model_dump(mode="json"), "audit_event": audit.model_dump(mode="json")}


@router.get("/skus/{sku_id}/audit")
def get_sku_lifecycle_audit(sku_id: str) -> dict[str, object]:
    events = tuple(event for event in LIFECYCLE_AUDIT if event.sku_id == sku_id)
    return {"items": [event.model_dump(mode="json") for event in events], "total": len(events)}
