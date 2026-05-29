from datetime import datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/pilot", tags=["business-pilot"])


class PilotStatus(StrEnum):
    RUNNING = "running"
    ACCEPTANCE_PENDING = "acceptance_pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"


class PilotIssueStatus(StrEnum):
    OPEN = "open"
    TRIAGED = "triaged"
    ACCEPTED_RISK = "accepted_risk"
    RESOLVED = "resolved"


class FeedbackType(StrEnum):
    BUG = "bug"
    USABILITY = "usability"
    BUSINESS_RULE = "business_rule"


class PilotScope(BaseModel):
    scope_id: str
    regions: tuple[str, ...]
    stores: tuple[str, ...]
    categories: tuple[str, ...]
    users: tuple[str, ...]
    status: PilotStatus


class PilotKpi(BaseModel):
    name: str
    value: float
    threshold: float
    unit: str
    status: str


class PilotFeedback(BaseModel):
    feedback_id: str
    user: str
    feedback_type: FeedbackType
    text: str
    linked_module: str
    status: PilotIssueStatus
    created_at: datetime


class PilotIssue(BaseModel):
    issue_id: str
    severity: str
    status: PilotIssueStatus
    owner_role: str
    summary: str
    sla_due_at: datetime


class PilotAcceptance(BaseModel):
    acceptance_id: str
    signed_by: str
    signed_role: str
    status: PilotStatus
    decision: str
    signed_at: datetime | None


class PilotShadowChecklistItem(BaseModel):
    item_id: str
    owner_role: str
    status: str
    evidence: str


class PilotRunbookStep(BaseModel):
    step: int
    owner_role: str
    action: str
    exit_criteria: str


class PilotRollbackAction(BaseModel):
    trigger: str
    action: str
    owner_role: str
    rto_minutes: int = Field(gt=0)


class PilotShadowPack(BaseModel):
    pack_id: str
    scope: PilotScope
    mode: str
    business_dates: tuple[str, ...]
    checklist: tuple[PilotShadowChecklistItem, ...]
    runbook: tuple[PilotRunbookStep, ...]
    rollback: tuple[PilotRollbackAction, ...]
    ready_for_shadow: bool


class PilotAcceptanceRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    decision: str = Field(min_length=1)


PILOT_SCOPE = PilotScope(
    scope_id="pilot-north-fresh-001",
    regions=("north",),
    stores=("S001", "S002", "S003"),
    categories=("fresh", "grocery"),
    users=("forecast.planner@example.org", "supply.manager@example.org", "business.owner@example.org"),
    status=PilotStatus.ACCEPTANCE_PENDING,
)

PILOT_KPIS: tuple[PilotKpi, ...] = (
    PilotKpi(name="wape", value=15.7, threshold=18.0, unit="%", status="green"),
    PilotKpi(name="service_level", value=96.2, threshold=95.0, unit="%", status="green"),
    PilotKpi(name="lost_sales_reduction", value=4.1, threshold=3.0, unit="pp", status="green"),
    PilotKpi(name="overstock_reduction", value=2.4, threshold=2.0, unit="pp", status="green"),
)

PILOT_FEEDBACK: tuple[PilotFeedback, ...] = (
    PilotFeedback(
        feedback_id="fb-20260528-001",
        user="forecast.planner@example.org",
        feedback_type=FeedbackType.USABILITY,
        text="Forecast review needs quicker navigation from KPI alert to SKU detail.",
        linked_module="forecast-workbench",
        status=PilotIssueStatus.TRIAGED,
        created_at=datetime(2026, 5, 28, 16, 10, tzinfo=timezone.utc),
    ),
)

PILOT_ISSUES: tuple[PilotIssue, ...] = (
    PilotIssue(
        issue_id="pilot-issue-001",
        severity="medium",
        status=PilotIssueStatus.ACCEPTED_RISK,
        owner_role="Product Owner",
        summary="Forecast KPI drill-down navigation improvement accepted after pilot.",
        sla_due_at=datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc),
    ),
)

PILOT_SHADOW_CHECKLIST: tuple[PilotShadowChecklistItem, ...] = (
    PilotShadowChecklistItem(
        item_id="pilot-source-coverage",
        owner_role="Data Platform Owner",
        status="ready",
        evidence="/data/ingestion/pilot-shadow-load/plan returns source coverage",
    ),
    PilotShadowChecklistItem(
        item_id="pilot-security-boundary",
        owner_role="Security Owner",
        status="ready",
        evidence="JWT/OIDC boundary and shared policy layer are enabled for stage",
    ),
    PilotShadowChecklistItem(
        item_id="pilot-process-package",
        owner_role="Process Owner",
        status="ready",
        evidence="/process-deployment/packages/current exposes BPMN/DMN/CMMN checksums",
    ),
    PilotShadowChecklistItem(
        item_id="pilot-business-kpi-baseline",
        owner_role="Business Owner",
        status="ready",
        evidence="WAPE, service level, lost sales and overstock KPIs defined",
    ),
)

