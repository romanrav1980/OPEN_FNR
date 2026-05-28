from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field

from .data_contracts import DataDomain, DqSeverity


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


@router.get("/rules")
def list_dq_rules(domain: DataDomain | None = None) -> dict[str, object]:
    rules = list(RULES)
    if domain is not None:
        rules = [rule for rule in rules if rule.domain == domain]
    return {"items": [rule.model_dump(mode="json") for rule in rules], "total": len(rules)}


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
