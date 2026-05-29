from datetime import datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/observability", tags=["observability"])


class AlertSeverity(StrEnum):
    SEV1 = "sev1"
    SEV2 = "sev2"
    SEV3 = "sev3"


class IncidentStatus(StrEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    ESCALATED = "escalated"
    RESOLVED = "resolved"


class Alert(BaseModel):
    alert_id: str
    service: str
    severity: AlertSeverity
    message: str
    runbook_url: str
    created_at: datetime


class Incident(BaseModel):
    incident_id: str
    alert_id: str
    status: IncidentStatus
    owner_role: str
    sla_minutes: int = Field(gt=0)
    timeline: tuple[str, ...]


class IncidentActionRequest(BaseModel):
    actor: str = Field(min_length=1)
    actor_role: str
    comment: str = Field(min_length=1)


class SloTarget(BaseModel):
    service: str
    indicator: str
    target: str
    window: str
    owner_role: str
    dashboard_panel: str


class AlertRule(BaseModel):
    rule_id: str
    service: str
    severity: AlertSeverity
    expression: str
    runbook_url: str
    owner_role: str
    process_key: str


class TracePropagationCheck(BaseModel):
    trace_id: str
    services: tuple[str, ...]
    status: str
    evidence: tuple[str, ...]


class RunbookDrill(BaseModel):
    drill_id: str
    incident_type: str
    runbook_url: str
    steps: tuple[str, ...]
    expected_result: str
    last_result: str


ALERTS: tuple[Alert, ...] = (
    Alert(
        alert_id="alert-export-20260528-001",
        service="publication-export",
        severity=AlertSeverity.SEV2,
        message="ERP export failed for replenishment package.",
        runbook_url="runbooks/publication-export-failure.md",
        created_at=datetime(2026, 5, 28, 21, 0, tzinfo=timezone.utc),
    ),
)

SLO_TARGETS: tuple[SloTarget, ...] = (
    SloTarget(
        service="daily-pipeline",
        indicator="successful_daily_cycle",
        target="99.0%",
        window="rolling_30_days",
        owner_role="Data Platform Lead",
        dashboard_panel="pipeline_success_rate",
    ),
    SloTarget(
        service="forecasting",
        indicator="forecast_batch_runtime",
        target="p95_under_2_hours",
        window="rolling_14_days",
        owner_role="ML Lead",
        dashboard_panel="forecast_runtime_p95",
    ),
    SloTarget(
        service="publication-export",
        indicator="erp_export_latency",
        target="p95_under_15_minutes",
        window="business_day",
        owner_role="Integration Lead",
        dashboard_panel="erp_export_latency",
    ),
)

ALERT_RULES: tuple[AlertRule, ...] = (
    AlertRule(
        rule_id="alert-rule-source-sla-missed",
        service="integration-operations",
        severity=AlertSeverity.SEV2,
        expression="source_readiness_status == blocked for one daily cycle",
        runbook_url="docs/runbooks/source-sla-missed.md",
        owner_role="Data Platform Lead",
        process_key="data_load_monitoring_process",
    ),
    AlertRule(
        rule_id="alert-rule-forecast-runtime-p95",
        service="forecasting",
        severity=AlertSeverity.SEV2,
        expression="forecast_batch_runtime_p95 exceeds configured two hour gate",
        runbook_url="docs/runbooks/forecast-runtime-breach.md",
        owner_role="ML Lead",
        process_key="performance_test_run_process",
    ),
    AlertRule(
        rule_id="alert-rule-publication-export-failed",
        service="publication-export",
        severity=AlertSeverity.SEV2,
        expression="export_status == failed after retry budget exhausted",
        runbook_url="docs/runbooks/publication-export-failure.md",
        owner_role="Integration Lead",
        process_key="publication_process",
    ),
)

TRACE_PROPAGATION_CHECKS: tuple[TracePropagationCheck, ...] = (
    TracePropagationCheck(
        trace_id="trace-export-001",
        services=("daily-pipeline", "replenishment", "publication-export", "opensearch"),
        status="passed",
        evidence=("correlation_id_present", "trace_id_present_in_log", "incident_links_trace"),
    ),
)

RUNBOOK_DRILLS: tuple[RunbookDrill, ...] = (
    RunbookDrill(
        drill_id="drill-publication-export-20260529",
        incident_type="publication_export_failed",
        runbook_url="docs/runbooks/publication-export-failure.md",
        steps=(
            "confirm alert severity and owner",
            "find trace_id in log search",
            "check export idempotency key",
            "retry export or escalate to Integration Lead",
            "resolve incident with timeline evidence",
        ),
        expected_result="support can diagnose and recover failed ERP export without duplicate publication",
        last_result="passed",
    ),
)

INCIDENTS: tuple[Incident, ...] = (
    Incident(
        incident_id="inc-20260528-001",
        alert_id="alert-export-20260528-001",
        status=IncidentStatus.OPEN,
        owner_role="L2",
        sla_minutes=60,
        timeline=("alert_created", "incident_opened"),
    ),
)


def incident_sla_minutes(severity: AlertSeverity) -> int:
    return {AlertSeverity.SEV1: 15, AlertSeverity.SEV2: 60, AlertSeverity.SEV3: 240}[severity]


def transition_incident(incident: Incident, action: str, payload: IncidentActionRequest) -> Incident:
    role_by_action = {"acknowledge": "L1", "escalate": "L2", "resolve": "Incident Manager"}
    if action not in role_by_action:
        raise HTTPException(status_code=400, detail="unsupported incident action")
    if payload.actor_role != role_by_action[action]:
        raise HTTPException(status_code=403, detail=f"{role_by_action[action]} role required")
    status_by_action = {
        "acknowledge": IncidentStatus.ACKNOWLEDGED,
        "escalate": IncidentStatus.ESCALATED,
        "resolve": IncidentStatus.RESOLVED,
    }
    return incident.model_copy(update={"status": status_by_action[action], "timeline": (*incident.timeline, action)})


@router.get("/alerts")
def list_alerts(actor_role: str = "L1") -> dict[str, object]:
    if actor_role not in {"L1", "L2", "L3", "Incident Manager"}:
        raise HTTPException(status_code=403, detail="ops role required")
    return {"items": [item.model_dump(mode="json") for item in ALERTS], "total": len(ALERTS)}


@router.get("/incidents")
def list_incidents() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in INCIDENTS], "total": len(INCIDENTS)}


