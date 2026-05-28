from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field

from .data_contracts import DataDomain, DqSeverity
from .shadow_load import ShadowLoadContractResult, ShadowLoadReport, run_shadow_load_discovery


class DqDimension(StrEnum):
    COMPLETENESS = "completeness"
    UNIQUENESS = "uniqueness"
    VALIDITY = "validity"
    REFERENTIAL_INTEGRITY = "referential_integrity"
    FRESHNESS = "freshness"


class DqIncidentStatus(StrEnum):
    NEW = "new"
    IN_REVIEW = "in_review"
    FIXED = "fixed"
    WAIVED = "waived"
    BLOCKING = "blocking"
    CLOSED = "closed"


class DqRule(BaseModel):
    rule_id: str = Field(min_length=1, max_length=128)
    domain: DataDomain
    dimension: DqDimension
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=1024)
    severity: DqSeverity
    blocking: bool
    owner_role: str = Field(min_length=1, max_length=64)


class SourceContractDqPlan(BaseModel):
    source_system: str = Field(min_length=1, max_length=64)
    contract_name: str = Field(min_length=1, max_length=128)
    blocking_rules: tuple[str, ...]
    warning_rules: tuple[str, ...] = ()
    owner_role: str = Field(min_length=1, max_length=64)


class DqIncident(BaseModel):
    incident_id: str = Field(min_length=1, max_length=128)
    rule_id: str = Field(min_length=1, max_length=128)
    batch_id: str = Field(min_length=1, max_length=128)
    domain: DataDomain
    business_date: date
    severity: DqSeverity
    status: DqIncidentStatus
    blocking: bool
    affected_rows: int = Field(ge=0)
    affected_scope: str = Field(min_length=1, max_length=512)
    message: str = Field(min_length=1, max_length=1024)
    created_at: datetime
    owner_role: str = Field(min_length=1, max_length=64)
    waiver_reason: str | None = Field(default=None, max_length=512)


class DqWaiverRequest(BaseModel):
    reason: str = Field(min_length=10, max_length=512)
    approver_role: str = Field(min_length=1, max_length=64)


class SourceContractDqCheckResult(BaseModel):
    source_system: str
    contract_name: str
    status: str
    severity: DqSeverity
    blocking_rules_checked: tuple[str, ...]
    warning_rules_checked: tuple[str, ...]
    blocker_count: int = Field(ge=0)
    warning_count: int = Field(ge=0)
    message: str


class SourceContractDqRunRequest(BaseModel):
    business_date: date
    landing_root_path: str | None = Field(default=None, max_length=512)


class SourceContractDqRunResponse(BaseModel):
    business_date: date
    status: str
    total_contracts: int = Field(ge=0)
    blocker_count: int = Field(ge=0)
    warning_count: int = Field(ge=0)
    results: tuple[SourceContractDqCheckResult, ...]


router = APIRouter(prefix="/data-quality", tags=["data-quality"])


RULES: tuple[DqRule, ...] = (
    DqRule(
        rule_id="sales_required_keys",
        domain=DataDomain.SALES,
        dimension=DqDimension.COMPLETENESS,
        name="Sales required keys",
        description="business_date, store_id and sku_id must be present.",
        severity=DqSeverity.BLOCKER,
        blocking=True,
        owner_role="Data Engineer",
    ),
    DqRule(
        rule_id="stock_non_negative_qty",
        domain=DataDomain.STOCK,
        dimension=DqDimension.VALIDITY,
        name="Stock non-negative quantity",
        description="on_hand_qty, reserved_qty and in_transit_qty must be non-negative.",
        severity=DqSeverity.ERROR,
        blocking=True,
        owner_role="Data Owner",
    ),
    DqRule(
        rule_id="prices_freshness",
        domain=DataDomain.PRICES,
        dimension=DqDimension.FRESHNESS,
        name="Prices loaded before cutoff",
        description="Daily prices must arrive before forecast cutoff.",
        severity=DqSeverity.WARNING,
        blocking=False,
        owner_role="Data Owner",
    ),
)

