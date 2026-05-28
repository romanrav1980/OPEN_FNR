from pathlib import Path


CLICKHOUSE_INIT = Path("infra/dev/clickhouse/init/001_open_fnr.sql")


def test_raw_wms_inventory_schemas_exist() -> None:
    sql = CLICKHOUSE_INIT.read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS open_fnr.raw_wms_stock_snapshots" in sql
    assert "snapshot_id String" in sql
    assert "available_qty Float64" in sql
    assert "CREATE TABLE IF NOT EXISTS open_fnr.raw_wms_open_orders" in sql
    assert "order_id String" in sql
    assert "expected_delivery_date Date" in sql
    assert "ordered_qty Float64" in sql
    assert "CREATE TABLE IF NOT EXISTS open_fnr.raw_wms_in_transit" in sql
    assert "shipment_id String" in sql
    assert "eta_date Date" in sql
    assert "shipped_qty Float64" in sql
