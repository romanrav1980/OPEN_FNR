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


class RollbackStep(BaseModel):
    step_id: str
    name: str
    owner_role: str
    command_or_action: str
    expected_evidence: str
    status: ChecklistStatus


class RollbackPlan(BaseModel):
    plan_id: str
    release_candidate_id: str
    trigger: str
    steps: tuple[RollbackStep, ...]
    decision_required_by: tuple[str, ...]
    ready: bool


class DrDrillEvidence(BaseModel):
    drill_id: str
    scope: str
    rpo_target: str
    rto_target: str
    restore_evidence: tuple[str, ...]
    degraded_mode: str
    status: ChecklistStatus


class DegradedModePlan(BaseModel):
    mode_id: str
    name: str
    allowed_capabilities: tuple[str, ...]
    blocked_capabilities: tuple[str, ...]
    activation_owner_role: str
    exit_criteria: tuple[str, ...]


CHECKLIST: tuple[ReleaseChecklistItem, ...] = (
    ReleaseChecklistItem(item_id="rel-001", area="full_regression", status=ChecklistStatus.PASSED, evidence="236 automated tests passed", owner_role="Product Owner"),
    ReleaseChecklistItem(item_id="rel-002", area="performance", status=ChecklistStatus.PASSED, evidence="Industrial projection within target", owner_role="Architecture"),
    ReleaseChecklistItem(item_id="rel-003", area="data", status=ChecklistStatus.PASSED, evidence="Industrial DQ gate pass", owner_role="Business Owners"),
    ReleaseChecklistItem(item_id="rel-004", area="dr_smoke", status=ChecklistStatus.PASSED, evidence="Backup/restore smoke accepted", owner_role="IT Ops"),
    ReleaseChecklistItem(item_id="rel-005", area="support_handover", status=ChecklistStatus.PASSED, evidence="Runbooks and incident roles assigned", owner_role="IT Ops"),
)

ROLLBACK_STEPS: tuple[RollbackStep, ...] = (
    RollbackStep(
        step_id="rollback-001",
        name="Freeze controlled exports",
        owner_role="IT Ops",
        command_or_action="activate configured publication stop switch",
        expected_evidence="publication packages remain queued and are not sent twice",
        status=ChecklistStatus.PASSED,
    ),
    RollbackStep(
        step_id="rollback-002",
        name="Restore previous application version",
        owner_role="Release Manager",
        command_or_action="redeploy previous approved image tag from release manifest",
        expected_evidence="health and ready probes pass on previous version",
        status=ChecklistStatus.PASSED,
    ),
    RollbackStep(
        step_id="rollback-003",
        name="Apply migration rollback or forward fix decision",
        owner_role="Architecture",
        command_or_action="execute approved migration recovery path from release notes",
        expected_evidence="schema compatibility check passes",
        status=ChecklistStatus.PASSED,
    ),
    RollbackStep(
        step_id="rollback-004",
        name="Run backup restore smoke evidence check",
        owner_role="DBA",
        command_or_action="validate latest backup manifest and restore-smoke output",
        expected_evidence="checksum and restore evidence are attached to release incident",
        status=ChecklistStatus.PASSED,
    ),
)

DR_DRILL = DrDrillEvidence(
    drill_id="drill-dep4-20260529",
    scope="application rollback plus PostgreSQL and ClickHouse restore smoke",
    rpo_target="latest committed business event before release window",
    rto_target="restore critical review mode before business order approval window",
    restore_evidence=(
        "backup manifest checksum verified",
        "PostgreSQL restore-smoke database validated",
        "ClickHouse restore-smoke topology decision recorded",
        "publication exports remain stopped until reconciliation passes",
    ),
    degraded_mode="shadow_review_only",
    status=ChecklistStatus.PASSED,
)

DEGRADED_MODES: tuple[DegradedModePlan, ...] = (
    DegradedModePlan(
        mode_id="shadow_review_only",
        name="Shadow review only",
        allowed_capabilities=("data ingestion review", "forecast review", "replenishment review", "BI read-only"),
        blocked_capabilities=("ERP export", "auto-order export", "bulk approval", "supplier publication"),
        activation_owner_role="Incident Manager",
        exit_criteria=("root cause fixed", "reconciliation passed", "release manager approves export resume"),
    ),
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


def build_rollback_plan() -> RollbackPlan:
    return RollbackPlan(
        plan_id="rollback-open-fnr-industrial-rc1",
        release_candidate_id="open-fnr-industrial-rc1",
        trigger="sev1_or_sev2_after_release_or_failed_migration_gate",
        steps=ROLLBACK_STEPS,
        decision_required_by=("Release Manager", "IT Ops", "Architecture", "Incident Manager"),
        ready=all(item.status != ChecklistStatus.FAILED for item in ROLLBACK_STEPS),
    )


@router.get("/candidate")
def get_release_candidate() -> dict[str, object]:
    return build_release_candidate().model_dump(mode="json")


@router.get("/rollback-plan")
def get_rollback_plan() -> dict[str, object]:
    return build_rollback_plan().model_dump(mode="json")


@router.get("/dr-drill")
def get_dr_drill() -> dict[str, object]:
    return DR_DRILL.model_dump(mode="json")


@router.get("/degraded-modes")
def get_degraded_modes() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in DEGRADED_MODES], "total": len(DEGRADED_MODES)}


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
