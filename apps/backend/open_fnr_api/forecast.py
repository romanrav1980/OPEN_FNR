from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field


class ForecastStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SCORED = "scored"
    VALIDATED = "validated"
    PUBLISHED = "published"
    FAILED = "failed"


class ForecastVersion(BaseModel):
    forecast_version: str = Field(min_length=1, max_length=128)
    run_date: date
    horizon_days: int = Field(ge=1, le=365)
    status: ForecastStatus
    model_version: str = Field(min_length=1, max_length=128)
    data_version: str = Field(min_length=1, max_length=128)
    feature_version: str = Field(min_length=1, max_length=128)
    rows: int = Field(ge=0)
    wape: float = Field(ge=0)
    bias: float
    created_at: datetime
    published_at: datetime | None = None


class ForecastRow(BaseModel):
    forecast_version: str
    forecast_date: date
    store_id: str
    sku_id: str
    regular_forecast_qty: float = Field(ge=0)
    promo_uplift_forecast_qty: float = Field(default=0, ge=0)
    total_forecast_qty: float = Field(ge=0)
    quality_flag: str
    category_id: str = "fresh"
    actual_qty: float | None = Field(default=None, ge=0)


class ForecastSliceSummary(BaseModel):
    forecast_version: str
    total_rows: int = Field(ge=0)
    total_forecast_qty: float = Field(ge=0)
    total_actual_qty: float = Field(ge=0)
    wape: float = Field(ge=0)
    bias: float


router = APIRouter(prefix="/forecast", tags=["forecast"])


def calculate_wape(actual: list[float], forecast: list[float]) -> float:
    denominator = sum(abs(value) for value in actual)
    if denominator == 0:
        return 0.0
    numerator = sum(abs(a - f) for a, f in zip(actual, forecast, strict=True))
    return numerator / denominator


def calculate_bias(actual: list[float], forecast: list[float]) -> float:
    denominator = sum(actual)
    if denominator == 0:
        return 0.0
    return sum(forecast) / denominator - 1


FORECAST_VERSIONS: tuple[ForecastVersion, ...] = (
    ForecastVersion(
        forecast_version="regular-baseline-20260528-001",
        run_date=date(2026, 5, 28),
        horizon_days=30,
        status=ForecastStatus.PUBLISHED,
        model_version="seasonal-naive-v1",
        data_version="clean-20260528-001",
        feature_version="fm-20260528-001",
        rows=64200000,
        wape=0.184,
        bias=-0.012,
        created_at=datetime(2026, 5, 28, 5, 40, tzinfo=timezone.utc),
        published_at=datetime(2026, 5, 28, 6, 5, tzinfo=timezone.utc),
    ),
)

FORECAST_ROWS: tuple[ForecastRow, ...] = (
    ForecastRow(
        forecast_version="regular-baseline-20260528-001",
        forecast_date=date(2026, 5, 29),
        store_id="S001",
        sku_id="SKU001",
        regular_forecast_qty=12.4,
        total_forecast_qty=12.4,
        quality_flag="ok",
        actual_qty=11.0,
    ),
    ForecastRow(
        forecast_version="regular-baseline-20260528-001",
        forecast_date=date(2026, 5, 29),
        store_id="S001",
        sku_id="SKU002",
        regular_forecast_qty=4.8,
        total_forecast_qty=4.8,
        quality_flag="low_history",
        actual_qty=5.5,
    ),
)


def summarize_forecast_slice(rows: list[ForecastRow]) -> ForecastSliceSummary:
    actual = [row.actual_qty or 0 for row in rows]
    forecast = [row.total_forecast_qty for row in rows]
    return ForecastSliceSummary(
        forecast_version=rows[0].forecast_version if rows else "",
        total_rows=len(rows),
        total_forecast_qty=sum(forecast),
        total_actual_qty=sum(actual),
        wape=calculate_wape(actual, forecast),
        bias=calculate_bias(actual, forecast),
    )


@router.get("/versions")
def list_forecast_versions() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in FORECAST_VERSIONS], "total": len(FORECAST_VERSIONS)}


@router.get("/versions/latest")
def latest_forecast_version() -> dict[str, object]:
    latest = max(FORECAST_VERSIONS, key=lambda item: item.created_at)
    return latest.model_dump(mode="json")


@router.get("/versions/{forecast_version}/rows")
def list_forecast_rows(forecast_version: str = Path(min_length=1)) -> dict[str, object]:
    rows = [row for row in FORECAST_ROWS if row.forecast_version == forecast_version]
    if not rows:
        raise HTTPException(status_code=404, detail="forecast version not found")
    return {"items": [row.model_dump(mode="json") for row in rows], "total": len(rows)}


@router.get("/workbench")
def forecast_workbench_slice(
    forecast_version: str = Query(default="regular-baseline-20260528-001", min_length=1),
    store_id: str | None = None,
    sku_id: str | None = None,
    category_id: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict[str, object]:
    rows = [row for row in FORECAST_ROWS if row.forecast_version == forecast_version]
    if store_id is not None:
        rows = [row for row in rows if row.store_id == store_id]
    if sku_id is not None:
        rows = [row for row in rows if row.sku_id == sku_id]
    if category_id is not None:
        rows = [row for row in rows if row.category_id == category_id]
    if not rows:
        return {
            "items": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "summary": ForecastSliceSummary(
                forecast_version=forecast_version,
                total_rows=0,
                total_forecast_qty=0,
                total_actual_qty=0,
                wape=0,
                bias=0,
            ).model_dump(mode="json"),
        }
    page = rows[offset : offset + limit]
    return {
        "items": [row.model_dump(mode="json") for row in page],
        "total": len(rows),
        "limit": limit,
        "offset": offset,
        "summary": summarize_forecast_slice(rows).model_dump(mode="json"),
    }
