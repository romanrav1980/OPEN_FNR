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


class ProcessTaskRecord(BaseModel):
    task_id: str
    process_instance_id: str
    process_key: str
    name: str
    status: str
    assigned_role: str
    candidate_roles: tuple[str, ...]
    available_actions: tuple[str, ...]
    sla_due_at: datetime
    business_key: str
    payload: dict[str, object] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None


class ProcessTaskEventRecord(BaseModel):
    event_id: str
    process_instance_id: str
    task_id: str | None = None
    event_type: str
    actor: str
    actor_role: str | None = None
    message: str
    payload: dict[str, object] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalDecisionRecord(BaseModel):
    decision_id: str
    decision_type: str
    object_type: str
    object_id: str
    status: str
    actor: str
    actor_role: str | None = None
    idempotency_key: str
    correlation_id: str | None = None
    payload: dict[str, object] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProcessTaskRepository(Protocol):
    mode: RepositoryMode

    def upsert_task(self, task: ProcessTaskRecord) -> ProcessTaskRecord:
        ...

    def append_event(self, event: ProcessTaskEventRecord) -> ProcessTaskEventRecord:
        ...


class OperationalDecisionRepository(Protocol):
    mode: RepositoryMode

    def upsert_decision(self, decision: OperationalDecisionRecord) -> OperationalDecisionRecord:
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


class InMemoryProcessTaskRepository:
    mode = RepositoryMode.IN_MEMORY

    def __init__(self) -> None:
        self.tasks: dict[str, ProcessTaskRecord] = {}
        self.events: list[ProcessTaskEventRecord] = []

    def upsert_task(self, task: ProcessTaskRecord) -> ProcessTaskRecord:
        self.tasks[task.task_id] = task
        return task

    def append_event(self, event: ProcessTaskEventRecord) -> ProcessTaskEventRecord:
        self.events.append(event)
        return event


class PostgresProcessTaskRepository:
    mode = RepositoryMode.POSTGRES

    def __init__(self, connection_factory: DbConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def upsert_task(self, task: ProcessTaskRecord) -> ProcessTaskRecord:
        with managed_connection(self._connection_factory) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO open_fnr.process_tasks
                (
                    task_id, process_instance_id, process_key, name, status, assigned_role,
                    candidate_roles, available_actions, sla_due_at, business_key, payload,
                    created_at, updated_at, completed_at
                )
                VALUES
                (
                    %s, %s, %s, %s, %s, %s,
                    %s::jsonb, %s::jsonb, %s, %s, %s::jsonb,
                    %s, %s, %s
                )
                ON CONFLICT (task_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    assigned_role = EXCLUDED.assigned_role,
                    candidate_roles = EXCLUDED.candidate_roles,
                    available_actions = EXCLUDED.available_actions,
                    payload = EXCLUDED.payload,
                    updated_at = EXCLUDED.updated_at,
                    completed_at = EXCLUDED.completed_at
                """,
                (
                    task.task_id,
                    task.process_instance_id,
                    task.process_key,
                    task.name,
                    task.status,
                    task.assigned_role,
                    json.dumps(task.candidate_roles, ensure_ascii=False),
                    json.dumps(task.available_actions, ensure_ascii=False),
                    task.sla_due_at,
                    task.business_key,
                    json.dumps(task.payload, ensure_ascii=False),
                    task.created_at,
                    task.updated_at,
                    task.completed_at,
                ),
            )
        return task

    def append_event(self, event: ProcessTaskEventRecord) -> ProcessTaskEventRecord:
        with managed_connection(self._connection_factory) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO open_fnr.process_task_events
                (
                    event_id, process_instance_id, task_id, event_type, actor,
                    actor_role, message, payload, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                """,
                (
                    event.event_id,
                    event.process_instance_id,
                    event.task_id,
                    event.event_type,
                    event.actor,
                    event.actor_role,
                    event.message,
                    json.dumps(event.payload, ensure_ascii=False),
                    event.created_at,
                ),
            )
        return event


class InMemoryOperationalDecisionRepository:
    mode = RepositoryMode.IN_MEMORY

    def __init__(self) -> None:
        self.decisions: dict[str, OperationalDecisionRecord] = {}

    def upsert_decision(self, decision: OperationalDecisionRecord) -> OperationalDecisionRecord:
        self.decisions[decision.decision_id] = decision
        return decision


class PostgresOperationalDecisionRepository:
    mode = RepositoryMode.POSTGRES

    def __init__(self, connection_factory: DbConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def upsert_decision(self, decision: OperationalDecisionRecord) -> OperationalDecisionRecord:
        with managed_connection(self._connection_factory) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO open_fnr.operational_decisions
                (
                    decision_id, decision_type, object_type, object_id, status,
                    actor, actor_role, idempotency_key, correlation_id, payload,
                    created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                ON CONFLICT (idempotency_key) DO UPDATE SET
                    status = EXCLUDED.status,
                    payload = EXCLUDED.payload,
                    updated_at = EXCLUDED.updated_at
                """,
                (
                    decision.decision_id,
                    decision.decision_type,
                    decision.object_type,
                    decision.object_id,
                    decision.status,
                    decision.actor,
                    decision.actor_role,
                    decision.idempotency_key,
                    decision.correlation_id,
                    json.dumps(decision.payload, ensure_ascii=False),
                    decision.created_at,
                    decision.updated_at,
                ),
            )
        return decision


def build_audit_event_repository(app_settings: Settings = settings) -> AuditEventRepository:
    if app_settings.mock_mode:
        return InMemoryAuditEventRepository()
    return PostgresAuditEventRepository(make_pg8000_connection_factory(app_settings))


def build_process_task_repository(app_settings: Settings = settings) -> ProcessTaskRepository:
    if app_settings.mock_mode:
        return InMemoryProcessTaskRepository()
    return PostgresProcessTaskRepository(make_pg8000_connection_factory(app_settings))


def build_operational_decision_repository(app_settings: Settings = settings) -> OperationalDecisionRepository:
    if app_settings.mock_mode:
        return InMemoryOperationalDecisionRepository()
    return PostgresOperationalDecisionRepository(make_pg8000_connection_factory(app_settings))


audit_event_repository = build_audit_event_repository()
process_task_repository = build_process_task_repository()
operational_decision_repository = build_operational_decision_repository()
