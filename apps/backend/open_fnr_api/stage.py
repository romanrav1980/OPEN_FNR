from datetime import datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/stage", tags=["stage-rehearsal"])


class StageStepStatus(StrEnum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


class StageRunStatus(StrEnum):
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    GO_NO_GO_READY = "go_no_go_ready"


class StageStep(BaseModel):
    order: int = Field(gt=0)
    key: str
    name: str
    owner_role: str
    status: StageStepStatus
    evidence: str


class UatChecklistItem(BaseModel):
    item_id: str
    scenario: str
    role: str
    status: StageStepStatus
    evidence: str


class StageRun(BaseModel):
    run_id: str
    status: StageRunStatus
    snapshot_id: str
    started_at: datetime
    completed_at: datetime
    steps: tuple[StageStep, ...]
    uat_checklist: tuple[UatChecklistItem, ...]
    critical_defects: int = Field(ge=0)
    accepted_risks: int = Field(ge=0)


STAGE_STEPS: tuple[StageStep, ...] = (
    StageStep(order=1, key="dq", name="DQ checks", owner_role="Data Engineer", status=StageStepStatus.PASSED, evidence="DQ blockers = 0"),
    StageStep(order=2, key="forecast", name="Regular forecast", owner_role="Forecast Planner", status=StageStepStatus.PASSED, evidence="WAPE smoke accepted"),
    StageStep(order=3, key="promo", name="Promo forecast", owner_role="Promo Planner", status=StageStepStatus.PASSED, evidence="promo uplift exported"),
    StageStep(order=4, key="replenishment", name="Order proposals", owner_role="Replenishment Planner", status=StageStepStatus.PASSED, evidence="proposal batch generated"),
    StageStep(order=5, key="exceptions", name="Exception review", owner_role="Business Owner", status=StageStepStatus.WARNING, evidence="2 accepted non-blocking exceptions"),
    StageStep(order=6, key="publication", name="ERP/WMS/DWH export", owner_role="Integration Engineer", status=StageStepStatus.PASSED, evidence="idempotency keys accepted"),
)

UAT_CHECKLIST: tuple[UatChecklistItem, ...] = (
    UatChecklistItem(item_id="uat-001", scenario="Data owner accepts stage snapshot", role="Data Owner", status=StageStepStatus.PASSED, evidence="snapshot stage-20260528-001"),
    UatChecklistItem(item_id="uat-002", scenario="Planner reviews forecast and adjustment", role="Forecast Planner", status=StageStepStatus.PASSED, evidence="adjustment audit exists"),
    UatChecklistItem(item_id="uat-003", scenario="Supply manager approves shortage allocation", role="Supply Chain Manager", status=StageStepStatus.PASSED, evidence="DC allocation approved"),
    UatChecklistItem(item_id="uat-004", scenario="Integration owner validates export status", role="Integration Engineer", status=StageStepStatus.PASSED, evidence="ERP/WMS/DWH mocks accepted"),
)


def is_stage_go_no_go_ready(steps: tuple[StageStep, ...], critical_defects: int) -> bool:
    return critical_defects == 0 and all(step.status != StageStepStatus.FAILED for step in steps)


def build_stage_run() -> StageRun:
    status = StageRunStatus.GO_NO_GO_READY if is_stage_go_no_go_ready(STAGE_STEPS, critical_defects=0) else StageRunStatus.FAILED
    return StageRun(
        run_id="stage-run-20260528-001",
        status=status,
        snapshot_id="stage-snapshot-20260528-001",
        started_at=datetime(2026, 5, 28, 14, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 5, 28, 15, 45, tzinfo=timezone.utc),
        steps=STAGE_STEPS,
        uat_checklist=UAT_CHECKLIST,
        critical_defects=0,
        accepted_risks=2,
    )


@router.get("/runs")
def list_stage_runs() -> dict[str, object]:
    run = build_stage_run()
    return {"items": [run.model_dump(mode="json")], "total": 1}


@router.get("/runs/{run_id}")
def get_stage_run(run_id: str) -> dict[str, object]:
    run = build_stage_run()
    if run.run_id != run_id:
        raise HTTPException(status_code=404, detail="stage run not found")
    return run.model_dump(mode="json")


@router.get("/runs/{run_id}/trace")
def get_stage_trace(run_id: str) -> dict[str, object]:
    run = build_stage_run()
    if run.run_id != run_id:
        raise HTTPException(status_code=404, detail="stage run not found")
    return {
        "run_id": run_id,
        "trace": [
            {"order": step.order, "key": step.key, "owner_role": step.owner_role, "status": step.status, "evidence": step.evidence}
            for step in run.steps
        ],
    }
