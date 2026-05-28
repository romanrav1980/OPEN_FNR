from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.mart_repositories import CLICKHOUSE_MART_TABLES, RepositoryMode, mart_metadata_repository


client = TestClient(app)


def test_clickhouse_mart_metadata_lists_core_industrial_tables() -> None:
    response = client.get("/marts/clickhouse")
    assert response.status_code == 200

    payload = response.json()
    table_names = {item["name"] for item in payload["items"]}
    assert payload["storage"] == "clickhouse"
    assert payload["total"] == len(CLICKHOUSE_MART_TABLES)
    assert {
        "open_fnr.forecast_daily",
        "open_fnr.order_proposals",
        "open_fnr.stock_projection_daily",
        "open_fnr.kpi_daily",
        "open_fnr.diagnostic_insights",
        "open_fnr.supplier_performance_daily",
    }.issubset(table_names)


def test_mart_repository_is_clickhouse_boundary() -> None:
    assert mart_metadata_repository.mode == RepositoryMode.CLICKHOUSE
    assert all(table.engine == "MergeTree" for table in mart_metadata_repository.list_tables())