INCIDENTS: tuple[DqIncident, ...] = (
    DqIncident(
        incident_id="dq-20260528-sales-001",
        rule_id="sales_required_keys",
        batch_id="sales-2026-05-28-pos",
        domain=DataDomain.SALES,
        business_date=date(2026, 5, 28),
        severity=DqSeverity.BLOCKER,
        status=DqIncidentStatus.BLOCKING,
        blocking=True,
        affected_rows=128,
        affected_scope="region=77, source=POS",
        message="Missing store_id in inbound sales rows.",
        created_at=datetime(2026, 5, 28, 4, 20, tzinfo=timezone.utc),
        owner_role="Data Engineer",
    ),
    DqIncident(
        incident_id="dq-20260528-prices-001",
        rule_id="prices_freshness",
        batch_id="prices-2026-05-28-erp",
        domain=DataDomain.PRICES,
        business_date=date(2026, 5, 28),
        severity=DqSeverity.WARNING,
        status=DqIncidentStatus.IN_REVIEW,
        blocking=False,
        affected_rows=5400,
        affected_scope="category=fresh",
        message="Prices arrived after configured cutoff.",
        created_at=datetime(2026, 5, 28, 4, 55, tzinfo=timezone.utc),
        owner_role="Data Owner",
    ),
)

SOURCE_CONTRACT_DQ_PLANS: tuple[SourceContractDqPlan, ...] = (
    SourceContractDqPlan(
        source_system="POS",
        contract_name="pos_sales_line",
        blocking_rules=("required_keys", "non_zero_qty", "known_store_sku", "checksum_match"),
        warning_rules=("late_arrival", "negative_qty_return_ratio"),
        owner_role="Data Engineer",
    ),
    SourceContractDqPlan(
        source_system="WMS",
        contract_name="wms_stock_snapshot_line",
        blocking_rules=("required_keys", "non_negative_qty", "available_not_above_on_hand", "known_location_sku"),
        warning_rules=("late_arrival", "high_damaged_qty"),
        owner_role="Inventory Data Owner",
    ),
    SourceContractDqPlan(
        source_system="WMS",
        contract_name="wms_open_order_line",
        blocking_rules=("required_keys", "positive_ordered_qty", "valid_delivery_date", "known_location_sku"),
        warning_rules=("stale_order_status",),
        owner_role="Supply Chain Data Owner",
    ),
    SourceContractDqPlan(
        source_system="WMS",
        contract_name="wms_in_transit_line",
        blocking_rules=("required_keys", "positive_shipped_qty", "valid_eta_date", "known_location_sku"),
        warning_rules=("late_eta",),
        owner_role="Supply Chain Data Owner",
    ),
    SourceContractDqPlan(
        source_system="ERP",
        contract_name="erp_price_line",
        blocking_rules=("required_keys", "positive_prices", "selling_not_extreme", "valid_currency"),
        warning_rules=("late_arrival", "large_price_change"),
        owner_role="Commercial Data Owner",
    ),
    SourceContractDqPlan(
        source_system="ERP",
        contract_name="erp_order_export_status_line",
        blocking_rules=("required_keys", "known_proposal_id", "valid_export_status"),
        warning_rules=("retry_count_high", "missing_external_order_id"),
        owner_role="Integration Owner",
    ),
    SourceContractDqPlan(
        source_system="MDM",
        contract_name="mdm_product_line",
        blocking_rules=("required_keys", "valid_hierarchy", "valid_lifecycle_status"),
        warning_rules=("missing_supplier", "missing_shelf_life_for_fresh"),
        owner_role="MDM Data Owner",
    ),
    SourceContractDqPlan(
        source_system="MDM",
        contract_name="mdm_store_line",
        blocking_rules=("required_keys", "valid_region_format", "valid_replenishment_route"),
        warning_rules=("missing_warehouse_id",),
        owner_role="MDM Data Owner",
    ),
    SourceContractDqPlan(
        source_system="PROMO",
        contract_name="promo_plan_line",
        blocking_rules=("required_keys", "promo_price_not_above_regular", "no_invalid_overlap", "valid_period"),
        warning_rules=("missing_display_capacity", "display_capacity_above_planogram"),
        owner_role="Promo Planner",
    ),
)


def source_contract_plan_map() -> dict[tuple[str, str], SourceContractDqPlan]:
    return {(plan.source_system, plan.contract_name): plan for plan in SOURCE_CONTRACT_DQ_PLANS}


