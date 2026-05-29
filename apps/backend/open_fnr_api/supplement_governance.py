from __future__ import annotations

from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .config import settings


router = APIRouter(prefix="/supplement", tags=["supplement-governance"])


class GateStatus(StrEnum):
    READY = "ready"
    BLOCKED = "blocked"
    GOVERNED = "governed"
    OUT_OF_SCOPE = "out_of_scope"


class SourceSlaRule(BaseModel):
    source_system: str
    dataset: str
    target_sla: str
    cutoff_time: str
    completeness_threshold: float | None = Field(default=None, ge=0, le=1)
    degradation_mode: str
    owner_role: str


class SourceSlaEvaluationRequest(BaseModel):
    source_system: str
    dataset: str
    completeness: float = Field(ge=0, le=1)
    arrived_before_cutoff: bool


class SourceSlaEvaluation(BaseModel):
    source_system: str
    dataset: str
    status: GateStatus
    quality_flag: str
    publish_allowed_by_default: bool
    action: str


class MlLifecycleGate(BaseModel):
    stages: tuple[str, ...]
    candidate_min_backtesting_weeks: int
    candidate_bias_abs_threshold_pct: float
    candidate_wape_improvement_pp: float
    shadow_min_days: int
    fallback_chain: tuple[str, ...]
    emergency_rollback_hours: int


class ReplenishmentFinancialParameter(BaseModel):
    parameter: str
    owner_role: str
    required_before: str
    default_policy: str


class BusinessAcceptanceGate(BaseModel):
    phase: str
    min_duration: str
    required_evidence: tuple[str, ...]
    sign_off_roles: tuple[str, ...]


class DataGovernanceSupplement(BaseModel):
    lineage_required: bool
    retention: dict[str, str]
    ownership_domains: tuple[str, ...]


class ApiGovernancePolicy(BaseModel):
    version_prefix: str
    deprecation_notice_days: int
    emergency_deprecation_days: int
    consumer_registry_path: str
    error_registry_path: str
    standard_error_fields: tuple[str, ...]


class SupplierIsolationPolicy(BaseModel):
    supplier_api_prefix: str
    required_claim: str
    controls: tuple[str, ...]
    data_class: str


class ScopeDecision(BaseModel):
    topic: str
    v1_status: GateStatus
    rationale: str
    v1_compensating_controls: tuple[str, ...]
    v2_requirements: tuple[str, ...]


class HistoricalSimulationRequirement(BaseModel):
    min_weeks: int
    min_store_coverage_pct: float
    min_category_turnover_coverage_pct: float
    required_report_path: str
    metrics: tuple[str, ...]


class NotificationRule(BaseModel):
    notification_type: str
    channel: str
    max_delivery_minutes: int
    recipient_role: str


class HumanTaskSla(BaseModel):
    task_type: str
    sla: str
    escalation_role: str


class ItsmReadiness(BaseModel):
    status: GateStatus
    webhook_configured: bool
    target_setting: str
    v1_1_events: tuple[str, ...]


class OpenQuestion(BaseModel):
    question_id: str
    topic: str
    owner_role: str
    deadline_gate: str


class SupplementCoverageReport(BaseModel):
    supplement_document: str
    sections: tuple[str, ...]
    implemented_gates: tuple[str, ...]
    docs_to_sync: tuple[str, ...]


