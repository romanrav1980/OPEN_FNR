from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field


class TrainingRunStatus(StrEnum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    BACKTESTED = "backtested"
    READY_FOR_RELEASE = "ready_for_release"
    BLOCKED = "blocked"


class TrainingModelType(StrEnum):
    REGULAR_DEMAND = "regular_demand"
    PROMO_UPLIFT = "promo_uplift"


class RetrainingFrequency(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TrainingMetricSet(BaseModel):
    wape: float = Field(ge=0)
    bias: float
    baseline_wape: float = Field(ge=0)
    baseline_bias: float
    backtesting_weeks: int = Field(ge=0)


class ForecastTrainingRun(BaseModel):
    run_id: str
    model_type: TrainingModelType
    model_version: str
    dataset_id: str
    feature_version: str
    algorithm: str
    status: TrainingRunStatus
    metrics: TrainingMetricSet
    fallback_model_version: str
    scheduled_at: datetime
    completed_at: datetime | None
    owner_role: str
    approval_required_role: str


class RetrainingPlan(BaseModel):
    plan_id: str
    model_type: TrainingModelType
    frequency: RetrainingFrequency
    next_run_date: date
    trigger_policy: str
    max_training_runtime_minutes: int = Field(gt=0)
    owner_role: str


class ReleaseReadiness(BaseModel):
    run_id: str
    ready: bool
    gates: tuple[str, ...]
    blockers: tuple[str, ...]


router = APIRouter(prefix="/ml/training", tags=["ml-training"])


TRAINING_RUNS: tuple[ForecastTrainingRun, ...] = (
    ForecastTrainingRun(
        run_id="train-regular-lgbm-20260528-001",
        model_type=TrainingModelType.REGULAR_DEMAND,
        model_version="lgbm-regular-v2-candidate",
        dataset_id="training-snapshot-20260528-001",
        feature_version="fm-20260528-001",
        algorithm="hist_gradient_boosting",
        status=TrainingRunStatus.READY_FOR_RELEASE,
        metrics=TrainingMetricSet(wape=0.151, bias=-0.004, baseline_wape=0.184, baseline_bias=-0.012, backtesting_weeks=26),
        fallback_model_version="seasonal-naive-v1",
        scheduled_at=datetime(2026, 5, 28, 7, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 5, 28, 7, 42, tzinfo=timezone.utc),
        owner_role="ML Owner",
        approval_required_role="Forecast Owner",
    ),
    ForecastTrainingRun(
        run_id="train-promo-uplift-20260528-001",
        model_type=TrainingModelType.PROMO_UPLIFT,
        model_version="promo-uplift-v2-candidate",
        dataset_id="training-snapshot-20260528-001",
        feature_version="fm-20260528-001",
        algorithm="regularized_regression",
        status=TrainingRunStatus.BACKTESTED,
        metrics=TrainingMetricSet(wape=0.173, bias=0.008, baseline_wape=0.196, baseline_bias=0.015, backtesting_weeks=26),
        fallback_model_version="promo-uplift-v1",
        scheduled_at=datetime(2026, 5, 28, 7, 15, tzinfo=timezone.utc),
        completed_at=datetime(2026, 5, 28, 7, 51, tzinfo=timezone.utc),
        owner_role="ML Owner",
        approval_required_role="Forecast Owner",
    ),
)


RETRAINING_PLANS: tuple[RetrainingPlan, ...] = (
    RetrainingPlan(
        plan_id="regular-demand-weekly-retraining",
        model_type=TrainingModelType.REGULAR_DEMAND,
        frequency=RetrainingFrequency.WEEKLY,
        next_run_date=date(2026, 6, 1),
        trigger_policy="scheduled_or_drift_warning_or_wape_regression",
        max_training_runtime_minutes=90,
        owner_role="ML Owner",
    ),
    RetrainingPlan(
        plan_id="promo-uplift-weekly-retraining",
        model_type=TrainingModelType.PROMO_UPLIFT,
        frequency=RetrainingFrequency.WEEKLY,
        next_run_date=date(2026, 6, 1),
        trigger_policy="scheduled_or_promo_bias_warning",
        max_training_runtime_minutes=90,
        owner_role="ML Owner",
    ),
)


def release_readiness(run: ForecastTrainingRun) -> ReleaseReadiness:
    blockers: list[str] = []
    if run.metrics.backtesting_weeks < 26:
        blockers.append("backtesting_window_below_26_weeks")
    if run.metrics.wape >= run.metrics.baseline_wape:
        blockers.append("candidate_wape_not_better_than_baseline")
    if abs(run.metrics.bias) > abs(run.metrics.baseline_bias):
        blockers.append("candidate_bias_worse_than_baseline")
    if not run.fallback_model_version:
        blockers.append("fallback_model_missing")
    return ReleaseReadiness(
        run_id=run.run_id,
        ready=not blockers,
        gates=("backtesting_26_weeks", "wape_better_than_baseline", "bias_not_worse", "fallback_available"),
        blockers=tuple(blockers),
    )


@router.get("/runs")
def list_training_runs() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in TRAINING_RUNS], "total": len(TRAINING_RUNS)}


@router.get("/runs/{run_id}")
def get_training_run(run_id: str = Path(min_length=1)) -> dict[str, object]:
    for run in TRAINING_RUNS:
        if run.run_id == run_id:
            return run.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="training run not found")


@router.get("/runs/{run_id}/release-readiness")
def get_training_release_readiness(run_id: str = Path(min_length=1)) -> dict[str, object]:
    for run in TRAINING_RUNS:
        if run.run_id == run_id:
            return release_readiness(run).model_dump(mode="json")
    raise HTTPException(status_code=404, detail="training run not found")


@router.get("/retraining-plan")
def list_retraining_plan() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in RETRAINING_PLANS], "total": len(RETRAINING_PLANS)}
