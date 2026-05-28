from uuid import uuid4

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

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


@router.post("/events", response_model=AuditEventRecord)
def create_audit_event(request: AuditEventCreate) -> AuditEventRecord:
    return record_audit_event(request)


@router.get("/events", response_model=tuple[AuditEventRecord, ...])
def list_audit_events(limit: int = Query(default=50, ge=1, le=500)) -> tuple[AuditEventRecord, ...]:
    return audit_event_repository.list_recent(limit=limit)