SOURCE_SLA_RULES: tuple[SourceSlaRule, ...] = (
    SourceSlaRule(source_system="POS", dataset="sales", target_sla="D+1 06:00", cutoff_time="D+1 07:00", completeness_threshold=0.95, degradation_mode="data_gap", owner_role="Data Engineer"),
    SourceSlaRule(source_system="WMS", dataset="store_stock", target_sla="D+1 07:00", cutoff_time="D+1 08:00", completeness_threshold=0.90, degradation_mode="stale_stock", owner_role="WMS Data Owner"),
    SourceSlaRule(source_system="WMS", dataset="open_orders", target_sla="D+1 07:00", cutoff_time="D+1 08:00", completeness_threshold=0.85, degradation_mode="last_successful_batch", owner_role="WMS Data Owner"),
    SourceSlaRule(source_system="WMS", dataset="in_transit", target_sla="D+1 07:00", cutoff_time="D+1 08:00", completeness_threshold=0.80, degradation_mode="last_successful_batch", owner_role="WMS Data Owner"),
    SourceSlaRule(source_system="ERP", dataset="prices_discounts", target_sla="D+0 21:00", cutoff_time="D+0 23:00", completeness_threshold=1.0, degradation_mode="last_known_prices", owner_role="ERP Data Owner"),
    SourceSlaRule(source_system="ERP", dataset="order_statuses", target_sla="D+1 07:30", cutoff_time="D+1 08:30", completeness_threshold=0.90, degradation_mode="previous_batch", owner_role="ERP Data Owner"),
    SourceSlaRule(source_system="PROMO", dataset="promo_plan_90d", target_sla="weekly Sunday 20:00", cutoff_time="Sunday 22:00", completeness_threshold=0.99, degradation_mode="last_versioned_plan", owner_role="Promo Planner"),
    SourceSlaRule(source_system="MDM", dataset="products", target_sla="D+0 20:00", cutoff_time="D+0 23:00", completeness_threshold=1.0, degradation_mode="last_successful_mdm_version", owner_role="MDM Data Owner"),
    SourceSlaRule(source_system="MDM", dataset="stores", target_sla="D+0 20:00", cutoff_time="D+0 23:00", completeness_threshold=1.0, degradation_mode="last_successful_mdm_version", owner_role="MDM Data Owner"),
    SourceSlaRule(source_system="EXTERNAL", dataset="weather_events_14d", target_sla="D+0 22:00", cutoff_time="D+1 00:00", completeness_threshold=None, degradation_mode="no_external_features", owner_role="External Data Owner"),
)

ML_LIFECYCLE_GATE = MlLifecycleGate(
    stages=("EXPERIMENT", "CANDIDATE", "SHADOW", "CHALLENGER", "CHAMPION", "RETIRED"),
    candidate_min_backtesting_weeks=26,
    candidate_bias_abs_threshold_pct=5.0,
    candidate_wape_improvement_pp=0.5,
    shadow_min_days=14,
    fallback_chain=("champion", "previous_champion", "category_median_28d", "store_rolling_median_28d", "global_seasonal_naive"),
    emergency_rollback_hours=1,
)

FINANCIAL_PARAMETERS: tuple[ReplenishmentFinancialParameter, ...] = (
    ReplenishmentFinancialParameter(parameter="holding_cost_rate_annual", owner_role="CFO", required_before="Controlled Pilot", default_policy="blocked_until_signed"),
    ReplenishmentFinancialParameter(parameter="lost_sales_margin_rate", owner_role="Commercial Director", required_before="Parallel Run", default_policy="gross_margin_rate_until_signed"),
    ReplenishmentFinancialParameter(parameter="waste_cost_per_unit_or_rate", owner_role="Fresh Category Owner", required_before="Parallel Run", default_policy="category_config_required"),
    ReplenishmentFinancialParameter(parameter="service_level_targets_by_segment", owner_role="Commercial Director + SC Director", required_before="Parallel Run", default_policy="blocked_until_signed"),
)

BUSINESS_ACCEPTANCE_GATES: tuple[BusinessAcceptanceGate, ...] = (
    BusinessAcceptanceGate(phase="Shadow Mode", min_duration="14 calendar days", required_evidence=("forecast_shadow", "shadow_report", "no_critical_incidents"), sign_off_roles=("DS Lead", "SC Director")),
    BusinessAcceptanceGate(phase="Parallel Run", min_duration="6 weeks including 1 promo cycle", required_evidence=("historical_simulation_report", "matched_pairs", "business_kpi_report"), sign_off_roles=("Commercial Director", "SC Director", "IT Director")),
    BusinessAcceptanceGate(phase="Controlled Pilot", min_duration="agreed pilot window", required_evidence=("signed_kpi_thresholds", "rollback_plan", "audit_report"), sign_off_roles=("Business Owner", "IT Director")),
)

