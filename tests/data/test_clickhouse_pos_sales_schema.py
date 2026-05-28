from pathlib import Path


CLICKHOUSE_INIT = Path("infra/dev/clickhouse/init/001_open_fnr.sql")


def test_raw_pos_sales_lines_schema_exists() -> None:
    sql = CLICKHOUSE_INIT.read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS open_fnr.raw_pos_sales_lines" in sql
    assert "receipt_id String" in sql
    assert "line_id String" in sql
    assert "business_date Date" in sql
    assert "store_id String" in sql
    assert "sku_id String" in sql
    assert "sales_qty Float64" in sql
    assert "net_amount Float64" in sql
    assert "source_system String" in sql
