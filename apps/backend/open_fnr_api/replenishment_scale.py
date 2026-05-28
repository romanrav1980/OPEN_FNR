from datetime import datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/replenishment-scale", tags=["replenishment-scale"])


class BulkRunStatus(StrEnum):
    CALCULATED = "calculated"
    APPROVAL_READY = "approval_ready"
    APPROVED = "approved"
    EXPORT_QUEUED = "export_queued"
    FAILED = "failed"


class BulkActionStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ReplenishmentPartition(BaseModel):
    partition_id: str
    region_id: str
    category_id: str
    proposal_count: int = Field(ge=0)
    projected_stock_rows: int = Field(ge=0)
    constraint_eval_ms: int = Field(ge=0)
    status: BulkRunStatus


class IndustrialReplenishmentRun(BaseModel):
    run_id: str
    status: BulkRunStatus
    partitions: tuple[ReplenishmentPartition, ...]
    total_proposals: int = Field(ge=0)
    total_projected_stock_rows: int = Field(ge=0)
    runtime_minutes: int = Field(ge=0)
    retention_days: int = Field(gt=0)
    calculated_at: datetime


class BulkApprovalRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    saved_filter_id: str
    reason: str = Field(min_length=1)


class BulkApprovalResult(BaseModel):
    action_id: str
    run_id: str
    status: BulkActionStatus
    accepted_proposals: int = Field(ge=0)
    rejected_proposals: int = Field(ge=0)
    audit_message: str


PARTITIONS: tuple[ReplenishmentPartition, ...] = (
    ReplenishmentPartition(
        partition_id="repl-north-fresh-p001",
        region_id="north",
        category_id="fresh",
        proposal_count=1_240_000,
        projected_stock_rows=37_200_000,
        constraint_eval_ms=420,
        status=BulkRunStatus.APPROVAL_READY,
    ),
    ReplenishmentPartition(
        partition_id="repl-north-grocery-p002",
        region_id="north",
        category_id="grocery",
        proposal_count=2_360_000,
        projected_stock_rows=70_800_000,
        constraint_eval_ms=510,
        status=BulkRunStatus.APPROVAL_READY,
    ),
)


def build_industrial_replenishment_run() -> IndustrialReplenishmentRun:
    return IndustrialReplenishmentRun(
        run_id="industrial-repl-20260528-001",
        status=BulkRunStatus.APPROVAL_READY,
        partitions=PARTITIONS,
        total_proposals=sum(partition.proposal_count for partition in PARTITIONS),
        total_projected_stock_rows=sum(partition.projected_stock_rows for partition in PARTITIONS),
        runtime_minutes=94,
        retention_days=180,
        calculated_at=datetime(2026, 5, 28, 19, 0, tzinfo=timezone.utc),
    )


def bulk_auto_approval_allowed(partitions: tuple[ReplenishmentPartition, ...], runtime_minutes: int) -> bool:
    constraints_ok = all(partition.constraint_eval_ms <= 750 for partition in partitions)
    statuses_ok = all(partition.status == BulkRunStatus.APPROVAL_READY for partition in partitions)
    return constraints_ok and statuses_ok and runtime_minutes <= 120


@router.get("/runs")
def list_replenishment_scale_runs() -> dict[str, object]:
    run = build_industrial_replenishment_run()
    return {"items": [run.model_dump(mode="json")], "total": 1}


@router.get("/runs/{run_id}/bulk-gate")
def get_bulk_gate(run_id: str) -> dict[str, object]:
    run = build_industrial_replenishment_run()
    if run.run_id != run_id:
        raise HTTPException(status_code=404, detail="industrial replenishment run not found")
    return {"run_id": run_id, "bulk_approval_allowed": bulk_auto_approval_allowed(run.partitions, run.runtime_minutes)}


@router.post("/runs/{run_id}/bulk-approve")
def bulk_approve(run_id: str, payload: BulkApprovalRequest) -> dict[str, object]:
    run = build_industrial_replenishment_run()
    if run.run_id != run_id:
        raise HTTPException(status_code=404, detail="industrial replenishment run not found")
    if payload.actor_role != "Replenishment Owner":
        raise HTTPException(status_code=403, detail="Replenishment Owner role required")
    if not bulk_auto_approval_allowed(run.partitions, run.runtime_minutes):
        raise HTTPException(status_code=409, detail="bulk approval gate failed")
    result = BulkApprovalResult(
        action_id="bulk-approval-20260528-001",
        run_id=run_id,
        status=BulkActionStatus.ACCEPTED,
        accepted_proposals=run.total_proposals,
        rejected_proposals=0,
        audit_message=f"{payload.actor} approved {run.total_proposals} proposals by filter {payload.saved_filter_id}",
    )
    return result.model_dump(mode="json")


@router.get("/runs/{run_id}/export-package")
def get_export_package(run_id: str) -> dict[str, object]:
    run = build_industrial_replenishment_run()
    if run.run_id != run_id:
        raise HTTPException(status_code=404, detail="industrial replenishment run not found")
    return {
        "run_id": run_id,
        "package_id": "repl-export-20260528-001",
        "status": "queued",
        "target": "ERP/WMS",
        "idempotency_key": f"{run_id}:erp-wms:v1",
        "proposal_count": run.total_proposals,
    }
