from pathlib import Path


CLICKHOUSE_INIT = Path("infra/dev/clickhouse/init/001_open_fnr.sql")


def test_clickhouse_industrial_marts_are_declared_with_partitioning() -> None:
    sql = CLICKHOUSE_INIT.read_text(encoding="utf-8")

    for table in (
        "open_fnr.forecast_daily",
        "open_fnr.order_proposals",
        "open_fnr.stock_projection_daily",
        "open_fnr.kpi_daily",
        "open_fnr.diagnostic_insights",
        "open_fnr.supplier_performance_daily",
    ):
        assert f"CREATE TABLE IF NOT EXISTS {table}" in sql

    assert sql.count("ENGINE = MergeTree") >= 11
    assert "PARTITION BY toYYYYMM(run_date)" in sql
    assert "PARTITION BY toYYYYMM(period_end)" in sql
    assert "PARTITION BY toYYYYMM(calculation_date)" in sql
