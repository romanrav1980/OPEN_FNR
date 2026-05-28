from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .audit import AuditEventCreate, record_audit_event_if_enabled


router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


class DiagnosticStatus(StrEnum):
    DETECTED = "detected"
    CLASSIFIED = "classified"
    REVIEWED = "reviewed"
    CONVERTED_TO_EXCEPTION = "converted_to_exception"
    CLOSED = "closed"


class RootCause(StrEnum):
    LATE_DELIVERY = "late_delivery"
    FORECAST_UNDERESTIMATION = "forecast_underestimation"
    PROMO_OVER_UPLIFT = "promo_over_uplift"
    DATA_QUALITY_GAP = "data_quality_gap"


class DiagnosticEvidence(BaseModel):
    evidence_id: str
    source: str
    object_id: str
    fact: str
    severity: str


class DiagnosticInsight(BaseModel):
    insight_id: str
    status: DiagnosticStatus
    root_cause: RootCause
    confidence: float = Field(ge=0, le=1)
    affected_store: str
    affected_sku: str
    symptom: str
    recommended_action: str
    linked_objects: tuple[str, ...]
    evidence: tuple[DiagnosticEvidence, ...]


class ExceptionCreateRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    comment: str = Field(min_length=1)


EVIDENCE = (
    DiagnosticEvidence(
        evidence_id="ev-wms-001",
        source="WMS",
        object_id="inbound-po-001",
        fact="Delivery arrived 2 days after planned receipt date.",
        severity="critical",
    ),
    DiagnosticEvidence(
        evidence_id="ev-stock-001",
        source="Projected Stock",
        object_id="projection-s001-sku001",
        fact="Projected stock turns negative on promo start date.",
        severity="critical",
    ),
    DiagnosticEvidence(
        evidence_id="ev-forecast-001",
        source="Forecast",
        object_id="forecast-s001-sku001",
        fact="Forecast accuracy is within acceptance band, bias -0.6%.",
        severity="info",
    ),
)


def classify_root_cause(evidence: tuple[DiagnosticEvidence, ...]) -> RootCause:
    facts = " ".join(item.fact.lower() for item in evidence)
    if "arrived 2 days after" in facts:
        return RootCause.LATE_DELIVERY
    if "bias" in facts and "-" in facts:
        return RootCause.FORECAST_UNDERESTIMATION
    return RootCause.DATA_QUALITY_GAP


def build_insight() -> DiagnosticInsight:
    root_cause = classify_root_cause(EVIDENCE)
    return DiagnosticInsight(
        insight_id="diagnostic-20260602-s001-sku001",
        status=DiagnosticStatus.CLASSIFIED,
        root_cause=root_cause,
        confidence=0.88,
        affected_store="S001",
        affected_sku="SKU001",
        symptom="Projected stock-out on promo start.",
        recommended_action="Create supply exception and expedite replacement delivery.",
        linked_objects=(
            "projection-s001-sku001",
            "order-proposal-20260528-s001-sku001",
            "promo-20260601-fresh-001",
            "inbound-po-001",
        ),
        evidence=EVIDENCE,
    )


@router.get("/insights", response_model=tuple[DiagnosticInsight, ...])
def list_insights() -> tuple[DiagnosticInsight, ...]:
    return (build_insight(),)


@router.post("/insights/{insight_id}/exception")
def create_exception_from_insight(insight_id: str, request: ExceptionCreateRequest) -> dict[str, object]:
    insight = build_insight()
    if insight_id != insight.insight_id:
        raise HTTPException(status_code=404, detail="Diagnostic insight not found")
    if request.actor_role not in {"Supply Chain Manager", "Forecast Planner", "Data Engineer"}:
        raise HTTPException(status_code=403, detail="Role is not allowed to convert diagnostic insight")
    record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="diagnostic_exception_created",
            actor=request.actor,
            actor_role=request.actor_role,
            object_type="diagnostic_insight",
            object_id=insight_id,
            action="create_exception",
            reason=request.comment,
            correlation_id="exc-diagnostic-20260602-s001-sku001",
            payload={
                "root_cause": insight.root_cause,
                "confidence": insight.confidence,
                "evidence_ids": [item.evidence_id for item in insight.evidence],
            },
        )
    )
    return {
        "insight_id": insight_id,
        "status": DiagnosticStatus.CONVERTED_TO_EXCEPTION,
        "exception_id": "exc-diagnostic-20260602-s001-sku001",
        "audit": {
            "actor": request.actor,
            "actor_role": request.actor_role,
            "comment": request.comment,
            "evidence_ids": [item.evidence_id for item in insight.evidence],
        },
    }
