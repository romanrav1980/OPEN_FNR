import json
from enum import StrEnum
from urllib.error import URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .audit import AuditEventCreate, record_audit_event_if_enabled
from .config import settings


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


class TmsCapacityExportRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str = Field(default="Supply Chain Manager", min_length=1)
    service_account: str = Field(min_length=1)


class TmsCapacityExportPreview(BaseModel):
    target: str
    plan_id: str
    moved_orders: tuple[dict[str, object], ...]
    idempotency_key: str
    export_channel: str


class TmsCapacityExportResponse(BaseModel):
    export: TmsCapacityExportPreview
    response_code: str
    response_message: str
    audit_recorded: bool


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


def tms_capacity_export_channel() -> str:
    return "http_api" if settings.tms_capacity_export_url else "local_fallback"


def build_tms_capacity_export(plan: CapacityPlan) -> TmsCapacityExportPreview:
    return TmsCapacityExportPreview(
        target="TMS capacity",
        plan_id=plan.plan_id,
        moved_orders=tuple(order.model_dump(mode="json") for order in plan.affected_orders),
        idempotency_key=f"{plan.plan_id}:tms:v1",
        export_channel=tms_capacity_export_channel(),
    )


def send_tms_capacity_export_to_target(export: TmsCapacityExportPreview) -> tuple[str, str]:
    if not settings.tms_capacity_export_url:
        return "202", "sent to local TMS capacity fallback"
    request = Request(
        settings.tms_capacity_export_url,
        data=json.dumps(export.model_dump(mode="json"), ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Idempotency-Key": export.idempotency_key,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=settings.publication_http_timeout_seconds) as response:
            response_body = response.read().decode("utf-8", errors="replace").strip()
            return str(response.status), response_body or "sent to TMS capacity target"
    except URLError as exc:
        raise HTTPException(status_code=503, detail=f"TMS capacity target unavailable: {exc}") from exc


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
    return build_tms_capacity_export(plan).model_dump(mode="json")


@router.post("/tms-export/send", response_model=TmsCapacityExportResponse)
def send_tms_capacity_export(payload: TmsCapacityExportRequest) -> TmsCapacityExportResponse:
    if payload.actor_role not in {"Supply Chain Manager", "Store Operations"}:
        raise HTTPException(status_code=403, detail="capacity export role required")
    if payload.service_account != "svc-open-fnr-tms-export":
        raise HTTPException(status_code=403, detail="service account is not allowed to export capacity plan")
    plan = build_capacity_plan()
    export = build_tms_capacity_export(plan)
    response_code, response_message = send_tms_capacity_export_to_target(export)
    event = record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="tms_capacity_export_sent",
            actor=payload.actor,
            actor_role=payload.actor_role,
            object_type="capacity_plan",
            object_id=plan.plan_id,
            action="send",
            reason=f"Sent capacity plan through {export.export_channel}",
            correlation_id=export.idempotency_key,
            payload={
                "target": export.target,
                "moved_order_count": len(export.moved_orders),
                "export_channel": export.export_channel,
            },
        )
    )
    return TmsCapacityExportResponse(
        export=export,
        response_code=response_code,
        response_message=response_message,
        audit_recorded=event is not None,
    )
