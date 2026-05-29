from datetime import datetime, timezone

from open_fnr_api.config import Settings
from open_fnr_api.repositories import (
    AuditEventRecord,
    InMemoryAuditEventRepository,
    InMemoryOperationalDecisionRepository,
    InMemoryProcessTaskRepository,
    OperationalDecisionRecord,
    PostgresAuditEventRepository,
    PostgresOperationalDecisionRepository,
    PostgresProcessTaskRepository,
    ProcessTaskEventRecord,
    ProcessTaskRecord,
    RepositoryMode,
    build_audit_event_repository,
    build_operational_decision_repository,
    build_process_task_repository,
)


class FakeCursor:
    def __init__(self) -> None:
        self.executed: list[tuple[str, tuple[object, ...]]] = []

    def execute(self, sql: str, params: tuple[object, ...]) -> None:
        self.executed.append((sql, params))

    def fetchall(self) -> list[tuple[object, ...]]:
        return [
            (
                "audit-1",
                "approval",
                "planner@example.org",
                "Forecast Planner",
                "forecast",
                "forecast-1",
                "approve",
                "accepted",
                "corr-1",
                {"ok": True},
                datetime(2026, 5, 29, tzinfo=timezone.utc),
            )
        ]


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_instance = FakeCursor()
        self.committed = False
        self.closed = False

    def cursor(self) -> FakeCursor:
        return self.cursor_instance

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        raise AssertionError("rollback should not be called")

    def close(self) -> None:
        self.closed = True


def test_repository_factory_uses_in_memory_for_mock_mode() -> None:
    repository = build_audit_event_repository(Settings(mock_mode=True))
    process_repository = build_process_task_repository(Settings(mock_mode=True))
    decision_repository = build_operational_decision_repository(Settings(mock_mode=True))

    assert isinstance(repository, InMemoryAuditEventRepository)
    assert repository.mode == RepositoryMode.IN_MEMORY
    assert isinstance(process_repository, InMemoryProcessTaskRepository)
    assert process_repository.mode == RepositoryMode.IN_MEMORY
    assert isinstance(decision_repository, InMemoryOperationalDecisionRepository)
    assert decision_repository.mode == RepositoryMode.IN_MEMORY


def test_repository_factory_uses_postgres_when_mock_mode_is_disabled() -> None:
    repository = build_audit_event_repository(Settings(mock_mode=False))
    process_repository = build_process_task_repository(Settings(mock_mode=False))
    decision_repository = build_operational_decision_repository(Settings(mock_mode=False))

    assert isinstance(repository, PostgresAuditEventRepository)
    assert repository.mode == RepositoryMode.POSTGRES
    assert isinstance(process_repository, PostgresProcessTaskRepository)
    assert process_repository.mode == RepositoryMode.POSTGRES
    assert isinstance(decision_repository, PostgresOperationalDecisionRepository)
    assert decision_repository.mode == RepositoryMode.POSTGRES


def test_postgres_audit_repository_inserts_and_reads_events() -> None:
    fake_connection = FakeConnection()
    repository = PostgresAuditEventRepository(lambda: fake_connection)
    event = AuditEventRecord(
        event_id="audit-1",
        event_type="approval",
        actor="planner@example.org",
        actor_role="Forecast Planner",
        object_type="forecast",
        object_id="forecast-1",
        action="approve",
        reason="accepted",
        correlation_id="corr-1",
        payload={"ok": True},
        created_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )

    assert repository.append(event) == event
    assert fake_connection.committed is True
    assert fake_connection.closed is True
    insert_sql, insert_params = fake_connection.cursor_instance.executed[0]
    assert "INSERT INTO open_fnr.audit_events" in insert_sql
    assert insert_params[0] == "audit-1"
    assert insert_params[9] == '{"ok": true}'

    recent = repository.list_recent(limit=1)
    assert recent[0].event_id == "audit-1"
    assert recent[0].payload == {"ok": True}


def test_postgres_process_task_repository_upserts_task_and_appends_event() -> None:
    fake_connection = FakeConnection()
    repository = PostgresProcessTaskRepository(lambda: fake_connection)
    task = ProcessTaskRecord(
        task_id="task-1",
        process_instance_id="pi-1",
        process_key="forecast_review_process",
        name="Review forecast",
        status="open",
        assigned_role="Forecast Planner",
        candidate_roles=("Forecast Planner", "Forecast Owner"),
        available_actions=("approve", "reject"),
        sla_due_at=datetime(2026, 5, 30, tzinfo=timezone.utc),
        business_key="forecast-run-1",
        payload={"priority": "high"},
        created_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )
    event = ProcessTaskEventRecord(
        event_id="event-1",
        process_instance_id="pi-1",
        task_id="task-1",
        event_type="task_created",
        actor="system",
        actor_role="Service Account",
        message="Task created.",
        payload={"source": "test"},
        created_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )

    assert repository.upsert_task(task) == task
    assert repository.append_event(event) == event

    task_sql, task_params = fake_connection.cursor_instance.executed[0]
    event_sql, event_params = fake_connection.cursor_instance.executed[1]
    assert "INSERT INTO open_fnr.process_tasks" in task_sql
    assert "ON CONFLICT (task_id)" in task_sql
    assert task_params[0] == "task-1"
    assert task_params[6] == '["Forecast Planner", "Forecast Owner"]'
    assert task_params[10] == '{"priority": "high"}'
    assert "INSERT INTO open_fnr.process_task_events" in event_sql
    assert event_params[0] == "event-1"
    assert event_params[7] == '{"source": "test"}'


def test_postgres_operational_decision_repository_upserts_by_idempotency_key() -> None:
    fake_connection = FakeConnection()
    repository = PostgresOperationalDecisionRepository(lambda: fake_connection)
    decision = OperationalDecisionRecord(
        decision_id="decision-1",
        decision_type="approval",
        object_type="order_proposal",
        object_id="order-1",
        status="approved",
        actor="planner@example.org",
        actor_role="Replenishment Planner",
        idempotency_key="order-1:approve:v1",
        correlation_id="corr-1",
        payload={"qty": 48},
        created_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )

    assert repository.upsert_decision(decision) == decision

    sql, params = fake_connection.cursor_instance.executed[0]
    assert "INSERT INTO open_fnr.operational_decisions" in sql
    assert "ON CONFLICT (idempotency_key)" in sql
    assert params[0] == "decision-1"
    assert params[7] == "order-1:approve:v1"
    assert params[9] == '{"qty": 48}'
