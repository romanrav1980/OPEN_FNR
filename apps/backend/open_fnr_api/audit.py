from uuid import uuid4
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .config import settings
from .repositories import AuditEventRecord, audit_event_repository


router = APIRouter(prefix="/audit", tags=["audit"])


class AuditEventCreate(BaseModel):
    event_type: str = Field(min_length=1)
    actor: str = Field(min_length=1)
    actor_role: str | None = None
    object_type: str = Field(min_length=1)
    object_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    correlation_id: str | None = None
    payload: dict[str, object] = Field(default_factory=dict)


def record_audit_event(request: AuditEventCreate) -> AuditEventRecord:
    event = AuditEventRecord(event_id=f"audit-{uuid4()}", **request.model_dump())
    return audit_event_repository.append(event)


def record_audit_event_if_enabled(request: AuditEventCreate) -> AuditEventRecord | None:
    if not settings.audit_enabled:
        return None
    return record_audit_event(request)


@router.post("/events", response_model=AuditEventRecord)
def create_audit_event(request: AuditEventCreate) -> AuditEventRecord:
    return record_audit_event(request)


@router.get("/events", response_model=tuple[AuditEventRecord, ...])
def list_audit_events(
    limit: int = Query(default=50, ge=1, le=500),
    actor: str | None = None,
    object_type: str | None = None,
    object_id: str | None = None,
    event_type: str | None = None,
    correlation_id: str | None = None,
) -> tuple[AuditEventRecord, ...]:
    return audit_event_repository.search(
        limit=limit,
        actor=actor,
        object_type=object_type,
        object_id=object_id,
        event_type=event_type,
        correlation_id=correlation_id,
    )


@router.get("/retention-plan")
def get_audit_retention_plan() -> dict[str, object]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.audit_retention_days)
    return {
        "retention_days": settings.audit_retention_days,
        "cutoff_before": cutoff.isoformat(),
        "repository_mode": audit_event_repository.mode,
        "business_process_audit_default": settings.audit_enabled,
    }


@router.post("/retention/purge")
def purge_audit_events(actor_role: str = Query(min_length=1)) -> dict[str, object]:
    if actor_role not in {"Admin", "Auditor"}:
        raise HTTPException(status_code=403, detail="actor role is not allowed to purge audit events")
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.audit_retention_days)
    deleted = audit_event_repository.delete_older_than(cutoff)
    return {"deleted": deleted, "cutoff_before": cutoff.isoformat()}