NOTIFICATION_RULES: tuple[NotificationRule, ...] = (
    NotificationRule(notification_type="source_sla_breach", channel="email+in_app", max_delivery_minutes=5, recipient_role="Data Engineer + Source Owner"),
    NotificationRule(notification_type="critical_exception", channel="process_inbox+email", max_delivery_minutes=15, recipient_role="Planner"),
    NotificationRule(notification_type="p1_calculation_failed", channel="email+sms_or_telegram", max_delivery_minutes=5, recipient_role="DE On-call + IT Director"),
    NotificationRule(notification_type="human_task_created", channel="in_app+email", max_delivery_minutes=10, recipient_role="Assigned Role"),
)

HUMAN_TASK_SLAS: tuple[HumanTaskSla, ...] = (
    HumanTaskSla(task_type="standard_order_proposal_approval", sla="8 business hours", escalation_role="Supervisor"),
    HumanTaskSla(task_type="urgent_promo_order_proposal_approval", sla="2 business hours", escalation_role="SC Director"),
    HumanTaskSla(task_type="promo_approval", sla="24 hours", escalation_role="Category Director"),
    HumanTaskSla(task_type="dq_incident", sla="4 business hours", escalation_role="DS Lead"),
    HumanTaskSla(task_type="fresh_order_review", sla="1 business hour", escalation_role="Supervisor"),
)

OPEN_QUESTIONS: tuple[OpenQuestion, ...] = (
    OpenQuestion(question_id="M-01", topic="Service level targets by segment", owner_role="Commercial Director + SC Director", deadline_gate="Parallel Run"),
    OpenQuestion(question_id="M-02", topic="holding_cost_rate_annual", owner_role="CFO", deadline_gate="Controlled Pilot"),
    OpenQuestion(question_id="M-03", topic="lost_sales_margin_rate by category", owner_role="Commercial Director", deadline_gate="Parallel Run"),
    OpenQuestion(question_id="M-04", topic="Pilot KPI thresholds", owner_role="Commercial Director + SC Director", deadline_gate="Parallel Run"),
    OpenQuestion(question_id="M-05", topic="Matched-pairs control group", owner_role="SC Director + Analytics", deadline_gate="Parallel Run"),
    OpenQuestion(question_id="M-06", topic="Historical simulation categories", owner_role="Commercial Director", deadline_gate="Shadow Mode"),
    OpenQuestion(question_id="M-07", topic="Signed Data SLA Agreements", owner_role="IT Director + Source Owners", deadline_gate="Shadow Mode"),
    OpenQuestion(question_id="M-08", topic="Supplier data sharing classification", owner_role="IT Director + Procurement", deadline_gate="Supplier Collaboration"),
    OpenQuestion(question_id="M-09", topic="Planner notification channels", owner_role="IT Director", deadline_gate="Parallel Run"),
    OpenQuestion(question_id="M-10", topic="ITSM integration system and credentials", owner_role="IT Director", deadline_gate="v1.1"),
    OpenQuestion(question_id="M-11", topic="OTB budget source system", owner_role="CFO + IT", deadline_gate="v2"),
    OpenQuestion(question_id="M-12", topic="Target WAPE acceptance thresholds", owner_role="DS Lead + Commercial Director", deadline_gate="Parallel Run"),
)


def find_source_sla_rule(source_system: str, dataset: str) -> SourceSlaRule:
    for rule in SOURCE_SLA_RULES:
        if rule.source_system == source_system and rule.dataset == dataset:
            return rule
    raise HTTPException(status_code=404, detail="source SLA rule not found")


