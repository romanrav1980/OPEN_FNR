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
    store_count: int
    sku_count: int
    categories: tuple[str, ...]
    suppliers: tuple[str, ...] = ()
    users: tuple[str, ...]
    status: PilotStatus


class PilotScopeSignoff(BaseModel):
    signoff_id: str
    scope_id: str
    signed_roles: tuple[str, ...]
    pending_roles: tuple[str, ...]
    status: str
    signed_at: datetime | None


class PilotDataReadinessItem(BaseModel):
    area: str
    status: str
    coverage_percent: float = Field(ge=0, le=100)
    history_months: int | None = Field(default=None, ge=0)
    evidence: str
    blocker_count: int = Field(ge=0)


class PilotBusinessCalendarDay(BaseModel):
    business_date: str
    day_type: str
    notes: str


class PilotAcceptanceThreshold(BaseModel):
    metric: str
    threshold: float
    unit: str
    direction: str
    owner_role: str


class PilotReadinessPack(BaseModel):
    scope: PilotScope
    signoff: PilotScopeSignoff
    data_readiness: tuple[PilotDataReadinessItem, ...]
    business_calendar: tuple[PilotBusinessCalendarDay, ...]
    thresholds: tuple[PilotAcceptanceThreshold, ...]
    ready_for_shadow_mode: bool


class PilotShadowMetric(BaseModel):
    metric: str
    open_fnr_value: float
    legacy_value: float
    unit: str
    status: str


class PilotShadowException(BaseModel):
    exception_id: str
    store_id: str
    sku_id: str
    reason: str
    recommended_action: str
    owner_role: str


class PilotShadowRun(BaseModel):
    run_id: str
    business_date: str
    mode: str
    export_enabled: bool
    compared_orders: int
    metrics: tuple[PilotShadowMetric, ...]
    exceptions: tuple[PilotShadowException, ...]
    planner_actions: tuple[str, ...]
    status: str
    ready_for_business_review: bool


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
    store_count=3,
    sku_count=1200,
    categories=("fresh", "grocery"),
    suppliers=("SUP-FRESH-01", "SUP-GROCERY-02"),
    users=("forecast.planner@example.org", "supply.manager@example.org", "business.owner@example.org"),
    status=PilotStatus.ACCEPTANCE_PENDING,
)

PILOT_SCOPE_SIGNOFF = PilotScopeSignoff(
    signoff_id="pilot-scope-signoff-20260529-001",
    scope_id=PILOT_SCOPE.scope_id,
    signed_roles=("Business Owner", "Supply Chain Director", "Data Platform Lead", "IT Ops"),
    pending_roles=(),
    status="signed",
    signed_at=datetime(2026, 5, 29, 9, 0, tzinfo=timezone.utc),
)

PILOT_DATA_READINESS: tuple[PilotDataReadinessItem, ...] = (
    PilotDataReadinessItem(
        area="sales_history",
        status="ready",
        coverage_percent=99.4,
        history_months=24,
        evidence="POS and DWH history available for pilot scope",
        blocker_count=0,
    ),
    PilotDataReadinessItem(
        area="stock_and_in_transit",
        status="ready",
        coverage_percent=98.7,
        history_months=None,
        evidence="WMS stock, in-transit and open-order contracts are ready",
        blocker_count=0,
    ),
    PilotDataReadinessItem(
        area="active_matrix",
        status="ready",
        coverage_percent=100.0,
        history_months=None,
        evidence="Pilot SKU/store active matrix is frozen",
        blocker_count=0,
    ),
    PilotDataReadinessItem(
        area="promo_history",
        status="ready",
        coverage_percent=96.8,
        history_months=18,
        evidence="Promo plan and promo facts are available for pilot categories",
        blocker_count=0,
    ),
)

PILOT_BUSINESS_CALENDAR: tuple[PilotBusinessCalendarDay, ...] = (
    PilotBusinessCalendarDay(business_date="2026-06-01", day_type="pilot_start", notes="Shadow mode starts"),
    PilotBusinessCalendarDay(business_date="2026-06-14", day_type="shadow_gate", notes="Minimum shadow evidence window complete"),
    PilotBusinessCalendarDay(business_date="2026-06-15", day_type="controlled_export_gate", notes="Controlled export decision point"),
)

PILOT_ACCEPTANCE_THRESHOLDS: tuple[PilotAcceptanceThreshold, ...] = (
    PilotAcceptanceThreshold(metric="wape", threshold=18.0, unit="%", direction="less_or_equal", owner_role="DS Lead"),
    PilotAcceptanceThreshold(metric="service_level", threshold=95.0, unit="%", direction="greater_or_equal", owner_role="Supply Chain Director"),
    PilotAcceptanceThreshold(metric="lost_sales_reduction", threshold=3.0, unit="pp", direction="greater_or_equal", owner_role="Commercial Director"),
    PilotAcceptanceThreshold(metric="overstock_reduction", threshold=2.0, unit="pp", direction="greater_or_equal", owner_role="Supply Chain Director"),
    PilotAcceptanceThreshold(metric="waste_reduction", threshold=1.5, unit="pp", direction="greater_or_equal", owner_role="Fresh Category Manager"),
)

