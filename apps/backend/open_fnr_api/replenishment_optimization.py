from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum
from math import sqrt

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field


class OptimizationStatus(StrEnum):
    READY = "ready"
    WARNING = "warning"
    BLOCKED = "blocked"


class ServiceLevelTarget(BaseModel):
    abc_class: str = Field(pattern="^[ABC]$")
    xyz_class: str = Field(pattern="^[XYZ]$")
    service_level_target: float = Field(ge=0, le=1)
    safety_stock_z: float = Field(gt=0)


class ReplenishmentOptimizationRun(BaseModel):
    run_id: str
    business_date: date
    forecast_version: str
    training_dataset_id: str
    source_readiness_status: str
    total_store_sku_pairs: int = Field(ge=0)
    projected_stock_rows: int = Field(ge=0)
    order_proposal_rows: int = Field(ge=0)
    fresh_rows: int = Field(ge=0)
    service_level_impact: float
    stock_cost_impact: float
    waste_impact: float
    status: OptimizationStatus
    created_at: datetime


class OptimizationGate(BaseModel):
    run_id: str
    ready_for_export: bool
    gates: tuple[str, ...]
    blockers: tuple[str, ...]


router = APIRouter(prefix="/replenishment/optimization", tags=["replenishment-optimization"])


SERVICE_LEVEL_TARGETS: tuple[ServiceLevelTarget, ...] = (
    ServiceLevelTarget(abc_class="A", xyz_class="X", service_level_target=0.98, safety_stock_z=2.05),
    ServiceLevelTarget(abc_class="A", xyz_class="Y", service_level_target=0.97, safety_stock_z=1.88),
    ServiceLevelTarget(abc_class="A", xyz_class="Z", service_level_target=0.95, safety_stock_z=1.64),
    ServiceLevelTarget(abc_class="B", xyz_class="X", service_level_target=0.96, safety_stock_z=1.75),
    ServiceLevelTarget(abc_class="B", xyz_class="Y", service_level_target=0.95, safety_stock_z=1.64),
    ServiceLevelTarget(abc_class="B", xyz_class="Z", service_level_target=0.93, safety_stock_z=1.48),
    ServiceLevelTarget(abc_class="C", xyz_class="X", service_level_target=0.94, safety_stock_z=1.55),
    ServiceLevelTarget(abc_class="C", xyz_class="Y", service_level_target=0.92, safety_stock_z=1.41),
    ServiceLevelTarget(abc_class="C", xyz_class="Z", service_level_target=0.90, safety_stock_z=1.28),
)


OPTIMIZATION_RUNS: tuple[ReplenishmentOptimizationRun, ...] = (
    ReplenishmentOptimizationRun(
        run_id="repl-opt-20260528-001",
        business_date=date(2026, 5, 28),
        forecast_version="regular-baseline-20260528-001",
        training_dataset_id="training-snapshot-20260528-001",
        source_readiness_status="ready",
        total_store_sku_pairs=165000000,
        projected_stock_rows=4950000000,
        order_proposal_rows=165000000,
        fresh_rows=24000000,
        service_level_impact=0.012,
        stock_cost_impact=-0.034,
        waste_impact=-0.018,
        status=OptimizationStatus.READY,
        created_at=datetime(2026, 5, 28, 8, 15, tzinfo=timezone.utc),
    ),
)


def calculate_safety_stock(demand_std_qty: float, lead_time_days: int, safety_stock_z: float) -> float:
    if demand_std_qty < 0:
        raise ValueError("demand_std_qty must be non-negative")
    if lead_time_days < 0:
        raise ValueError("lead_time_days must be non-negative")
    return round(safety_stock_z * demand_std_qty * sqrt(max(lead_time_days, 1)), 2)


def get_target_for_segment(abc_class: str, xyz_class: str) -> ServiceLevelTarget:
    for target in SERVICE_LEVEL_TARGETS:
        if target.abc_class == abc_class and target.xyz_class == xyz_class:
            return target
    raise ValueError("unknown ABC/XYZ segment")


def optimization_gate(run: ReplenishmentOptimizationRun) -> OptimizationGate:
    blockers: list[str] = []
    if run.source_readiness_status != "ready":
        blockers.append("source_readiness_not_ready")
    if run.projected_stock_rows <= 0:
        blockers.append("projected_stock_missing")
    if run.order_proposal_rows <= 0:
        blockers.append("order_proposals_missing")
    if run.status == OptimizationStatus.BLOCKED:
        blockers.append("optimization_run_blocked")
    return OptimizationGate(
        run_id=run.run_id,
        ready_for_export=not blockers,
        gates=("source_readiness_ready", "projected_stock_generated", "order_proposals_generated", "fresh_waste_impact_calculated"),
        blockers=tuple(blockers),
    )


@router.get("/service-level-targets")
def list_service_level_targets() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in SERVICE_LEVEL_TARGETS], "total": len(SERVICE_LEVEL_TARGETS)}


@router.get("/runs")
def list_optimization_runs() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in OPTIMIZATION_RUNS], "total": len(OPTIMIZATION_RUNS)}


@router.get("/runs/{run_id}/gate")
def get_optimization_gate(run_id: str = Path(min_length=1)) -> dict[str, object]:
    for run in OPTIMIZATION_RUNS:
        if run.run_id == run_id:
            return optimization_gate(run).model_dump(mode="json")
    raise HTTPException(status_code=404, detail="optimization run not found")
