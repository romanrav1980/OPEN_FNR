from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field


class FeatureBuildStatus(StrEnum):
    QUEUED = "queued"
    BUILDING = "building"
    VALIDATED = "validated"
    FAILED = "failed"
    PUBLISHED = "published"


class ActiveMatrixSummary(BaseModel):
    business_date: date
    region_id: str
    category_id: str
    active_pairs: int = Field(ge=0)
    stores: int = Field(ge=0)
    skus: int = Field(ge=0)
    excluded_closed_stores: int = Field(ge=0)
    excluded_inactive_skus: int = Field(ge=0)


class FeatureMartVersion(BaseModel):
    feature_version: str = Field(min_length=1, max_length=128)
    business_date: date
    status: FeatureBuildStatus
    input_batch_ids: list[str]
    active_pairs: int = Field(ge=0)
    feature_count: int = Field(ge=0)
    created_at: datetime
    published_at: datetime | None = None
    quality_status: str = Field(min_length=1, max_length=64)


class FeatureDefinition(BaseModel):
    feature_name: str = Field(min_length=1, max_length=128)
    feature_group: str = Field(min_length=1, max_length=64)
    point_in_time_safe: bool
    description: str = Field(min_length=1, max_length=512)


router = APIRouter(prefix="/feature-mart", tags=["feature-mart"])


ACTIVE_MATRIX: tuple[ActiveMatrixSummary, ...] = (
    ActiveMatrixSummary(
        business_date=date(2026, 5, 28),
        region_id="77",
        category_id="fresh",
        active_pairs=820000,
        stores=1480,
        skus=640,
        excluded_closed_stores=12,
        excluded_inactive_skus=48,
    ),
    ActiveMatrixSummary(
        business_date=date(2026, 5, 28),
        region_id="78",
        category_id="grocery",
        active_pairs=1320000,
        stores=1200,
        skus=1800,
        excluded_closed_stores=4,
        excluded_inactive_skus=76,
    ),
)

FEATURE_VERSIONS: tuple[FeatureMartVersion, ...] = (
    FeatureMartVersion(
        feature_version="fm-20260528-001",
        business_date=date(2026, 5, 28),
        status=FeatureBuildStatus.PUBLISHED,
        input_batch_ids=["sales-2026-05-28-pos", "stock-2026-05-28-wms"],
        active_pairs=2140000,
        feature_count=42,
        created_at=datetime(2026, 5, 28, 5, 10, tzinfo=timezone.utc),
        published_at=datetime(2026, 5, 28, 5, 28, tzinfo=timezone.utc),
        quality_status="accepted",
    ),
)

FEATURES: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        feature_name="sales_lag_7d",
        feature_group="lag",
        point_in_time_safe=True,
        description="Sales quantity lagged by seven days.",
    ),
    FeatureDefinition(
        feature_name="sales_rolling_mean_28d",
        feature_group="rolling",
        point_in_time_safe=True,
        description="Rolling mean over completed historical days.",
    ),
    FeatureDefinition(
        feature_name="current_selling_price",
        feature_group="price",
        point_in_time_safe=True,
        description="Selling price known for the forecast generation date.",
    ),
    FeatureDefinition(
        feature_name="stock_available_flag",
        feature_group="stock",
        point_in_time_safe=True,
        description="Flag for positive available on-hand stock.",
    ),
)


@router.get("/active-matrix")
def list_active_matrix() -> dict[str, object]:
    return {
        "items": [item.model_dump(mode="json") for item in ACTIVE_MATRIX],
        "total": len(ACTIVE_MATRIX),
        "active_pairs_total": sum(item.active_pairs for item in ACTIVE_MATRIX),
    }


@router.get("/versions")
def list_feature_versions() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in FEATURE_VERSIONS], "total": len(FEATURE_VERSIONS)}


@router.get("/versions/{feature_version}")
def get_feature_version(feature_version: str = Path(min_length=1)) -> dict[str, object]:
    for version in FEATURE_VERSIONS:
        if version.feature_version == feature_version:
            return version.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="feature version not found")


@router.get("/features")
def list_feature_definitions() -> dict[str, object]:
    return {
        "items": [item.model_dump(mode="json") for item in FEATURES],
        "total": len(FEATURES),
        "point_in_time_safe": all(item.point_in_time_safe for item in FEATURES),
    }
