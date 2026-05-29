import json
from enum import StrEnum
from urllib.error import URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .audit import AuditEventCreate, record_audit_event_if_enabled
from .config import settings


router = APIRouter(prefix="/shelf-space", tags=["shelf-space"])


class ShelfStatus(StrEnum):
    VALID = "valid"
    CAPACITY_WARNING = "capacity_warning"
    REVIEW_REQUIRED = "review_required"
    APPROVED = "approved"


class ShelfPlanogram(BaseModel):
    store_id: str
    sku_id: str
    zone: str
    shelf_capacity_qty: int = Field(ge=0)
    display_capacity_qty: int = Field(ge=0)
    direct_to_shelf: bool


class ShelfValidation(BaseModel):
    store_id: str
    sku_id: str
    requested_display_qty: int = Field(ge=0)
    display_capacity_qty: int = Field(ge=0)
    status: ShelfStatus
    direct_to_shelf_recommended: bool
    warning: str | None


class ShelfActionRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    reason: str = Field(min_length=1)


class PlanogramExportRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str = Field(default="Category Manager", min_length=1)
    service_account: str = Field(min_length=1)


class PlanogramExportPreview(BaseModel):
    target: str
    store_id: str
    sku_id: str
    zone: str
    shelf_capacity_qty: int
    display_capacity_qty: int
    requested_display_qty: int
    status: ShelfStatus
    direct_to_shelf_recommended: bool
    idempotency_key: str
    export_channel: str


class PlanogramExportResponse(BaseModel):
    export: PlanogramExportPreview
    response_code: str
    response_message: str
    audit_recorded: bool


PLANOGRAMS: tuple[ShelfPlanogram, ...] = (
    ShelfPlanogram(store_id="S001", sku_id="SKU001", zone="front", shelf_capacity_qty=80, display_capacity_qty=120, direct_to_shelf=True),
    ShelfPlanogram(store_id="S001", sku_id="SKU002", zone="fresh-wall", shelf_capacity_qty=60, display_capacity_qty=90, direct_to_shelf=False),
)


def find_planogram(store_id: str, sku_id: str) -> ShelfPlanogram:
    planogram = next((item for item in PLANOGRAMS if item.store_id == store_id and item.sku_id == sku_id), None)
    if planogram is None:
        raise HTTPException(status_code=404, detail="planogram not found")
    return planogram


def validate_display_capacity(planogram: ShelfPlanogram, requested_display_qty: int) -> ShelfValidation:
    warning = None
    status = ShelfStatus.VALID
    if requested_display_qty > planogram.display_capacity_qty:
        status = ShelfStatus.CAPACITY_WARNING
        warning = "requested display stock exceeds display capacity"
    return ShelfValidation(
        store_id=planogram.store_id,
        sku_id=planogram.sku_id,
        requested_display_qty=requested_display_qty,
        display_capacity_qty=planogram.display_capacity_qty,
        status=status,
        direct_to_shelf_recommended=planogram.direct_to_shelf and requested_display_qty <= planogram.shelf_capacity_qty,
        warning=warning,
    )


def planogram_export_channel() -> str:
    return "http_api" if settings.planogram_export_url else "local_fallback"


def build_planogram_export(planogram: ShelfPlanogram, requested_display_qty: int = 140) -> PlanogramExportPreview:
    validation = validate_display_capacity(planogram, requested_display_qty=requested_display_qty)
    return PlanogramExportPreview(
        target="Planogram system",
        store_id=planogram.store_id,
        sku_id=planogram.sku_id,
        zone=planogram.zone,
        shelf_capacity_qty=planogram.shelf_capacity_qty,
        display_capacity_qty=planogram.display_capacity_qty,
        requested_display_qty=requested_display_qty,
        status=validation.status,
        direct_to_shelf_recommended=validation.direct_to_shelf_recommended,
        idempotency_key=f"{planogram.store_id}:{planogram.sku_id}:planogram:v1",
        export_channel=planogram_export_channel(),
    )


def send_planogram_export_to_target(export: PlanogramExportPreview) -> tuple[str, str]:
    if not settings.planogram_export_url:
        return "202", "sent to local planogram fallback"
    request = Request(
        settings.planogram_export_url,
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
            return str(response.status), response_body or "sent to planogram target"
    except URLError as exc:
        raise HTTPException(status_code=503, detail=f"planogram target unavailable: {exc}") from exc


@router.get("/planograms")
def list_planograms(zone: str | None = None) -> dict[str, object]:
    items = [item for item in PLANOGRAMS if zone is None or item.zone == zone]
    return {"items": [item.model_dump(mode="json") for item in items], "total": len(items)}


@router.get("/validations")
def list_shelf_validations() -> dict[str, object]:
    validations = (
        validate_display_capacity(PLANOGRAMS[0], requested_display_qty=140),
        validate_display_capacity(PLANOGRAMS[1], requested_display_qty=50),
    )
    return {"items": [item.model_dump(mode="json") for item in validations], "total": len(validations)}


@router.post("/validations/{store_id}/{sku_id}/approve")
def approve_shelf_exception(store_id: str, sku_id: str, payload: ShelfActionRequest) -> dict[str, object]:
    if payload.actor_role not in {"Category Manager", "Store Operations"}:
        raise HTTPException(status_code=403, detail="Category Manager or Store Operations role required")
    planogram = find_planogram(store_id, sku_id)
    validation = validate_display_capacity(planogram, requested_display_qty=140).model_copy(update={"status": ShelfStatus.APPROVED})
    return {"validation": validation.model_dump(mode="json"), "audit_message": f"{payload.actor} approved shelf/display exception: {payload.reason}"}


@router.get("/planogram-export/{store_id}/{sku_id}")
def get_planogram_export(store_id: str, sku_id: str) -> dict[str, object]:
    planogram = find_planogram(store_id, sku_id)
    return build_planogram_export(planogram).model_dump(mode="json")


@router.post("/planogram-export/{store_id}/{sku_id}/send", response_model=PlanogramExportResponse)
def send_planogram_export(store_id: str, sku_id: str, payload: PlanogramExportRequest) -> PlanogramExportResponse:
    if payload.actor_role not in {"Category Manager", "Store Operations"}:
        raise HTTPException(status_code=403, detail="Category Manager or Store Operations role required")
    if payload.service_account != "svc-open-fnr-planogram-export":
        raise HTTPException(status_code=403, detail="service account is not allowed to export planogram decision")
    planogram = find_planogram(store_id, sku_id)
    export = build_planogram_export(planogram)
    response_code, response_message = send_planogram_export_to_target(export)
    event = record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="planogram_export_sent",
            actor=payload.actor,
            actor_role=payload.actor_role,
            object_type="planogram",
            object_id=f"{store_id}:{sku_id}",
            action="send",
            reason=f"Sent planogram decision through {export.export_channel}",
            correlation_id=export.idempotency_key,
            payload={
                "store_id": export.store_id,
                "sku_id": export.sku_id,
                "zone": export.zone,
                "status": export.status,
                "export_channel": export.export_channel,
            },
        )
    )
    return PlanogramExportResponse(
        export=export,
        response_code=response_code,
        response_message=response_message,
        audit_recorded=event is not None,
    )
