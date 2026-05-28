from datetime import datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field


router = APIRouter(prefix="/multi-echelon", tags=["multi-echelon"])


class DcPlanStatus(StrEnum):
    CALCULATED = "calculated"
    SHORTAGE = "shortage"
    ALLOCATED = "allocated"
    APPROVED = "approved"


class AllocationPriority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class StoreDemand(BaseModel):
    store_id: str
    region_id: str
    dc_id: str
    sku_id: str
    demand_qty: float = Field(ge=0)
    priority: AllocationPriority
    service_risk: float = Field(ge=0, le=1)


class DcStock(BaseModel):
    dc_id: str
    region_id: str
    sku_id: str
    on_hand_qty: float = Field(ge=0)
    inbound_qty: float = Field(ge=0)
    reserved_qty: float = Field(ge=0)

    @property
    def available_qty(self) -> float:
        return self.on_hand_qty + self.inbound_qty - self.reserved_qty


class StoreAllocation(BaseModel):
    store_id: str
    requested_qty: float = Field(ge=0)
    allocated_qty: float = Field(ge=0)
    unfilled_qty: float = Field(ge=0)
    priority: AllocationPriority
    reason: str


class DcReplenishmentPlan(BaseModel):
    plan_id: str
    dc_id: str
    region_id: str
    sku_id: str
    status: DcPlanStatus
    total_store_demand_qty: float = Field(ge=0)
    available_dc_qty: float = Field(ge=0)
    shortage_qty: float = Field(ge=0)
    allocation_rule: str
    affected_stores: int = Field(ge=0)
    order_cutoff: datetime
    updated_at: datetime


class DcAllocationAuditEvent(BaseModel):
    event_id: str
    plan_id: str
    actor: str
    event_type: str
    message: str
    created_at: datetime


class ApproveAllocationRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    comment: str = Field(min_length=1)


STORE_DEMANDS: tuple[StoreDemand, ...] = (
    StoreDemand(
        store_id="S001",
        region_id="north",
        dc_id="DC001",
        sku_id="SKU001",
        demand_qty=120,
        priority=AllocationPriority.HIGH,
        service_risk=0.91,
    ),
    StoreDemand(
        store_id="S002",
        region_id="north",
        dc_id="DC001",
        sku_id="SKU001",
        demand_qty=90,
        priority=AllocationPriority.MEDIUM,
        service_risk=0.63,
    ),
    StoreDemand(
        store_id="S003",
        region_id="north",
        dc_id="DC001",
        sku_id="SKU001",
        demand_qty=60,
        priority=AllocationPriority.LOW,
        service_risk=0.28,
    ),
)

DC_STOCKS: tuple[DcStock, ...] = (
    DcStock(dc_id="DC001", region_id="north", sku_id="SKU001", on_hand_qty=180, inbound_qty=30, reserved_qty=0),
)


def aggregate_store_demand(store_demands: tuple[StoreDemand, ...], dc_id: str, sku_id: str) -> float:
    return sum(row.demand_qty for row in store_demands if row.dc_id == dc_id and row.sku_id == sku_id)


def calculate_available_dc_qty(stock: DcStock) -> float:
    return max(stock.available_qty, 0)


def calculate_dc_shortage(total_demand_qty: float, available_qty: float) -> float:
    return max(total_demand_qty - available_qty, 0)


def allocate_dc_stock(store_demands: tuple[StoreDemand, ...], available_qty: float) -> tuple[StoreAllocation, ...]:
    priority_rank = {AllocationPriority.HIGH: 0, AllocationPriority.MEDIUM: 1, AllocationPriority.LOW: 2}
    sorted_demands = sorted(
        store_demands,
        key=lambda item: (priority_rank[item.priority], -item.service_risk, item.store_id),
    )
    remaining = available_qty
    allocations: list[StoreAllocation] = []
    for demand in sorted_demands:
        allocated = min(demand.demand_qty, max(remaining, 0))
        remaining -= allocated
        unfilled = demand.demand_qty - allocated
        reason = "priority and service risk covered" if unfilled == 0 else "DC shortage after higher priority allocation"
        allocations.append(
            StoreAllocation(
                store_id=demand.store_id,
                requested_qty=demand.demand_qty,
                allocated_qty=allocated,
                unfilled_qty=unfilled,
                priority=demand.priority,
                reason=reason,
            )
        )
    return tuple(allocations)


