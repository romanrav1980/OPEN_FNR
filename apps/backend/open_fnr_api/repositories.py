import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, Field

from .config import Settings, settings
from .database import DbConnectionFactory, make_pg8000_connection_factory, managed_connection


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


class PostgresAuditEventRepository:
    mode = RepositoryMode.POSTGRES

    def __init__(self, connection_factory: DbConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def append(self, event: AuditEventRecord) -> AuditEventRecord:
        with managed_connection(self._connection_factory) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO open_fnr.audit_events
                (
                    event_id, event_type, actor, actor_role, object_type, object_id,
                    action, reason, correlation_id, payload, created_at
                )
                VALUES
                (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s::jsonb, %s
                )
                """,
                (
                    event.event_id,
                    event.event_type,
                    event.actor,
                    event.actor_role,
                    event.object_type,
                    event.object_id,
                    event.action,
                    event.reason,
                    event.correlation_id,
                    json.dumps(event.payload, ensure_ascii=False),
                    event.created_at,
                ),
            )
        return event

    def list_recent(self, limit: int = 50) -> tuple[AuditEventRecord, ...]:
        with managed_connection(self._connection_factory) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    event_id, event_type, actor, actor_role, object_type, object_id,
                    action, reason, correlation_id, payload, created_at
                FROM open_fnr.audit_events
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cursor.fetchall()

        return tuple(
            AuditEventRecord(
                event_id=row[0],
                event_type=row[1],
                actor=row[2],
                actor_role=row[3],
                object_type=row[4],
                object_id=row[5],
                action=row[6],
                reason=row[7],
                correlation_id=row[8],
                payload=row[9] if isinstance(row[9], dict) else json.loads(row[9]),
                created_at=row[10],
            )
            for row in rows
        )


def build_audit_event_repository(app_settings: Settings = settings) -> AuditEventRepository:
    if app_settings.mock_mode:
        return InMemoryAuditEventRepository()
    return PostgresAuditEventRepository(make_pg8000_connection_factory(app_settings))


audit_event_repository = build_audit_event_repository()
