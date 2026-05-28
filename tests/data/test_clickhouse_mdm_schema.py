from pathlib import Path


CLICKHOUSE_INIT = Path("infra/dev/clickhouse/init/001_open_fnr.sql")


def test_raw_mdm_reference_schemas_exist() -> None:
    sql = CLICKHOUSE_INIT.read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS open_fnr.raw_mdm_products" in sql
    assert "category_path String" in sql
    assert "shelf_life_days Nullable(UInt32)" in sql
    assert "lifecycle_status String" in sql
    assert "CREATE TABLE IF NOT EXISTS open_fnr.raw_mdm_stores" in sql
    assert "replenishment_calendar_id Nullable(String)" in sql
    assert "warehouse_id Nullable(String)" in sql
