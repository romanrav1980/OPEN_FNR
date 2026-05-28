from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field


class ModelStatus(StrEnum):
    CANDIDATE = "candidate"
    BACKTESTED = "backtested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROMOTED = "promoted"


class ModelKind(StrEnum):
    BASELINE = "baseline"
    ML_REGULAR = "ml_regular"


class ModelVersion(BaseModel):
    model_version: str = Field(min_length=1, max_length=128)
    model_kind: ModelKind
    algorithm: str = Field(min_length=1, max_length=128)
    status: ModelStatus
    training_window_start: date
    training_window_end: date
    feature_version: str = Field(min_length=1, max_length=128)
    wape: float = Field(ge=0)
    bias: float
    baseline_wape: float = Field(ge=0)
    baseline_bias: float
    inference_runtime_seconds: int = Field(ge=0)
    fallback_model_version: str | None = Field(default=None, max_length=128)
    registered_at: datetime
    approved_by: str | None = Field(default=None, max_length=128)
    approval_reason: str | None = Field(default=None, max_length=512)


class ModelComparison(BaseModel):
    candidate_model_version: str
    baseline_model_version: str
    wape_delta: float
    bias_delta: float
    candidate_better_than_baseline: bool
    fallback_available: bool


router = APIRouter(prefix="/ml-models", tags=["ml-models"])


MODEL_VERSIONS: tuple[ModelVersion, ...] = (
    ModelVersion(
        model_version="seasonal-naive-v1",
        model_kind=ModelKind.BASELINE,
        algorithm="seasonal_naive",
        status=ModelStatus.PROMOTED,
        training_window_start=date(2025, 11, 1),
        training_window_end=date(2026, 5, 27),
        feature_version="fm-20260528-001",
        wape=0.184,
        bias=-0.012,
        baseline_wape=0.184,
        baseline_bias=-0.012,
        inference_runtime_seconds=420,
        registered_at=datetime(2026, 5, 28, 5, 30, tzinfo=timezone.utc),
    ),
    ModelVersion(
        model_version="lgbm-regular-v1-candidate",
        model_kind=ModelKind.ML_REGULAR,
        algorithm="lightgbm",
        status=ModelStatus.BACKTESTED,
        training_window_start=date(2025, 11, 1),
        training_window_end=date(2026, 5, 27),
        feature_version="fm-20260528-001",
        wape=0.158,
        bias=-0.006,
        baseline_wape=0.184,
        baseline_bias=-0.012,
        inference_runtime_seconds=960,
        fallback_model_version="seasonal-naive-v1",
        registered_at=datetime(2026, 5, 28, 7, 20, tzinfo=timezone.utc),
    ),
)


def compare_with_baseline(candidate: ModelVersion, baseline: ModelVersion) -> ModelComparison:
    return ModelComparison(
        candidate_model_version=candidate.model_version,
        baseline_model_version=baseline.model_version,
        wape_delta=candidate.wape - baseline.wape,
        bias_delta=abs(candidate.bias) - abs(baseline.bias),
        candidate_better_than_baseline=candidate.wape < baseline.wape and abs(candidate.bias) <= abs(baseline.bias),
        fallback_available=candidate.fallback_model_version == baseline.model_version,
    )


def approve_candidate(model: ModelVersion, approver_role: str, reason: str) -> ModelVersion:
    if approver_role not in {"Forecast Owner", "ML Owner"}:
        raise PermissionError("model approval requires Forecast Owner or ML Owner role")
    if model.wape >= model.baseline_wape:
        raise ValueError("candidate WAPE must be better than baseline")
    return model.model_copy(
        update={
            "status": ModelStatus.APPROVED,
            "approved_by": approver_role,
            "approval_reason": reason,
        },
    )


@router.get("/versions")
def list_model_versions() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in MODEL_VERSIONS], "total": len(MODEL_VERSIONS)}


@router.get("/versions/{model_version}")
def get_model_version(model_version: str = Path(min_length=1)) -> dict[str, object]:
    for version in MODEL_VERSIONS:
        if version.model_version == model_version:
            return version.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="model version not found")


@router.get("/versions/{model_version}/comparison")
def get_model_comparison(model_version: str = Path(min_length=1)) -> dict[str, object]:
    baseline = next(version for version in MODEL_VERSIONS if version.model_kind == ModelKind.BASELINE)
    for candidate in MODEL_VERSIONS:
        if candidate.model_version == model_version:
            return compare_with_baseline(candidate, baseline).model_dump(mode="json")
    raise HTTPException(status_code=404, detail="model version not found")