@router.get("/slo-targets")
def list_slo_targets() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in SLO_TARGETS], "total": len(SLO_TARGETS)}


@router.get("/alert-rules")
def list_alert_rules() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in ALERT_RULES], "total": len(ALERT_RULES)}


@router.get("/trace-propagation")
def list_trace_propagation_checks() -> dict[str, object]:
    return {
        "items": [item.model_dump(mode="json") for item in TRACE_PROPAGATION_CHECKS],
        "total": len(TRACE_PROPAGATION_CHECKS),
    }


@router.get("/runbook-drills")
def list_runbook_drills() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in RUNBOOK_DRILLS], "total": len(RUNBOOK_DRILLS)}


@router.post("/incidents/{incident_id}/{action}")
def act_on_incident(incident_id: str, action: str, payload: IncidentActionRequest) -> dict[str, object]:
    incident = next((item for item in INCIDENTS if item.incident_id == incident_id), None)
    if incident is None:
        raise HTTPException(status_code=404, detail="incident not found")
    updated = transition_incident(incident, action, payload)
    return updated.model_dump(mode="json")


@router.get("/logs/search")
def search_logs(query: str) -> dict[str, object]:
    return {
        "query": query,
        "items": [
            {
                "timestamp": "2026-05-28T21:00:02Z",
                "service": "publication-export",
                "message": "ERP export failed for repl-export-20260528-001",
                "trace_id": "trace-export-001",
            }
        ],
        "total": 1,
    }
