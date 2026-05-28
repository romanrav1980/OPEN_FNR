from pathlib import Path


CLICKHOUSE_INIT = Path("infra/dev/clickhouse/init/001_open_fnr.sql")


def test_clean_canonical_tables_exist_with_lineage_and_quality_status() -> None:
    sql = CLICKHOUSE_INIT.read_text(encoding="utf-8")

    for table in (
        "clean_sales_daily",
        "clean_stock_snapshot_daily",
        "clean_open_orders",
        "clean_in_transit",
        "clean_prices",
        "clean_promo_plans",
    ):
        assert f"CREATE TABLE IF NOT EXISTS open_fnr.{table}" in sql

    assert sql.count("source_batch_id String") >= 6
    assert sql.count("quality_status String") >= 6
    assert "receipt_count UInt32" in sql
    assert "return_qty Float64" in sql
    assert "display_capacity_units Nullable(Float64)" in sql