PILOT_RUNBOOK: tuple[PilotRunbookStep, ...] = (
    PilotRunbookStep(step=1, owner_role="Data Engineer", action="Run source landing discovery", exit_criteria="All required contracts discovered or recovery tasks created"),
    PilotRunbookStep(step=2, owner_role="Data Owner", action="Resolve DQ blockers", exit_criteria="No blocker DQ incidents remain"),
    PilotRunbookStep(step=3, owner_role="Forecast Owner", action="Run forecast and compare WAPE", exit_criteria="WAPE does not exceed pilot threshold"),
    PilotRunbookStep(step=4, owner_role="Replenishment Owner", action="Review order proposals in shadow mode", exit_criteria="No critical order exceptions remain"),
    PilotRunbookStep(step=5, owner_role="Business Owner", action="Sign pilot go/no-go", exit_criteria="Acceptance or rollback decision recorded"),
)

PILOT_ROLLBACK: tuple[PilotRollbackAction, ...] = (
    PilotRollbackAction(trigger="critical_data_gap", action="Stop publication and run current legacy process", owner_role="Data Platform Owner", rto_minutes=30),
    PilotRollbackAction(trigger="wape_above_threshold", action="Keep OPEN FNR in shadow mode and activate forecast fallback", owner_role="Forecast Owner", rto_minutes=45),
    PilotRollbackAction(trigger="export_incident", action="Disable controlled exports and retry only after integration owner approval", owner_role="Integration Owner", rto_minutes=30),
)


def pilot_ready_for_acceptance(kpis: tuple[PilotKpi, ...], issues: tuple[PilotIssue, ...]) -> bool:
    kpis_ok = all(kpi.value <= kpi.threshold if kpi.name == "wape" else kpi.value >= kpi.threshold for kpi in kpis)
    blocking_issues = [issue for issue in issues if issue.severity == "critical" and issue.status != PilotIssueStatus.RESOLVED]
    return kpis_ok and not blocking_issues


def build_pilot_shadow_pack() -> PilotShadowPack:
    return PilotShadowPack(
        pack_id="pilot-shadow-pack-north-fresh-001",
        scope=PILOT_SCOPE,
        mode="shadow",
        business_dates=("2026-05-28", "2026-05-29", "2026-05-30"),
        checklist=PILOT_SHADOW_CHECKLIST,
        runbook=PILOT_RUNBOOK,
        rollback=PILOT_ROLLBACK,
        ready_for_shadow=all(item.status == "ready" for item in PILOT_SHADOW_CHECKLIST),
    )


@router.get("/scope")
def get_pilot_scope() -> dict[str, object]:
    return PILOT_SCOPE.model_dump(mode="json")


@router.get("/dashboard")
def get_pilot_dashboard() -> dict[str, object]:
    return {
        "scope": PILOT_SCOPE.model_dump(mode="json"),
        "kpis": [item.model_dump(mode="json") for item in PILOT_KPIS],
        "feedback": [item.model_dump(mode="json") for item in PILOT_FEEDBACK],
        "issues": [item.model_dump(mode="json") for item in PILOT_ISSUES],
        "ready_for_acceptance": pilot_ready_for_acceptance(PILOT_KPIS, PILOT_ISSUES),
    }


@router.get("/shadow-pack")
def get_pilot_shadow_pack() -> dict[str, object]:
    return build_pilot_shadow_pack().model_dump(mode="json")


@router.post("/acceptance/sign")
def sign_pilot_acceptance(payload: PilotAcceptanceRequest) -> dict[str, object]:
    if payload.actor_role != "Business Owner":
        raise HTTPException(status_code=403, detail="only Business Owner can sign pilot acceptance")
    if not pilot_ready_for_acceptance(PILOT_KPIS, PILOT_ISSUES):
        raise HTTPException(status_code=409, detail="pilot is not ready for acceptance")
    acceptance = PilotAcceptance(
        acceptance_id="pilot-acceptance-20260528-001",
        signed_by=payload.actor,
        signed_role=payload.actor_role,
        status=PilotStatus.ACCEPTED,
        decision=payload.decision,
        signed_at=datetime(2026, 5, 28, 16, 30, tzinfo=timezone.utc),
    )
    return acceptance.model_dump(mode="json")
