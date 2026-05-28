from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field


router = APIRouter(prefix="/kpi", tags=["kpi"])


class KpiStatus(StrEnum):
    CALCULATED = "calculated"
    REVIEW_REQUIRED = "review_required"
    REVIEWED = "reviewed"
    ACTION_CREATED = "action_created"


class KpiSegment(BaseModel):
    network: str
    region: str
    category_id: str
    store_id: str | None = None
    sku_id: str | None = None


class AccuracyKpi(BaseModel):
    segment_id: str
    segment: KpiSegment
    period_start: date
    period_end: date
    status: KpiStatus
    actual_qty: float = Field(ge=0)
    ml_forecast_qty: float = Field(ge=0)
    final_forecast_qty: float = Field(ge=0)
    wape: float = Field(ge=0)
    bias: float
    service_level: float = Field(ge=0, le=1)
    out_of_stock_rate: float = Field(ge=0, le=1)
    overstock_value: float = Field(ge=0)
    lost_sales_value: float = Field(ge=0)
    waste_value: float = Field(ge=0)
    proposal_acceptance_rate: float = Field(ge=0, le=1)
    manual_adjustment_effect: float
    calculated_at: datetime


class BusinessValueSummary(BaseModel):
    service_level_impact: float
    stock_cost_impact: float
    lost_sales_impact: float
    waste_impact: float
    total_business_value: float


class KpiDashboard(BaseModel):
    filters: dict[str, list[str]]
    items: list[AccuracyKpi]
    business_value: BusinessValueSummary


def calculate_wape(actual: list[float], forecast: list[float]) -> float:
    denominator = sum(abs(value) for value in actual)
    if denominator == 0:
        return 0
    return sum(abs(a - f) for a, f in zip(actual, forecast, strict=True)) / denominator


def calculate_bias(actual: list[float], forecast: list[float]) -> float:
    denominator = sum(actual)
    if denominator == 0:
        return 0
    return sum(forecast) / denominator - 1


def kpi_alert_required(wape: float, bias: float, service_level: float) -> bool:
    return wape > 0.2 or abs(bias) > 0.05 or service_level < 0.94


KPI_ITEMS: tuple[AccuracyKpi, ...] = (
    AccuracyKpi(
        segment_id="network-all",
        segment=KpiSegment(network="OPEN_FNR_NETWORK", region="all", category_id="all"),
        period_start=date(2026, 5, 1),
        period_end=date(2026, 5, 28),
        status=KpiStatus.CALCULATED,
        actual_qty=1_240_000,
        ml_forecast_qty=1_218_000,
        final_forecast_qty=1_232_000,
        wape=0.158,
        bias=-0.006,
        service_level=0.965,
        out_of_stock_rate=0.021,
        overstock_value=1_420_000,
        lost_sales_value=680_000,
        waste_value=210_000,
        proposal_acceptance_rate=0.87,
        manual_adjustment_effect=14_000,
        calculated_at=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
    ),
    AccuracyKpi(
        segment_id="region-north-fresh",
        segment=KpiSegment(network="OPEN_FNR_NETWORK", region="north", category_id="fresh"),
        period_start=date(2026, 5, 1),
        period_end=date(2026, 5, 28),
        status=KpiStatus.REVIEW_REQUIRED,
        actual_qty=142_000,
        ml_forecast_qty=132_000,
        final_forecast_qty=136_000,
        wape=0.226,
        bias=-0.042,
        service_level=0.918,
        out_of_stock_rate=0.057,
        overstock_value=210_000,
        lost_sales_value=180_000,
        waste_value=65_000,
        proposal_acceptance_rate=0.71,
        manual_adjustment_effect=4_000,
        calculated_at=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
    ),
    AccuracyKpi(
        segment_id="sku-s001-sku001",
        segment=KpiSegment(network="OPEN_FNR_NETWORK", region="north", category_id="fresh", store_id="S001", sku_id="SKU001"),
        period_start=date(2026, 5, 1),
        period_end=date(2026, 5, 28),
        status=KpiStatus.ACTION_CREATED,
        actual_qty=320,
        ml_forecast_qty=292,
        final_forecast_qty=306,
        wape=0.241,
        bias=-0.044,
        service_level=0.902,
        out_of_stock_rate=0.083,
        overstock_value=0,
        lost_sales_value=18_000,
        waste_value=0,
        proposal_acceptance_rate=0.67,
        manual_adjustment_effect=14,
        calculated_at=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
    ),
)


def build_business_value(items: list[AccuracyKpi]) -> BusinessValueSummary:
    service_level_impact = sum((item.service_level - 0.94) * item.actual_qty for item in items)
    stock_cost_impact = -sum(item.overstock_value for item in items) * 0.02
    lost_sales_impact = sum(item.lost_sales_value for item in items) * 0.03
    waste_impact = -sum(item.waste_value for item in items) * 0.05
    total = service_level_impact + stock_cost_impact + lost_sales_impact + waste_impact
    return BusinessValueSummary(
        service_level_impact=service_level_impact,
        stock_cost_impact=stock_cost_impact,
        lost_sales_impact=lost_sales_impact,
        waste_impact=waste_impact,
        total_business_value=total,
    )


@router.get("/dashboard")
def get_kpi_dashboard(
    region: str | None = Query(default=None),
    category_id: str | None = Query(default=None),
    store_id: str | None = Query(default=None),
    sku_id: str | None = Query(default=None),
) -> dict[str, object]:
    items = list(KPI_ITEMS)
    if region is not None:
        items = [item for item in items if item.segment.region == region]
    if category_id is not None:
        items = [item for item in items if item.segment.category_id == category_id]
    if store_id is not None:
        items = [item for item in items if item.segment.store_id == store_id]
    if sku_id is not None:
        items = [item for item in items if item.segment.sku_id == sku_id]
    dashboard = KpiDashboard(
        filters={
            "networks": ["OPEN_FNR_NETWORK"],
            "regions": ["all", "north"],
            "categories": ["all", "fresh"],
            "stores": ["S001"],
            "skus": ["SKU001"],
        },
        items=items,
        business_value=build_business_value(items),
    )
    return dashboard.model_dump(mode="json")


@router.get("/segments/{segment_id}")
def get_kpi_segment(segment_id: str) -> dict[str, object]:
    item = next((kpi for kpi in KPI_ITEMS if kpi.segment_id == segment_id), None)
    if item is None:
        return {"item": None}
    return item.model_dump(mode="json")