def evaluate_source_contract_dq_result(
    contract: ShadowLoadContractResult,
    plan: SourceContractDqPlan,
) -> SourceContractDqCheckResult:
    if contract.status == "missing_files":
        return SourceContractDqCheckResult(
            source_system=contract.source_system,
            contract_name=contract.contract_name,
            status="blocked",
            severity=DqSeverity.BLOCKER,
            blocking_rules_checked=plan.blocking_rules,
            warning_rules_checked=plan.warning_rules,
            blocker_count=1,
            warning_count=0,
            message="Source files are missing; DQ execution cannot continue.",
        )
    if contract.discovered_size_bytes == 0:
        return SourceContractDqCheckResult(
            source_system=contract.source_system,
            contract_name=contract.contract_name,
            status="blocked",
            severity=DqSeverity.BLOCKER,
            blocking_rules_checked=plan.blocking_rules,
            warning_rules_checked=plan.warning_rules,
            blocker_count=1,
            warning_count=0,
            message="Source files are empty; clean publication is blocked.",
        )
    return SourceContractDqCheckResult(
        source_system=contract.source_system,
        contract_name=contract.contract_name,
        status="passed",
        severity=DqSeverity.INFO,
        blocking_rules_checked=plan.blocking_rules,
        warning_rules_checked=plan.warning_rules,
        blocker_count=0,
        warning_count=0,
        message="Source file discovered and contract DQ plan executed.",
    )


def run_source_contract_dq(report: ShadowLoadReport) -> SourceContractDqRunResponse:
    plans = source_contract_plan_map()
    results: list[SourceContractDqCheckResult] = []
    for contract in report.results:
        plan = plans[(contract.source_system, contract.contract_name)]
        results.append(evaluate_source_contract_dq_result(contract, plan))

    blocker_count = sum(result.blocker_count for result in results)
    warning_count = sum(result.warning_count for result in results)
    return SourceContractDqRunResponse(
        business_date=report.business_date,
        status="blocked" if blocker_count else "passed_with_warnings" if warning_count else "passed",
        total_contracts=len(results),
        blocker_count=blocker_count,
        warning_count=warning_count,
        results=tuple(results),
    )


@router.get("/rules")
def list_dq_rules(domain: DataDomain | None = None) -> dict[str, object]:
    rules = list(RULES)
    if domain is not None:
        rules = [rule for rule in rules if rule.domain == domain]
    return {"items": [rule.model_dump(mode="json") for rule in rules], "total": len(rules)}


@router.get("/source-contract-plans")
def list_source_contract_dq_plans(source_system: str | None = None) -> dict[str, object]:
    plans = list(SOURCE_CONTRACT_DQ_PLANS)
    if source_system is not None:
        plans = [plan for plan in plans if plan.source_system == source_system.upper()]
    return {"items": [plan.model_dump(mode="json") for plan in plans], "total": len(plans)}


@router.post("/source-contract-runs")
def run_source_contract_dq_checks(request: SourceContractDqRunRequest) -> dict[str, object]:
    report = run_shadow_load_discovery(request.business_date, request.landing_root_path)
    result = run_source_contract_dq(report)
    return result.model_dump(mode="json")


@router.get("/incidents")
def list_dq_incidents(
    domain: DataDomain | None = None,
    severity: DqSeverity | None = None,
    status: DqIncidentStatus | None = None,
    blocking: bool | None = None,
) -> dict[str, object]:
    incidents = list(INCIDENTS)
    if domain is not None:
        incidents = [incident for incident in incidents if incident.domain == domain]
    if severity is not None:
        incidents = [incident for incident in incidents if incident.severity == severity]
    if status is not None:
        incidents = [incident for incident in incidents if incident.status == status]
    if blocking is not None:
        incidents = [incident for incident in incidents if incident.blocking is blocking]
    return {"items": [incident.model_dump(mode="json") for incident in incidents], "total": len(incidents)}


@router.get("/incidents/{incident_id}")
def get_dq_incident(incident_id: str = Path(min_length=1)) -> dict[str, object]:
    for incident in INCIDENTS:
        if incident.incident_id == incident_id:
            return incident.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="incident not found")


@router.post("/incidents/{incident_id}/waiver")
def waive_dq_incident(
    request: DqWaiverRequest,
    incident_id: str = Path(min_length=1),
) -> dict[str, object]:
    if request.approver_role not in {"Data Owner", "Admin"}:
        raise HTTPException(status_code=403, detail="waiver requires Data Owner or Admin role")
    for incident in INCIDENTS:
        if incident.incident_id == incident_id:
            waived = incident.model_copy(
                update={
                    "status": DqIncidentStatus.WAIVED,
                    "blocking": False,
                    "waiver_reason": request.reason,
                },
            )
            return waived.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="incident not found")
