from pathlib import Path


CLICKHOUSE_INIT = Path("infra/dev/clickhouse/init/001_open_fnr.sql")


def test_raw_erp_commercial_schemas_exist() -> None:
    sql = CLICKHOUSE_INIT.read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS open_fnr.raw_erp_prices" in sql
    assert "price_id String" in sql
    assert "valid_from Date" in sql
    assert "selling_price Float64" in sql
    assert "CREATE TABLE IF NOT EXISTS open_fnr.raw_erp_order_export_statuses" in sql
    assert "export_id String" in sql
    assert "proposal_id String" in sql
    assert "retry_count UInt32" in sql
