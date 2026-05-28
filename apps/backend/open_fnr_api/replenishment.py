from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field, model_validator


router = APIRouter(prefix="/replenishment", tags=["replenishment"])


class ProjectionStatus(StrEnum):
    QUEUED = "queued"
    PROJECTED = "projected"
    PROJECTION_WARNING = "projection_warning"
    FAILED = "failed"


class StockOutRisk(StrEnum):
    NONE = "none"
    WARNING = "warning"
    STOCK_OUT = "stock_out"


class StockSnapshot(BaseModel):
    snapshot_id: str
    store_id: str
    sku_id: str
    on_hand_qty: float = Field(ge=0)
    reserved_qty: float = Field(ge=0)
    available_qty: float = Field(ge=0)
    snapshot_at: datetime

    @model_validator(mode="after")
    def validate_available_qty(self) -> "StockSnapshot":
        expected_available = self.on_hand_qty - self.reserved_qty
        if abs(self.available_qty - expected_available) > 0.001:
            raise ValueError("available_qty must equal on_hand_qty minus reserved_qty")
        return self


class OpenOrder(BaseModel):
    order_id: str
    store_id: str
    sku_id: str
    expected_delivery_date: date
    qty: float = Field(gt=0)
    source: str


class ReplenishmentPolicy(BaseModel):
    store_id: str
    sku_id: str
    lead_time_days: int = Field(ge=0)
    safety_stock_qty: float = Field(ge=0)
    presentation_stock_qty: float = Field(ge=0)
    min_order_qty: float = Field(gt=0)
    order_multiple: float = Field(gt=0)


class InventoryProjectionDay(BaseModel):
    projection_date: date
    opening_stock_qty: float = Field(ge=0)
    demand_projection_qty: float = Field(ge=0)
    open_order_receipt_qty: float = Field(ge=0)
    in_transit_receipt_qty: float = Field(ge=0)
    projected_stock_qty: float
    safety_stock_qty: float = Field(ge=0)
    stock_out_risk: StockOutRisk


class InventoryProjection(BaseModel):
    projection_id: str
    store_id: str
    sku_id: str
    status: ProjectionStatus
    forecast_version: str
    stock_snapshot_id: str
    calculated_at: datetime
    lead_time_days: int = Field(ge=0)
    days: list[InventoryProjectionDay]


def calculate_projected_stock(
    opening_stock_qty: float,
    demand_projection_qty: float,
    open_order_receipt_qty: float,
    in_transit_receipt_qty: float,
) -> float:
    return opening_stock_qty + open_order_receipt_qty + in_transit_receipt_qty - demand_projection_qty


def classify_stock_out_risk(projected_stock_qty: float, safety_stock_qty: float) -> StockOutRisk:
    if projected_stock_qty <= 0:
        return StockOutRisk.STOCK_OUT
    if projected_stock_qty < safety_stock_qty:
        return StockOutRisk.WARNING
    return StockOutRisk.NONE


STOCK_SNAPSHOTS: tuple[StockSnapshot, ...] = (
    StockSnapshot(
        snapshot_id="stock-snap-20260528-s001-sku001",
        store_id="S001",
        sku_id="SKU001",
        on_hand_qty=220,
        reserved_qty=20,
        available_qty=200,
        snapshot_at=datetime(2026, 5, 28, 3, 0, tzinfo=timezone.utc),
    ),
)

OPEN_ORDERS: tuple[OpenOrder, ...] = (
    OpenOrder(
        order_id="open-order-20260529-001",
        store_id="S001",
        sku_id="SKU001",
        expected_delivery_date=date(2026, 5, 30),
        qty=80,
        source="WMS",
    ),
    OpenOrder(
        order_id="in-transit-20260531-001",
        store_id="S001",
        sku_id="SKU001",
        expected_delivery_date=date(2026, 5, 31),
        qty=60,
        source="in_transit",
    ),
)

POLICIES: tuple[ReplenishmentPolicy, ...] = (
    ReplenishmentPolicy(
        store_id="S001",
        sku_id="SKU001",
        lead_time_days=2,
        safety_stock_qty=90,
        presentation_stock_qty=25,
        min_order_qty=24,
        order_multiple=12,
    ),
)

INVENTORY_PROJECTIONS: tuple[InventoryProjection, ...] = (
    InventoryProjection(
        projection_id="projection-20260528-s001-sku001",
        store_id="S001",
        sku_id="SKU001",
        status=ProjectionStatus.PROJECTION_WARNING,
        forecast_version="regular-baseline-20260528-001",
        stock_snapshot_id="stock-snap-20260528-s001-sku001",
        calculated_at=datetime(2026, 5, 28, 4, 30, tzinfo=timezone.utc),
        lead_time_days=2,
        days=[
            InventoryProjectionDay(
                projection_date=date(2026, 5, 29),
                opening_stock_qty=200,
                demand_projection_qty=52,
                open_order_receipt_qty=0,
                in_transit_receipt_qty=0,
                projected_stock_qty=148,
                safety_stock_qty=90,
                stock_out_risk=StockOutRisk.NONE,
            ),
            InventoryProjectionDay(
                projection_date=date(2026, 5, 30),
                opening_stock_qty=148,
                demand_projection_qty=65,
                open_order_receipt_qty=80,
                in_transit_receipt_qty=0,
                projected_stock_qty=163,
                safety_stock_qty=90,
                stock_out_risk=StockOutRisk.NONE,
            ),
            InventoryProjectionDay(
                projection_date=date(2026, 5, 31),
                opening_stock_qty=163,
                demand_projection_qty=88,
                open_order_receipt_qty=0,
                in_transit_receipt_qty=60,
                projected_stock_qty=135,
                safety_stock_qty=90,
                stock_out_risk=StockOutRisk.NONE,
            ),
            InventoryProjectionDay(
                projection_date=date(2026, 6, 1),
                opening_stock_qty=135,
                demand_projection_qty=168,
                open_order_receipt_qty=0,
                in_transit_receipt_qty=0,
                projected_stock_qty=-33,
                safety_stock_qty=90,
                stock_out_risk=StockOutRisk.STOCK_OUT,
            ),
        ],
    ),
)


@router.get("/stock-snapshots")
def list_stock_snapshots() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in STOCK_SNAPSHOTS], "total": len(STOCK_SNAPSHOTS)}


@router.get("/open-orders")
def list_open_orders() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in OPEN_ORDERS], "total": len(OPEN_ORDERS)}


@router.get("/policies")
def list_replenishment_policies() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in POLICIES], "total": len(POLICIES)}


@router.get("/inventory-projections")
def list_inventory_projections() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in INVENTORY_PROJECTIONS], "total": len(INVENTORY_PROJECTIONS)}


@router.get("/inventory-projections/{projection_id}")
def get_inventory_projection(projection_id: str = Path(min_length=1)) -> dict[str, object]:
    for projection in INVENTORY_PROJECTIONS:
        if projection.projection_id == projection_id:
            return projection.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="inventory projection not found")