def assert_dc_scope(actor_region: str, dc_region: str) -> None:
    if actor_region != dc_region and actor_region != "all":
        raise HTTPException(status_code=403, detail="actor is not allowed to access this DC region")


def build_dc_plan() -> DcReplenishmentPlan:
    stock = DC_STOCKS[0]
    total_demand = aggregate_store_demand(STORE_DEMANDS, stock.dc_id, stock.sku_id)
    available = calculate_available_dc_qty(stock)
    shortage = calculate_dc_shortage(total_demand, available)
    status = DcPlanStatus.SHORTAGE if shortage > 0 else DcPlanStatus.CALCULATED
    return DcReplenishmentPlan(
        plan_id="dc-plan-20260528-dc001-sku001",
        dc_id=stock.dc_id,
        region_id=stock.region_id,
        sku_id=stock.sku_id,
        status=status,
        total_store_demand_qty=total_demand,
        available_dc_qty=available,
        shortage_qty=shortage,
        allocation_rule="priority_service_risk_first",
        affected_stores=len(STORE_DEMANDS),
        order_cutoff=datetime(2026, 5, 28, 16, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 28, 10, 0, tzinfo=timezone.utc),
    )


@router.get("/dc-plans")
def list_dc_plans(actor_region: str = "all") -> dict[str, object]:
    plan = build_dc_plan()
    assert_dc_scope(actor_region, plan.region_id)
    return {"items": [plan.model_dump(mode="json")], "total": 1}


@router.get("/dc-plans/{plan_id}")
def get_dc_plan(plan_id: str = Path(min_length=1), actor_region: str = "all") -> dict[str, object]:
    plan = build_dc_plan()
    if plan.plan_id != plan_id:
        raise HTTPException(status_code=404, detail="DC plan not found")
    assert_dc_scope(actor_region, plan.region_id)
    return plan.model_dump(mode="json")


@router.get("/dc-plans/{plan_id}/allocations")
def get_dc_allocations(plan_id: str = Path(min_length=1), actor_region: str = "all") -> dict[str, object]:
    plan = build_dc_plan()
    if plan.plan_id != plan_id:
        raise HTTPException(status_code=404, detail="DC plan not found")
    assert_dc_scope(actor_region, plan.region_id)
    allocations = allocate_dc_stock(STORE_DEMANDS, plan.available_dc_qty)
    return {
        "plan_id": plan_id,
        "allocation_rule": plan.allocation_rule,
        "items": [item.model_dump(mode="json") for item in allocations],
        "total": len(allocations),
    }


@router.post("/dc-plans/{plan_id}/approve")
def approve_dc_allocation(plan_id: str, payload: ApproveAllocationRequest) -> dict[str, object]:
    plan = build_dc_plan()
    if plan.plan_id != plan_id:
        raise HTTPException(status_code=404, detail="DC plan not found")
    if payload.actor_role != "Supply Chain Manager":
        raise HTTPException(status_code=403, detail="only Supply Chain Manager can approve DC allocation")
    approved = plan.model_copy(update={"status": DcPlanStatus.APPROVED, "updated_at": datetime(2026, 5, 28, 10, 30, tzinfo=timezone.utc)})
    audit_event = DcAllocationAuditEvent(
        event_id=f"dc-audit-{plan_id}-approved",
        plan_id=plan_id,
        actor=payload.actor,
        event_type="allocation_approved",
        message=payload.comment,
        created_at=datetime(2026, 5, 28, 10, 30, tzinfo=timezone.utc),
    )
    return {"plan": approved.model_dump(mode="json"), "audit_event": audit_event.model_dump(mode="json")}
