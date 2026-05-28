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