@router.get("/coverage", response_model=SupplementCoverageReport)
def get_supplement_coverage() -> SupplementCoverageReport:
    return SupplementCoverageReport(
        supplement_document="TECHNICAL_SPEC_SUPPLEMENT_1.md",
        sections=tuple(f"Section {letter}" for letter in "ABCDEFGHIJKLM"),
        implemented_gates=(
            "source_sla",
            "ml_lifecycle",
            "financial_replenishment_parameters",
            "business_acceptance",
            "dr_bc_lineage",
            "api_versioning_deprecation",
            "supplier_isolation",
            "intraday_scope",
            "historical_simulation",
            "notifications_itsm",
            "otb_scope",
            "open_questions",
        ),
        docs_to_sync=(
            "TECHNICAL_SPEC.md",
            "PROJECT_CHARTER.md",
            "DATA_GOVERNANCE.md",
            "ML_GOVERNANCE.md",
            "REAL_DATA_INGESTION_PIPELINES.md",
            "PILOT_LAUNCH_PLAN.md",
            "INTEGRATION_STRATEGY.md",
            "SECURITY_STRATEGY.md",
            "TESTING_STRATEGY.md",
        ),
    )


@router.get("/source-sla", response_model=tuple[SourceSlaRule, ...])
def list_source_sla_rules() -> tuple[SourceSlaRule, ...]:
    return SOURCE_SLA_RULES


@router.post("/source-sla/evaluate", response_model=SourceSlaEvaluation)
def evaluate_source_sla(request: SourceSlaEvaluationRequest) -> SourceSlaEvaluation:
    rule = find_source_sla_rule(request.source_system, request.dataset)
    threshold_ok = rule.completeness_threshold is None or request.completeness >= rule.completeness_threshold
    if request.arrived_before_cutoff and threshold_ok:
        return SourceSlaEvaluation(source_system=rule.source_system, dataset=rule.dataset, status=GateStatus.READY, quality_flag="ok", publish_allowed_by_default=True, action="start_pipeline")
    return SourceSlaEvaluation(source_system=rule.source_system, dataset=rule.dataset, status=GateStatus.BLOCKED, quality_flag="degraded", publish_allowed_by_default=False, action=f"use_{rule.degradation_mode}_and_open_process_incident")


@router.get("/ml-lifecycle", response_model=MlLifecycleGate)
def get_ml_lifecycle_gate() -> MlLifecycleGate:
    return ML_LIFECYCLE_GATE


@router.get("/replenishment-financial-parameters", response_model=tuple[ReplenishmentFinancialParameter, ...])
def list_replenishment_financial_parameters() -> tuple[ReplenishmentFinancialParameter, ...]:
    return FINANCIAL_PARAMETERS


@router.get("/business-acceptance", response_model=tuple[BusinessAcceptanceGate, ...])
def list_business_acceptance_gates() -> tuple[BusinessAcceptanceGate, ...]:
    return BUSINESS_ACCEPTANCE_GATES


@router.get("/data-governance", response_model=DataGovernanceSupplement)
def get_data_governance_supplement() -> DataGovernanceSupplement:
    return DataGovernanceSupplement(
        lineage_required=True,
        retention={
            "raw_pos_sales": "5 years",
            "clean_sales": "5 years",
            "detailed_forecasts": "2 years, last 5 versions per day",
            "order_proposals": "3 years",
            "audit_log": "5 years",
            "ml_model_artifacts": "forever, retired at least 3 years",
            "bpmn_dmn_cmmn": "forever",
            "prometheus_metrics": "1 year detailed, 5 years aggregated",
        },
        ownership_domains=("sales", "stock", "prices", "promo", "mdm_products", "mdm_stores", "supplier_terms", "forecasts", "order_proposals", "audit_log", "ml_models", "business_rules"),
    )


