from datetime import datetime, timezone
from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, Field


class RepositoryMode(StrEnum):
    IN_MEMORY = "in_memory"
    POSTGRES = "postgres"
    CLICKHOUSE = "clickhouse"


class AuditEventRecord(BaseModel):
    event_id: str
    event_type: str
    actor: str
    actor_role: str | None = None
    object_type: str
    object_id: str
    action: str
    reason: str
    correlation_id: str | None = None
    payload: dict[str, object] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditEventRepository(Protocol):
    mode: RepositoryMode

    def append(self, event: AuditEventRecord) -> AuditEventRecord:
        ...

    def list_recent(self, limit: int = 50) -> tuple[AuditEventRecord, ...]:
        ...


class InMemoryAuditEventRepository:
    mode = RepositoryMode.IN_MEMORY

    def __init__(self) -> None:
        self._events: list[AuditEventRecord] = []

    def append(self, event: AuditEventRecord) -> AuditEventRecord:
        self._events.append(event)
        return event

    def list_recent(self, limit: int = 50) -> tuple[AuditEventRecord, ...]:
        return tuple(reversed(self._events[-limit:]))


audit_event_repository = InMemoryAuditEventRepository()
