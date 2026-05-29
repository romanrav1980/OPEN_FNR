from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field, model_validator

from .repositories import OperationalDecisionRecord, operational_decision_repository


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


class OrderProposalStatus(StrEnum):
    DRAFT = "draft"
    AUTO_APPROVED = "auto_approved"
    MANUAL_REVIEW = "manual_review"
    BLOCKED = "blocked"


class FinalOrderStatus(StrEnum):
    MANUAL_REVIEW = "manual_review"
    ADJUSTED = "adjusted"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class FreshStatus(StrEnum):
    CALCULATED = "calculated"
    SPOILAGE_RISK = "spoilage_risk"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    ADJUSTED = "adjusted"


class SpoilageRisk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


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


class OrderProposalExplanation(BaseModel):
    gross_requirement_qty: float = Field(ge=0)
    projected_stock_at_receipt_qty: float
    safety_stock_qty: float = Field(ge=0)
    presentation_stock_qty: float = Field(ge=0)
    net_requirement_qty: float = Field(ge=0)
    raw_order_qty: float = Field(ge=0)
    rounded_order_qty: float = Field(ge=0)
    min_order_qty: float = Field(gt=0)
    order_multiple: float = Field(gt=0)
    constraint_flags: list[str]


class OrderProposal(BaseModel):
    proposal_id: str
    projection_id: str
    store_id: str
    sku_id: str
    supplier_id: str
    status: OrderProposalStatus
    order_date: date
    expected_delivery_date: date
    recommended_order_qty: float = Field(ge=0)
    explanation: OrderProposalExplanation
    created_at: datetime


class OrderAdjustmentRequest(BaseModel):
    final_order_qty: float = Field(ge=0)
    actor: str = Field(min_length=1)
    actor_role: str
    reason: str = Field(min_length=1)
    comment: str = Field(min_length=1)


class FinalOrder(BaseModel):
    final_order_id: str
    proposal_id: str
    store_id: str
    sku_id: str
    supplier_id: str
    status: FinalOrderStatus
    proposed_qty: float = Field(ge=0)
    final_order_qty: float = Field(ge=0)
    projected_stock_after_order_qty: float
    export_ready: bool
    updated_at: datetime


class OrderAuditEvent(BaseModel):
    event_id: str
    proposal_id: str
    actor: str
    actor_role: str
    old_order_qty: float = Field(ge=0)
    new_order_qty: float = Field(ge=0)
    reason: str
    comment: str
    created_at: datetime


class ReplenishmentWorkbench(BaseModel):
    filters: dict[str, list[str]]
    proposals: list[OrderProposal]
    final_orders: list[FinalOrder]
    audit_events: list[OrderAuditEvent]


class FreshBatch(BaseModel):
    batch_id: str
    store_id: str
    sku_id: str
    received_date: date
    expiration_date: date
    qty: float = Field(ge=0)
    remaining_shelf_life_days: int = Field(ge=0)


class FreshProjectionDay(BaseModel):
    projection_date: date
    demand_qty: float = Field(ge=0)
    available_qty: float = Field(ge=0)
    expected_waste_qty: float = Field(ge=0)
    service_level: float = Field(ge=0, le=1)


class FreshWorkbenchItem(BaseModel):
    item_id: str
    store_id: str
    sku_id: str
    status: FreshStatus
    spoilage_risk: SpoilageRisk
    recommended_order_qty: float = Field(ge=0)
    adjusted_order_qty: float = Field(ge=0)
    expected_waste_before_qty: float = Field(ge=0)
    expected_waste_after_qty: float = Field(ge=0)
    service_level_before: float = Field(ge=0, le=1)
    service_level_after: float = Field(ge=0, le=1)
    batches: list[FreshBatch]
    projection: list[FreshProjectionDay]


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


