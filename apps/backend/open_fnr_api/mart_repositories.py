from dataclasses import dataclass
from typing import Protocol

from .repositories import RepositoryMode


@dataclass(frozen=True)
class MartTable:
    name: str
    purpose: str
    engine: str
    partition_key: str
    order_key: str


class MartMetadataRepository(Protocol):
    mode: RepositoryMode

    def list_tables(self) -> tuple[MartTable, ...]:
        ...


CLICKHOUSE_MART_TABLES: tuple[MartTable, ...] = (
    MartTable(
        name="open_fnr.forecast_daily",
        purpose="Forecast rows by store, SKU and day",
        engine="MergeTree",
        partition_key="toYYYYMM(run_date)",
        order_key="run_date, forecast_date, store_id, sku_id",
    ),
    MartTable(
        name="open_fnr.order_proposals",
        purpose="Order proposals with replenishment explanation",
        engine="MergeTree",
        partition_key="toYYYYMM(run_date)",
        order_key="run_date, order_date, target_location_id, sku_id",
    ),
    MartTable(
        name="open_fnr.stock_projection_daily",
        purpose="Projected stock by store, SKU and day",
        engine="MergeTree",
        partition_key="toYYYYMM(run_date)",
        order_key="run_date, projection_date, store_id, sku_id",
    ),
    MartTable(
        name="open_fnr.kpi_daily",
        purpose="Accuracy and business KPI aggregates",
        engine="MergeTree",
        partition_key="toYYYYMM(period_end)",
        order_key="period_end, region_id, category_id, store_id, sku_id",
    ),
    MartTable(
        name="open_fnr.diagnostic_insights",
        purpose="Supply chain root cause diagnostics",
        engine="MergeTree",
        partition_key="toYYYYMM(run_date)",
        order_key="run_date, severity, object_type, object_id, insight_id",
    ),
    MartTable(
        name="open_fnr.supplier_performance_daily",
        purpose="Supplier collaboration performance metrics",
        engine="MergeTree",
        partition_key="toYYYYMM(calculation_date)",
        order_key="calculation_date, supplier_id",
    ),
)


class StaticMartMetadataRepository:
    mode = RepositoryMode.CLICKHOUSE

    def list_tables(self) -> tuple[MartTable, ...]:
        return CLICKHOUSE_MART_TABLES


mart_metadata_repository = StaticMartMetadataRepository()
