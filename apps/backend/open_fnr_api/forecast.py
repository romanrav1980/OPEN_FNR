from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path
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
    ),
    ForecastRow(
        forecast_version="regular-baseline-20260528-001",
        forecast_date=date(2026, 5, 29),
        store_id="S001",
        sku_id="SKU002",
        regular_forecast_qty=4.8,
        total_forecast_qty=4.8,
        quality_flag="low_history",
    ),
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
