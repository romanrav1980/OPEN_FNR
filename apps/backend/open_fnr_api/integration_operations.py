from __future__ import annotations

from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .data_contracts import SOURCE_CONTRACT_REGISTRY, SourceContractDefinition
from .data_quality import run_source_contract_dq
from .shadow_load import run_shadow_load_discovery


router = APIRouter(prefix="/integration/operations", tags=["integration-operations"])


class SourceOperationalStatus(BaseModel):
    source_system: str
    contract_name: str
    business_date: date
    owner_role: str
    source_sla: str
    status: str
    blocker_count: int = Field(ge=0)
    warning_count: int = Field(ge=0)
    retry_allowed: bool
    recovery_action: str
    idempotency_key: str


class SourceReadinessResponse(BaseModel):
    business_date: date
    status: str
    total_contracts: int = Field(ge=0)
    ready_contracts: int = Field(ge=0)
    blocked_contracts: int = Field(ge=0)
    warning_contracts: int = Field(ge=0)
    items: tuple[SourceOperationalStatus, ...]


class SourceRetryPlan(BaseModel):
    source_system: str
    contract_name: str
    idempotency_key: str
    retry_strategy: str
    max_attempts: int = Field(ge=1)
    owner_role: str
    next_action: str


class RetryPlanResponse(BaseModel):
    business_date: date
    total: int = Field(ge=0)
    items: tuple[SourceRetryPlan, ...]


class ReconciliationItem(BaseModel):
    source_system: str
    contract_name: str
    reconciliation_keys: tuple[str, ...]
    status: str
    downstream_blockers: tuple[str, ...]
    owner_role: str


class ReconciliationResponse(BaseModel):
    business_date: date
    status: str
    total: int = Field(ge=0)
    blocked_count: int = Field(ge=0)
    items: tuple[ReconciliationItem, ...]


def _contract_by_name() -> dict[tuple[str, str], SourceContractDefinition]:
    return {(contract.source_system, contract.contract_name): contract for contract in SOURCE_CONTRACT_REGISTRY}


def build_source_readiness(business_date: date, landing_root_path: str | None = None) -> SourceReadinessResponse:
    report = run_shadow_load_discovery(business_date, landing_root_path)
    dq_run = run_source_contract_dq(report)
    contracts = _contract_by_name()
    shadow_by_key = {(item.source_system, item.contract_name): item for item in report.results}
    results_by_key = {(item.source_system, item.contract_name): item for item in dq_run.results}
    items: list[SourceOperationalStatus] = []

    for key, contract in contracts.items():
        shadow = shadow_by_key[key]
        result = results_by_key[key]
        status = "ready"
        if result.blocker_count:
            status = "blocked"
        elif result.warning_count:
            status = "warning"
        items.append(
            SourceOperationalStatus(
                source_system=contract.source_system,
                contract_name=contract.contract_name,
                business_date=business_date,
                owner_role=contract.business_owner_role,
                source_sla=contract.source_sla,
                status=status,
                blocker_count=result.blocker_count,
                warning_count=result.warning_count,
                retry_allowed=status == "blocked",
                recovery_action="request_resend_and_rerun" if status == "blocked" else "monitor",
                idempotency_key=shadow.idempotency_key,
            )
        )

    blocked_contracts = sum(1 for item in items if item.status == "blocked")
    warning_contracts = sum(1 for item in items if item.status == "warning")
    ready_contracts = sum(1 for item in items if item.status == "ready")
    return SourceReadinessResponse(
        business_date=business_date,
        status="blocked" if blocked_contracts else "warning" if warning_contracts else "ready",
        total_contracts=len(items),
        ready_contracts=ready_contracts,
        blocked_contracts=blocked_contracts,
        warning_contracts=warning_contracts,
        items=tuple(items),
    )


def build_retry_plan(business_date: date, landing_root_path: str | None = None) -> RetryPlanResponse:
    readiness = build_source_readiness(business_date, landing_root_path)
    items = tuple(
        SourceRetryPlan(
            source_system=item.source_system,
            contract_name=item.contract_name,
            idempotency_key=item.idempotency_key,
            retry_strategy="same_idempotency_key_no_duplicate_clean_rows",
            max_attempts=3,
            owner_role=item.owner_role,
            next_action=item.recovery_action,
        )
        for item in readiness.items
        if item.retry_allowed
    )
    return RetryPlanResponse(business_date=business_date, total=len(items), items=items)


def build_reconciliation_summary(business_date: date, landing_root_path: str | None = None) -> ReconciliationResponse:
    readiness = build_source_readiness(business_date, landing_root_path)
    contracts = _contract_by_name()
    items = []
    for status in readiness.items:
        contract = contracts[(status.source_system, status.contract_name)]
        items.append(
            ReconciliationItem(
                source_system=status.source_system,
                contract_name=status.contract_name,
                reconciliation_keys=contract.reconciliation_keys,
                status="blocked" if status.blocker_count else "ready",
                downstream_blockers=contract.required_for if status.blocker_count else (),
                owner_role=status.owner_role,
            )
        )
    blocked_count = sum(1 for item in items if item.status == "blocked")
    return ReconciliationResponse(
        business_date=business_date,
        status="blocked" if blocked_count else "ready",
        total=len(items),
        blocked_count=blocked_count,
        items=tuple(items),
    )


@router.get("/source-readiness")
def get_source_readiness(business_date: date, landing_root_path: str | None = None) -> dict[str, object]:
    return build_source_readiness(business_date, landing_root_path).model_dump(mode="json")


@router.get("/retry-plan")
def get_retry_plan(business_date: date, landing_root_path: str | None = None) -> dict[str, object]:
    return build_retry_plan(business_date, landing_root_path).model_dump(mode="json")


@router.get("/reconciliation")
def get_reconciliation_summary(business_date: date, landing_root_path: str | None = None) -> dict[str, object]:
    return build_reconciliation_summary(business_date, landing_root_path).model_dump(mode="json")