def calculate_net_requirement(
    projected_stock_at_receipt_qty: float,
    gross_requirement_qty: float,
    safety_stock_qty: float,
    presentation_stock_qty: float,
) -> float:
    target_qty = gross_requirement_qty + safety_stock_qty + presentation_stock_qty
    return max(0, target_qty - projected_stock_at_receipt_qty)


def round_order_qty(raw_order_qty: float, min_order_qty: float, order_multiple: float) -> float:
    if raw_order_qty <= 0:
        return 0
    constrained_qty = max(raw_order_qty, min_order_qty)
    return ((constrained_qty + order_multiple - 1) // order_multiple) * order_multiple


def order_batches_fefo(batches: list[FreshBatch]) -> list[FreshBatch]:
    return sorted(batches, key=lambda batch: (batch.expiration_date, batch.received_date, batch.batch_id))


def estimate_expected_waste(available_qty: float, demand_qty: float) -> float:
    return max(0, available_qty - demand_qty)


def classify_spoilage_risk(expected_waste_qty: float, available_qty: float) -> SpoilageRisk:
    if available_qty == 0:
        return SpoilageRisk.LOW
    waste_ratio = expected_waste_qty / available_qty
    if waste_ratio >= 0.25:
        return SpoilageRisk.HIGH
    if waste_ratio >= 0.1:
        return SpoilageRisk.MEDIUM
    return SpoilageRisk.LOW


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

ORDER_PROPOSALS: tuple[OrderProposal, ...] = (
    OrderProposal(
        proposal_id="order-proposal-20260528-s001-sku001",
        projection_id="projection-20260528-s001-sku001",
        store_id="S001",
        sku_id="SKU001",
        supplier_id="SUP001",
        status=OrderProposalStatus.MANUAL_REVIEW,
        order_date=date(2026, 5, 28),
        expected_delivery_date=date(2026, 5, 30),
        recommended_order_qty=276,
        explanation=OrderProposalExplanation(
            gross_requirement_qty=321,
            projected_stock_at_receipt_qty=163,
            safety_stock_qty=90,
            presentation_stock_qty=25,
            net_requirement_qty=273,
            raw_order_qty=273,
            rounded_order_qty=276,
            min_order_qty=24,
            order_multiple=12,
            constraint_flags=["stock_out_risk", "manual_review_required"],
        ),
        created_at=datetime(2026, 5, 28, 5, 0, tzinfo=timezone.utc),
    ),
    OrderProposal(
        proposal_id="order-proposal-20260528-s001-sku002",
        projection_id="projection-20260528-s001-sku002",
        store_id="S001",
        sku_id="SKU002",
        supplier_id="SUP001",
        status=OrderProposalStatus.AUTO_APPROVED,
        order_date=date(2026, 5, 28),
        expected_delivery_date=date(2026, 5, 30),
        recommended_order_qty=48,
        explanation=OrderProposalExplanation(
            gross_requirement_qty=42,
            projected_stock_at_receipt_qty=55,
            safety_stock_qty=40,
            presentation_stock_qty=10,
            net_requirement_qty=37,
            raw_order_qty=37,
            rounded_order_qty=48,
            min_order_qty=24,
            order_multiple=12,
            constraint_flags=["rounded_to_order_multiple"],
        ),
        created_at=datetime(2026, 5, 28, 5, 0, tzinfo=timezone.utc),
    ),
    OrderProposal(
        proposal_id="order-proposal-20260528-s001-sku003",
        projection_id="projection-20260528-s001-sku003",
        store_id="S001",
        sku_id="SKU003",
        supplier_id="SUP002",
        status=OrderProposalStatus.BLOCKED,
        order_date=date(2026, 5, 28),
        expected_delivery_date=date(2026, 5, 31),
        recommended_order_qty=0,
        explanation=OrderProposalExplanation(
            gross_requirement_qty=120,
            projected_stock_at_receipt_qty=20,
            safety_stock_qty=50,
            presentation_stock_qty=15,
            net_requirement_qty=165,
            raw_order_qty=165,
            rounded_order_qty=168,
            min_order_qty=24,
            order_multiple=12,
            constraint_flags=["supplier_blocked", "calendar_closed"],
        ),
        created_at=datetime(2026, 5, 28, 5, 0, tzinfo=timezone.utc),
    ),
)

FINAL_ORDERS: tuple[FinalOrder, ...] = (
    FinalOrder(
        final_order_id="final-order-20260528-s001-sku001",
        proposal_id="order-proposal-20260528-s001-sku001",
        store_id="S001",
        sku_id="SKU001",
        supplier_id="SUP001",
        status=FinalOrderStatus.MANUAL_REVIEW,
        proposed_qty=276,
        final_order_qty=276,
        projected_stock_after_order_qty=243,
        export_ready=False,
        updated_at=datetime(2026, 5, 28, 5, 5, tzinfo=timezone.utc),
    ),
    FinalOrder(
        final_order_id="final-order-20260528-s001-sku002",
        proposal_id="order-proposal-20260528-s001-sku002",
        store_id="S001",
        sku_id="SKU002",
        supplier_id="SUP001",
        status=FinalOrderStatus.APPROVED,
        proposed_qty=48,
        final_order_qty=48,
        projected_stock_after_order_qty=103,
        export_ready=True,
        updated_at=datetime(2026, 5, 28, 5, 10, tzinfo=timezone.utc),
    ),
)

ORDER_AUDIT_EVENTS: tuple[OrderAuditEvent, ...] = (
    OrderAuditEvent(
        event_id="order-audit-20260528-001",
        proposal_id="order-proposal-20260528-s001-sku002",
        actor="replenishment.planner@example.org",
        actor_role="Replenishment Planner",
        old_order_qty=48,
        new_order_qty=48,
        reason="auto approval accepted",
        comment="No risk flags.",
        created_at=datetime(2026, 5, 28, 5, 10, tzinfo=timezone.utc),
    ),
)

FRESH_WORKBENCH_ITEMS: tuple[FreshWorkbenchItem, ...] = (
    FreshWorkbenchItem(
        item_id="fresh-s001-sku001-20260528",
        store_id="S001",
        sku_id="SKU001",
        status=FreshStatus.SPOILAGE_RISK,
        spoilage_risk=SpoilageRisk.HIGH,
        recommended_order_qty=96,
        adjusted_order_qty=72,
        expected_waste_before_qty=34,
        expected_waste_after_qty=14,
        service_level_before=0.97,
        service_level_after=0.95,
        batches=[
            FreshBatch(
                batch_id="batch-s001-sku001-001",
                store_id="S001",
                sku_id="SKU001",
                received_date=date(2026, 5, 26),
                expiration_date=date(2026, 5, 30),
                qty=42,
                remaining_shelf_life_days=2,
            ),
            FreshBatch(
                batch_id="batch-s001-sku001-002",
                store_id="S001",
                sku_id="SKU001",
                received_date=date(2026, 5, 27),
                expiration_date=date(2026, 6, 1),
                qty=58,
                remaining_shelf_life_days=4,
            ),
        ],
        projection=[
            FreshProjectionDay(
                projection_date=date(2026, 5, 29),
                demand_qty=38,
                available_qty=100,
                expected_waste_qty=0,
                service_level=0.98,
            ),
            FreshProjectionDay(
                projection_date=date(2026, 5, 30),
                demand_qty=44,
                available_qty=62,
                expected_waste_qty=18,
                service_level=0.97,
            ),
            FreshProjectionDay(
                projection_date=date(2026, 5, 31),
                demand_qty=48,
                available_qty=38,
                expected_waste_qty=16,
                service_level=0.95,
            ),
        ],
    ),
)


def preview_projected_stock_after_order(current_projected_stock_qty: float, final_order_qty: float) -> float:
    return current_projected_stock_qty + final_order_qty


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


@router.get("/order-proposals")
def list_order_proposals() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in ORDER_PROPOSALS], "total": len(ORDER_PROPOSALS)}


