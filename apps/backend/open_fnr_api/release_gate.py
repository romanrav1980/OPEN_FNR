from datetime import datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/release-gate", tags=["release-gate"])


class ReleaseDecision(StrEnum):
    GO = "go"
    NO_GO = "no_go"
    CONDITIONAL_GO = "conditional_go"


class ChecklistStatus(StrEnum):
    PASSED = "passed"
    ACCEPTED_RISK = "accepted_risk"
    FAILED = "failed"


class ReleaseChecklistItem(BaseModel):
    item_id: str
    area: str
    status: ChecklistStatus
    evidence: str
    owner_role: str


class ReleaseRisk(BaseModel):
    risk_id: str
    severity: str
    summary: str
    accepted_by: str | None
    status: ChecklistStatus


class ReleaseCandidate(BaseModel):
    candidate_id: str
    version: str
    checklist: tuple[ReleaseChecklistItem, ...]
    risks: tuple[ReleaseRisk, ...]
    critical_defects: int = Field(ge=0)
    decision: ReleaseDecision
    decided_at: datetime | None


class ReleaseApprovalRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    decision: ReleaseDecision
    comment: str = Field(min_length=1)


CHECKLIST: tuple[ReleaseChecklistItem, ...] = (
    ReleaseChecklistItem(item_id="rel-001", area="full_regression", status=ChecklistStatus.PASSED, evidence="236 automated tests passed", owner_role="Product Owner"),
    ReleaseChecklistItem(item_id="rel-002", area="performance", status=ChecklistStatus.PASSED, evidence="Industrial projection within target", owner_role="Architecture"),
    ReleaseChecklistItem(item_id="rel-003", area="data", status=ChecklistStatus.PASSED, evidence="Industrial DQ gate pass", owner_role="Business Owners"),
    ReleaseChecklistItem(item_id="rel-004", area="dr_smoke", status=ChecklistStatus.PASSED, evidence="Backup/restore smoke accepted", owner_role="IT Ops"),
    ReleaseChecklistItem(item_id="rel-005", area="support_handover", status=ChecklistStatus.PASSED, evidence="Runbooks and incident roles assigned", owner_role="IT Ops"),
)

RISKS: tuple[ReleaseRisk, ...] = (
    ReleaseRisk(
        risk_id="risk-20260528-001",
        severity="medium",
        summary="KPI drill-down navigation improvement deferred after pilot.",
        accepted_by="business.owner@example.org",
        status=ChecklistStatus.ACCEPTED_RISK,
    ),
)


def release_readiness_decision(checklist: tuple[ReleaseChecklistItem, ...], risks: tuple[ReleaseRisk, ...], critical_defects: int) -> ReleaseDecision:
    if critical_defects > 0 or any(item.status == ChecklistStatus.FAILED for item in checklist):
        return ReleaseDecision.NO_GO
    if any(risk.status == ChecklistStatus.ACCEPTED_RISK for risk in risks):
        return ReleaseDecision.CONDITIONAL_GO
    return ReleaseDecision.GO


def build_release_candidate() -> ReleaseCandidate:
    decision = release_readiness_decision(CHECKLIST, RISKS, critical_defects=0)
    return ReleaseCandidate(
        candidate_id="open-fnr-industrial-rc1",
        version="0.30.0-rc1",
        checklist=CHECKLIST,
        risks=RISKS,
        critical_defects=0,
        decision=decision,
        decided_at=None,
    )


@router.get("/candidate")
def get_release_candidate() -> dict[str, object]:
    return build_release_candidate().model_dump(mode="json")


@router.post("/candidate/approve")
def approve_release_candidate(payload: ReleaseApprovalRequest) -> dict[str, object]:
    allowed_roles = {"Product Owner", "Architecture", "Business Owners", "IT Ops"}
    if payload.actor_role not in allowed_roles:
        raise HTTPException(status_code=403, detail="release approval role required")
    candidate = build_release_candidate()
    if payload.decision == ReleaseDecision.GO and candidate.decision == ReleaseDecision.NO_GO:
        raise HTTPException(status_code=409, detail="release candidate is not ready")
    approved = candidate.model_copy(update={"decision": payload.decision, "decided_at": datetime(2026, 5, 28, 22, 0, tzinfo=timezone.utc)})
    return approved.model_dump(mode="json")
