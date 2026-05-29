from pathlib import Path


POSTGRES_SCHEMA = Path("infra/dev/postgres/init/001_open_fnr.sql")


def test_postgres_schema_contains_operational_persistence_tables() -> None:
    sql = POSTGRES_SCHEMA.read_text(encoding="utf-8")

    for table in (
        "open_fnr.process_tasks",
        "open_fnr.process_task_events",
        "open_fnr.operational_decisions",
        "open_fnr.publication_packages",
        "open_fnr.export_attempts",
    ):
        assert f"CREATE TABLE IF NOT EXISTS {table}" in sql


def test_postgres_schema_contains_idempotency_and_process_indexes() -> None:
    sql = POSTGRES_SCHEMA.read_text(encoding="utf-8")

    assert "idempotency_key text NOT NULL UNIQUE" in sql
    assert "ix_process_tasks_business_key" in sql
    assert "ix_operational_decisions_object" in sql
    assert "ix_export_attempts_package" in sql
    assert "ix_audit_events_correlation" in sql
    assert "ix_audit_events_type" in sql
