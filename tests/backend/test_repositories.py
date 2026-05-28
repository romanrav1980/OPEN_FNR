from datetime import datetime, timezone

from open_fnr_api.config import Settings
from open_fnr_api.repositories import (
    AuditEventRecord,
    InMemoryAuditEventRepository,
    PostgresAuditEventRepository,
    RepositoryMode,
    build_audit_event_repository,
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

    assert isinstance(repository, InMemoryAuditEventRepository)
    assert repository.mode == RepositoryMode.IN_MEMORY


def test_repository_factory_uses_postgres_when_mock_mode_is_disabled() -> None:
    repository = build_audit_event_repository(Settings(mock_mode=False))

    assert isinstance(repository, PostgresAuditEventRepository)
    assert repository.mode == RepositoryMode.POSTGRES


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
