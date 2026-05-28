from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .audit import AuditEventCreate, record_audit_event_if_enabled


router = APIRouter(prefix="/capacity", tags=["capacity"])


class CapacityStatus(StrEnum):
    OK = "ok"
    OVERLOAD = "overload"
    SMOOTHING_PROPOSED = "smoothing_proposed"
    APPROVED = "approved"
    WAIVED = "waived"


class CapacityCalendarDay(BaseModel):
    dc_id: str
    date: str
    inbound_capacity_qty: int = Field(gt=0)
    planned_inbound_qty: int = Field(ge=0)
    transport_capacity_pallets: int = Field(gt=0)
    planned_transport_pallets: int = Field(ge=0)
    store_receiving_hours: int = Field(gt=0)


class AffectedOrder(BaseModel):
    order_id: str
    supplier_id: str
    original_date: str
    proposed_date: str
    qty: int = Field(gt=0)
    priority: str


class CapacityPlan(BaseModel):
    plan_id: str
    status: CapacityStatus
    overloaded_date: str
    overload_qty: int = Field(ge=0)
    moved_qty: int = Field(ge=0)
    affected_orders: tuple[AffectedOrder, ...]
    recommendation: str


class CapacityActionRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    reason: str = Field(min_length=1)


CALENDAR = CapacityCalendarDay(
    dc_id="DC001",
    date="2026-06-02",
    inbound_capacity_qty=10_000,
    planned_inbound_qty=12_400,
    transport_capacity_pallets=220,
    planned_transport_pallets=260,
    store_receiving_hours=8,
)

AFFECTED_ORDERS: tuple[AffectedOrder, ...] = (
    AffectedOrder(order_id="po-001", supplier_id="SUP_FAST", original_date="2026-06-02", proposed_date="2026-06-03", qty=1400, priority="medium"),
    AffectedOrder(order_id="po-002", supplier_id="SUP_CHEAP", original_date="2026-06-02", proposed_date="2026-06-04", qty=1000, priority="low"),
)


def detect_capacity_overload(day: CapacityCalendarDay) -> int:
    return max(day.planned_inbound_qty - day.inbound_capacity_qty, 0)


def build_capacity_plan() -> CapacityPlan:
    overload = detect_capacity_overload(CALENDAR)
    moved = sum(order.qty for order in AFFECTED_ORDERS)
    return CapacityPlan(
        plan_id="capacity-plan-20260602-dc001",
        status=CapacityStatus.SMOOTHING_PROPOSED if overload else CapacityStatus.OK,
        overloaded_date=CALENDAR.date,
        overload_qty=overload,
        moved_qty=moved,
        affected_orders=AFFECTED_ORDERS,
        recommendation="Move medium and low priority orders to following receiving days.",
    )


@router.get("/plans")
def list_capacity_plans() -> dict[str, object]:
    plan = build_capacity_plan()
    return {"items": [plan.model_dump(mode="json")], "total": 1}


@router.post("/plans/{plan_id}/approve")
def approve_capacity_plan(plan_id: str, payload: CapacityActionRequest) -> dict[str, object]:
    plan = build_capacity_plan()
    if plan.plan_id != plan_id:
        raise HTTPException(status_code=404, detail="capacity plan not found")
    if payload.actor_role not in {"Supply Chain Manager", "Store Operations"}:
        raise HTTPException(status_code=403, detail="capacity approval role required")
    approved = plan.model_copy(update={"status": CapacityStatus.APPROVED})
    record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="capacity_plan_approved",
            actor=payload.actor,
            actor_role=payload.actor_role,
            object_type="capacity_plan",
            object_id=plan_id,
            action="approve",
            reason=payload.reason,
            correlation_id=f"{plan_id}:approval",
            payload={
                "overloaded_date": plan.overloaded_date,
                "overload_qty": plan.overload_qty,
                "moved_qty": plan.moved_qty,
                "affected_order_count": len(plan.affected_orders),
            },
        )
    )
    return {"plan": approved.model_dump(mode="json"), "audit_message": f"{payload.actor} approved order moves: {payload.reason}"}


@router.get("/tms-export")
def get_tms_capacity_export() -> dict[str, object]:
    plan = build_capacity_plan()
    return {
        "target": "TMS capacity mock",
        "plan_id": plan.plan_id,
        "moved_orders": [order.model_dump(mode="json") for order in plan.affected_orders],
        "idempotency_key": f"{plan.plan_id}:tms:v1",
    }
