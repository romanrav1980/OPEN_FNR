from pathlib import Path


CLICKHOUSE_INIT = Path("infra/dev/clickhouse/init/001_open_fnr.sql")


def test_raw_promo_plan_schema_exists() -> None:
    sql = CLICKHOUSE_INIT.read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS open_fnr.raw_promo_plans" in sql
    assert "promo_id String" in sql
    assert "store_scope_id String" in sql
    assert "discount_pct Float64" in sql
    assert "display_location Nullable(String)" in sql
    assert "display_capacity_units Nullable(Float64)" in sql
    assert "forecast_lock UInt8" in sql
