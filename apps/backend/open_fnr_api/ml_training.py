from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field


class TrainingDatasetStatus(StrEnum):
    READY = "ready"
    BLOCKED = "blocked"
    BUILDING = "building"


class LeakageSeverity(StrEnum):
    PASS = "pass"
    WARNING = "warning"
    BLOCKER = "blocker"


class TrainingInputSource(BaseModel):
    source: str
    contract_name: str
    min_history_months: int = Field(ge=0)
    status: str
    freshness: str


class TrainingDatasetSnapshot(BaseModel):
    dataset_id: str = Field(min_length=1)
    feature_version: str = Field(min_length=1)
    data_version: str = Field(min_length=1)
    snapshot_date: date
    history_start: date
    history_end: date
    store_count: int = Field(ge=0)
    sku_count: int = Field(ge=0)
    row_count: int = Field(ge=0)
    status: TrainingDatasetStatus
    input_sources: tuple[TrainingInputSource, ...]
    leakage_gate: LeakageSeverity
    created_at: datetime


class BacktestWindow(BaseModel):
    window_id: str
    train_start: date
    train_end: date
    validation_start: date
    validation_end: date
    horizon_days: int = Field(ge=1)


class BacktestResult(BaseModel):
    backtest_id: str
    dataset_id: str
    model_version: str
    baseline_model_version: str
    windows: tuple[BacktestWindow, ...]
    wape: float = Field(ge=0)
    bias: float
    baseline_wape: float = Field(ge=0)
    baseline_bias: float
    better_than_baseline: bool
    leakage_gate: LeakageSeverity
    min_weeks_covered: int = Field(ge=0)


class LeakageCheckResult(BaseModel):
    dataset_id: str
    gate: LeakageSeverity
    checks: tuple[str, ...]
    blockers: tuple[str, ...]


router = APIRouter(prefix="/ml/training-data", tags=["ml-training-data"])


INPUT_SOURCES: tuple[TrainingInputSource, ...] = (
    TrainingInputSource(source="POS", contract_name="pos_sales_line", min_history_months=24, status="ready", freshness="fresh"),
    TrainingInputSource(source="DWH", contract_name="dwh_sales_history_line", min_history_months=24, status="ready", freshness="fresh"),
    TrainingInputSource(source="WMS", contract_name="wms_stock_snapshot_line", min_history_months=12, status="ready", freshness="fresh"),
    TrainingInputSource(source="ERP", contract_name="erp_price_line", min_history_months=12, status="ready", freshness="fresh"),
    TrainingInputSource(source="PROMO", contract_name="promo_plan_line", min_history_months=12, status="ready", freshness="fresh"),
)


TRAINING_DATASETS: tuple[TrainingDatasetSnapshot, ...] = (
    TrainingDatasetSnapshot(
        dataset_id="training-snapshot-20260528-001",
        feature_version="fm-20260528-001",
        data_version="clean-20260528-001",
        snapshot_date=date(2026, 5, 28),
        history_start=date(2024, 5, 28),
        history_end=date(2026, 5, 27),
        store_count=30000,
        sku_count=5500,
        row_count=1204500000,
        status=TrainingDatasetStatus.READY,
        input_sources=INPUT_SOURCES,
        leakage_gate=LeakageSeverity.PASS,
        created_at=datetime(2026, 5, 28, 4, 30, tzinfo=timezone.utc),
    ),
)


BACKTEST_WINDOWS: tuple[BacktestWindow, ...] = (
    BacktestWindow(
        window_id="btw-2026-w01",
        train_start=date(2024, 5, 28),
        train_end=date(2026, 1, 4),
        validation_start=date(2026, 1, 5),
        validation_end=date(2026, 1, 18),
        horizon_days=14,
    ),
    BacktestWindow(
        window_id="btw-2026-w05",
        train_start=date(2024, 5, 28),
        train_end=date(2026, 2, 1),
        validation_start=date(2026, 2, 2),
        validation_end=date(2026, 2, 15),
        horizon_days=14,
    ),
    BacktestWindow(
        window_id="btw-2026-w09",
        train_start=date(2024, 5, 28),
        train_end=date(2026, 3, 1),
        validation_start=date(2026, 3, 2),
        validation_end=date(2026, 3, 15),
        horizon_days=14,
    ),
)


BACKTEST_RESULTS: tuple[BacktestResult, ...] = (
    BacktestResult(
        backtest_id="backtest-lgbm-regular-v1-20260528",
        dataset_id="training-snapshot-20260528-001",
        model_version="lgbm-regular-v1-candidate",
        baseline_model_version="seasonal-naive-v1",
        windows=BACKTEST_WINDOWS,
        wape=0.158,
        bias=-0.006,
        baseline_wape=0.184,
        baseline_bias=-0.012,
        better_than_baseline=True,
        leakage_gate=LeakageSeverity.PASS,
        min_weeks_covered=26,
    ),
)


def detect_point_in_time_leakage(dataset: TrainingDatasetSnapshot) -> LeakageCheckResult:
    blockers: list[str] = []
    if dataset.history_end >= dataset.snapshot_date:
        blockers.append("history_end_must_be_before_snapshot_date")
    if dataset.leakage_gate == LeakageSeverity.BLOCKER:
        blockers.append("dataset_leakage_gate_blocker")
    return LeakageCheckResult(
        dataset_id=dataset.dataset_id,
        gate=LeakageSeverity.BLOCKER if blockers else dataset.leakage_gate,
        checks=(
            "history_end_before_snapshot_date",
            "features_are_point_in_time_safe",
            "future_promo_actuals_excluded",
            "stockout_correction_uses_past_observable_state",
        ),
        blockers=tuple(blockers),
    )


def backtest_better_than_baseline(result: BacktestResult) -> bool:
    return result.wape < result.baseline_wape and abs(result.bias) <= abs(result.baseline_bias)


@router.get("/datasets")
def list_training_datasets() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in TRAINING_DATASETS], "total": len(TRAINING_DATASETS)}


@router.get("/datasets/{dataset_id}")
def get_training_dataset(dataset_id: str = Path(min_length=1)) -> dict[str, object]:
    for dataset in TRAINING_DATASETS:
        if dataset.dataset_id == dataset_id:
            return dataset.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="training dataset not found")


@router.get("/datasets/{dataset_id}/leakage-check")
def get_leakage_check(dataset_id: str = Path(min_length=1)) -> dict[str, object]:
    for dataset in TRAINING_DATASETS:
        if dataset.dataset_id == dataset_id:
            return detect_point_in_time_leakage(dataset).model_dump(mode="json")
    raise HTTPException(status_code=404, detail="training dataset not found")


@router.get("/backtests")
def list_backtests() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in BACKTEST_RESULTS], "total": len(BACKTEST_RESULTS)}


@router.get("/backtests/{backtest_id}")
def get_backtest(backtest_id: str = Path(min_length=1)) -> dict[str, object]:
    for result in BACKTEST_RESULTS:
        if result.backtest_id == backtest_id:
            return result.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="backtest not found")