@router.get("/api-governance", response_model=ApiGovernancePolicy)
def get_api_governance_policy() -> ApiGovernancePolicy:
    return ApiGovernancePolicy(
        version_prefix="/api/v{major}/",
        deprecation_notice_days=90,
        emergency_deprecation_days=7,
        consumer_registry_path="docs/api-consumers/registry.md",
        error_registry_path="docs/api-errors/registry.md",
        standard_error_fields=("error_code", "message", "request_id", "timestamp", "docs_url"),
    )


@router.get("/supplier-isolation", response_model=SupplierIsolationPolicy)
def get_supplier_isolation_policy() -> SupplierIsolationPolicy:
    return SupplierIsolationPolicy(
        supplier_api_prefix="/supplier-api/v1/",
        required_claim="supplier_id",
        controls=("jwt_supplier_scope", "row_level_api_filtering", "no_cross_supplier_inference", "service_account_scopes", "audit_every_supplier_request"),
        data_class="C3 Confidential",
    )


@router.get("/scope/intraday", response_model=ScopeDecision)
def get_intraday_scope_decision() -> ScopeDecision:
    return ScopeDecision(
        topic="Intraday and demand sensing",
        v1_status=GateStatus.OUT_OF_SCOPE,
        rationale="v1 is daily batch; streaming ingestion and online inference are v2 architecture.",
        v1_compensating_controls=("fresh_early_cutoff", "fresh_intraday_alert_without_reforecast", "morning_fresh_priority_batch"),
        v2_requirements=("streaming_ingestion", "online_feature_store", "intraday_replenishment_trigger", "dark_store_ecommerce_priority"),
    )


@router.get("/historical-simulation", response_model=HistoricalSimulationRequirement)
def get_historical_simulation_requirement() -> HistoricalSimulationRequirement:
    return HistoricalSimulationRequirement(
        min_weeks=52,
        min_store_coverage_pct=20.0,
        min_category_turnover_coverage_pct=50.0,
        required_report_path="docs/simulation-reports/",
        metrics=("simulated_oos_rate", "simulated_overstock", "simulated_waste_fresh", "proposal_vs_actual_delta"),
    )


@router.get("/notifications", response_model=tuple[NotificationRule, ...])
def list_notification_rules() -> tuple[NotificationRule, ...]:
    return NOTIFICATION_RULES


@router.get("/human-task-sla", response_model=tuple[HumanTaskSla, ...])
def list_human_task_slas() -> tuple[HumanTaskSla, ...]:
    return HUMAN_TASK_SLAS


@router.get("/itsm-readiness", response_model=ItsmReadiness)
def get_itsm_readiness() -> ItsmReadiness:
    return ItsmReadiness(
        status=GateStatus.READY if settings.itsm_webhook_url else GateStatus.OUT_OF_SCOPE,
        webhook_configured=bool(settings.itsm_webhook_url),
        target_setting="OPEN_FNR_ITSM_WEBHOOK_URL",
        v1_1_events=("p1_calculation_failed", "source_sla_breach_2_days", "dmn_change_request", "supplier_onboarding_request"),
    )


@router.get("/scope/otb", response_model=ScopeDecision)
def get_otb_scope_decision() -> ScopeDecision:
    return ScopeDecision(
        topic="Open-to-Buy and seasonal budget integration",
        v1_status=GateStatus.OUT_OF_SCOPE,
        rationale="v1 creates order proposals without top-down budget constraints; category manager applies budget limits manually.",
        v1_compensating_controls=("seasonal_90_day_horizon", "max_stock_selling_days_parameter", "termination_date_lifecycle_workflow", "category_manager_budget_responsibility"),
        v2_requirements=("otb_constraint_input", "budget_aware_order_shaping", "budget_utilization_view", "seasonal_buy_integration", "markdown_recommendation"),
    )


@router.get("/open-questions", response_model=tuple[OpenQuestion, ...])
def list_open_questions() -> tuple[OpenQuestion, ...]:
    return OPEN_QUESTIONS