@router.get("/order-proposals/{proposal_id}")
def get_order_proposal(proposal_id: str = Path(min_length=1)) -> dict[str, object]:
    for proposal in ORDER_PROPOSALS:
        if proposal.proposal_id == proposal_id:
            return proposal.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="order proposal not found")


@router.get("/workbench")
def get_replenishment_workbench() -> dict[str, object]:
    workbench = ReplenishmentWorkbench(
        filters={
            "suppliers": ["SUP001", "SUP002"],
            "distribution_centers": ["DC001"],
            "stores": ["S001"],
            "categories": ["fresh", "grocery"],
        },
        proposals=list(ORDER_PROPOSALS),
        final_orders=list(FINAL_ORDERS),
        audit_events=list(ORDER_AUDIT_EVENTS),
    )
    return workbench.model_dump(mode="json")


@router.post("/order-proposals/{proposal_id}/adjust")
def adjust_order_proposal(proposal_id: str, payload: OrderAdjustmentRequest) -> dict[str, object]:
    if payload.actor_role != "Replenishment Planner":
        raise HTTPException(status_code=403, detail="only Replenishment Planner can adjust final order")

    final_order = next((item for item in FINAL_ORDERS if item.proposal_id == proposal_id), None)
    if final_order is None:
        raise HTTPException(status_code=404, detail="final order not found")
    if final_order.status == FinalOrderStatus.APPROVED:
        raise HTTPException(status_code=409, detail="approved final order cannot be adjusted")

    adjusted_order = final_order.model_copy(
        update={
            "status": FinalOrderStatus.ADJUSTED,
            "final_order_qty": payload.final_order_qty,
            "projected_stock_after_order_qty": preview_projected_stock_after_order(-33, payload.final_order_qty),
            "export_ready": False,
            "updated_at": datetime(2026, 5, 28, 6, 0, tzinfo=timezone.utc),
        }
    )
    audit_event = OrderAuditEvent(
        event_id=f"order-audit-{proposal_id}-adjusted",
        proposal_id=proposal_id,
        actor=payload.actor,
        actor_role=payload.actor_role,
        old_order_qty=final_order.final_order_qty,
        new_order_qty=payload.final_order_qty,
        reason=payload.reason,
        comment=payload.comment,
        created_at=datetime(2026, 5, 28, 6, 0, tzinfo=timezone.utc),
    )
    operational_decision_repository.upsert_decision(
        OperationalDecisionRecord(
            decision_id=f"replenishment-adjust-{proposal_id}",
            decision_type="order_proposal_adjustment",
            object_type="order_proposal",
            object_id=proposal_id,
            status=adjusted_order.status.value,
            actor=payload.actor,
            actor_role=payload.actor_role,
            idempotency_key=f"{proposal_id}:adjust:{payload.actor}:{payload.final_order_qty}",
            correlation_id=proposal_id,
            payload={
                "old_order_qty": final_order.final_order_qty,
                "new_order_qty": payload.final_order_qty,
                "reason": payload.reason,
                "comment": payload.comment,
                "projected_stock_after_order_qty": adjusted_order.projected_stock_after_order_qty,
            },
            created_at=audit_event.created_at,
            updated_at=audit_event.created_at,
        )
    )
    return {"final_order": adjusted_order.model_dump(mode="json"), "audit_event": audit_event.model_dump(mode="json")}


@router.get("/fresh/workbench")
def get_fresh_workbench() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in FRESH_WORKBENCH_ITEMS], "total": len(FRESH_WORKBENCH_ITEMS)}


@router.get("/fresh/workbench/{item_id}")
def get_fresh_workbench_item(item_id: str) -> dict[str, object]:
    item = next((fresh_item for fresh_item in FRESH_WORKBENCH_ITEMS if fresh_item.item_id == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="fresh item not found")
    return item.model_dump(mode="json")
