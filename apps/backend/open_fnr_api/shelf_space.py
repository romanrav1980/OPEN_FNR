from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


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


PLANOGRAMS: tuple[ShelfPlanogram, ...] = (
    ShelfPlanogram(store_id="S001", sku_id="SKU001", zone="front", shelf_capacity_qty=80, display_capacity_qty=120, direct_to_shelf=True),
    ShelfPlanogram(store_id="S001", sku_id="SKU002", zone="fresh-wall", shelf_capacity_qty=60, display_capacity_qty=90, direct_to_shelf=False),
)


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
    planogram = next((item for item in PLANOGRAMS if item.store_id == store_id and item.sku_id == sku_id), None)
    if planogram is None:
        raise HTTPException(status_code=404, detail="planogram not found")
    validation = validate_display_capacity(planogram, requested_display_qty=140).model_copy(update={"status": ShelfStatus.APPROVED})
    return {"validation": validation.model_dump(mode="json"), "audit_message": f"{payload.actor} approved shelf/display exception: {payload.reason}"}
