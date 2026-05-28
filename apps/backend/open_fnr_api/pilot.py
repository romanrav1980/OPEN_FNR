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


def pilot_ready_for_acceptance(kpis: tuple[PilotKpi, ...], issues: tuple[PilotIssue, ...]) -> bool:
    kpis_ok = all(kpi.value <= kpi.threshold if kpi.name == "wape" else kpi.value >= kpi.threshold for kpi in kpis)
    blocking_issues = [issue for issue in issues if issue.severity == "critical" and issue.status != PilotIssueStatus.RESOLVED]
    return kpis_ok and not blocking_issues


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