PILOT_SHADOW_RUNS: tuple[PilotShadowRun, ...] = (
    PilotShadowRun(
        run_id="shadow-run-20260601-001",
        business_date="2026-06-01",
        mode="shadow",
        export_enabled=False,
        compared_orders=18420,
        metrics=(
            PilotShadowMetric(metric="wape", open_fnr_value=16.9, legacy_value=19.4, unit="%", status="green"),
            PilotShadowMetric(metric="bias", open_fnr_value=-0.7, legacy_value=-2.8, unit="%", status="green"),
            PilotShadowMetric(metric="service_level_proxy", open_fnr_value=95.8, legacy_value=94.6, unit="%", status="green"),
            PilotShadowMetric(metric="order_quantity_delta_abs", open_fnr_value=4.2, legacy_value=0.0, unit="%", status="amber"),
        ),
        exceptions=(
            PilotShadowException(
                exception_id="shadow-exc-001",
                store_id="S002",
                sku_id="SKU-FRESH-0007",
                reason="legacy order is lower than projected demand and presentation stock",
                recommended_action="planner review before controlled export gate",
                owner_role="Replenishment Owner",
            ),
        ),
        planner_actions=("review amber order deltas", "confirm fresh exceptions", "record business feedback"),
        status="business_review",
        ready_for_business_review=True,
    ),
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


def build_pilot_readiness_pack() -> PilotReadinessPack:
    ready = (
        PILOT_SCOPE_SIGNOFF.status == "signed"
        and not PILOT_SCOPE_SIGNOFF.pending_roles
        and all(item.status == "ready" and item.blocker_count == 0 for item in PILOT_DATA_READINESS)
        and all(item.history_months is None or item.history_months >= 12 for item in PILOT_DATA_READINESS)
    )
    return PilotReadinessPack(
        scope=PILOT_SCOPE,
        signoff=PILOT_SCOPE_SIGNOFF,
        data_readiness=PILOT_DATA_READINESS,
        business_calendar=PILOT_BUSINESS_CALENDAR,
        thresholds=PILOT_ACCEPTANCE_THRESHOLDS,
        ready_for_shadow_mode=ready,
    )


def build_shadow_mode_summary() -> dict[str, object]:
    runs = list(PILOT_SHADOW_RUNS)
    green_metric_count = sum(1 for run in runs for metric in run.metrics if metric.status == "green")
    amber_metric_count = sum(1 for run in runs for metric in run.metrics if metric.status == "amber")
    return {
        "mode": "shadow",
        "export_enabled": False,
        "run_count": len(runs),
        "green_metric_count": green_metric_count,
        "amber_metric_count": amber_metric_count,
        "ready_for_business_review": all(run.ready_for_business_review for run in runs),
        "runs": [run.model_dump(mode="json") for run in runs],
    }


@router.get("/scope")
def get_pilot_scope() -> dict[str, object]:
    return PILOT_SCOPE.model_dump(mode="json")


@router.get("/scope-signoff")
def get_pilot_scope_signoff() -> dict[str, object]:
    return PILOT_SCOPE_SIGNOFF.model_dump(mode="json")


@router.get("/data-readiness")
def get_pilot_data_readiness() -> dict[str, object]:
    pack = build_pilot_readiness_pack()
    return {
        "scope_id": pack.scope.scope_id,
        "items": [item.model_dump(mode="json") for item in pack.data_readiness],
        "business_calendar": [item.model_dump(mode="json") for item in pack.business_calendar],
        "thresholds": [item.model_dump(mode="json") for item in pack.thresholds],
        "ready_for_shadow_mode": pack.ready_for_shadow_mode,
    }


@router.get("/readiness-pack")
def get_pilot_readiness_pack() -> dict[str, object]:
    return build_pilot_readiness_pack().model_dump(mode="json")


@router.get("/shadow-runs")
def list_pilot_shadow_runs() -> dict[str, object]:
    return build_shadow_mode_summary()


@router.get("/shadow-runs/{run_id}")
def get_pilot_shadow_run(run_id: str) -> dict[str, object]:
    run = next((item for item in PILOT_SHADOW_RUNS if item.run_id == run_id), None)
    if run is None:
        raise HTTPException(status_code=404, detail="shadow run not found")
    return run.model_dump(mode="json")


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
