from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field

from .audit import AuditEventCreate, record_audit_event_if_enabled


class FeatureBuildStatus(StrEnum):
    QUEUED = "queued"
    BUILDING = "building"
    VALIDATED = "validated"
    FAILED = "failed"
    PUBLISHED = "published"


class FeatureBuildMode(StrEnum):
    DRY_RUN = "dry_run"
    MOCK_RUN = "mock_run"


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


class FeatureBuildDependency(BaseModel):
    dependency_name: str = Field(min_length=1, max_length=128)
    source_table: str = Field(min_length=1, max_length=128)
    status: str = Field(min_length=1, max_length=64)
    freshness_status: str = Field(min_length=1, max_length=64)
    expected_min_rows: int = Field(ge=0)


class FeatureBuildPlan(BaseModel):
    plan_id: str = Field(min_length=1, max_length=128)
    business_date: date
    feature_version: str = Field(min_length=1, max_length=128)
    status: FeatureBuildStatus
    output_table: str = Field(min_length=1, max_length=128)
    partition_key: str = Field(min_length=1, max_length=128)
    active_pairs: int = Field(ge=0)
    dependency_count: int = Field(ge=0)
    dependencies: tuple[FeatureBuildDependency, ...]
    validation_rules: tuple[str, ...]
    build_sql: str = Field(min_length=1)


class FeatureBuildRunRequest(BaseModel):
    business_date: date
    actor: str = Field(min_length=1, max_length=128)
    actor_role: str = Field(default="Data Science Owner", min_length=1, max_length=64)
    mode: FeatureBuildMode = FeatureBuildMode.DRY_RUN


class FeatureBuildRunResponse(BaseModel):
    run_id: str
    business_date: date
    mode: FeatureBuildMode
    status: FeatureBuildStatus
    feature_version: str
    dependency_count: int = Field(ge=0)
    validation_status: str
    audit_recorded: bool


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


def feature_build_plan_for_date(business_date: date) -> FeatureBuildPlan:
    date_key = business_date.isoformat().replace("-", "")
    dependencies = (
        FeatureBuildDependency(
            dependency_name="sales_clean_daily",
            source_table="open_fnr.clean_sales_daily",
            status="published",
            freshness_status="fresh",
            expected_min_rows=1,
        ),
        FeatureBuildDependency(
            dependency_name="stock_snapshot_daily",
            source_table="open_fnr.clean_stock_snapshot_daily",
            status="published",
            freshness_status="fresh",
            expected_min_rows=1,
        ),
        FeatureBuildDependency(
            dependency_name="open_orders",
            source_table="open_fnr.clean_open_orders",
            status="published",
            freshness_status="fresh",
            expected_min_rows=0,
        ),
        FeatureBuildDependency(
            dependency_name="in_transit",
            source_table="open_fnr.clean_in_transit",
            status="published",
            freshness_status="fresh",
            expected_min_rows=0,
        ),
        FeatureBuildDependency(
            dependency_name="prices",
            source_table="open_fnr.clean_prices",
            status="published",
            freshness_status="fresh",
            expected_min_rows=1,
        ),
        FeatureBuildDependency(
            dependency_name="promo_plans",
            source_table="open_fnr.clean_promo_plans",
            status="published",
            freshness_status="fresh",
            expected_min_rows=0,
        ),
    )
    active_pairs = sum(item.active_pairs for item in ACTIVE_MATRIX if item.business_date == business_date) or 2140000
    return FeatureBuildPlan(
        plan_id=f"feature-build-{business_date.isoformat()}",
        business_date=business_date,
        feature_version=f"fm-{date_key}-001",
        status=FeatureBuildStatus.QUEUED,
        output_table="open_fnr.feature_store_daily",
        partition_key="business_date",
        active_pairs=active_pairs,
        dependency_count=len(dependencies),
        dependencies=dependencies,
        validation_rules=(
            "all_required_clean_dependencies_published",
            "active_matrix_non_empty",
            "no_future_fact_leakage",
            "feature_null_rate_within_threshold",
            "feature_version_idempotent_for_business_date",
        ),
        build_sql=(
            "INSERT INTO open_fnr.feature_store_daily "
            "SELECT active.business_date, active.store_id, active.sku_id, "
            "sales.sales_qty AS sales_lag_1d, prices.selling_price, stock.available_qty, "
            "now() AS calculated_at "
            "FROM open_fnr.active_matrix active "
            "LEFT JOIN open_fnr.clean_sales_daily sales USING (business_date, store_id, sku_id) "
            "LEFT JOIN open_fnr.clean_prices prices USING (sku_id) "
            "LEFT JOIN open_fnr.clean_stock_snapshot_daily stock USING (business_date, sku_id) "
            f"WHERE active.business_date = '{business_date.isoformat()}'"
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


@router.get("/build-plans")
def list_feature_build_plans(business_date: date) -> dict[str, object]:
    plan = feature_build_plan_for_date(business_date)
    return {"items": [plan.model_dump(mode="json")], "total": 1}


@router.get("/build-plans/{plan_id}")
def get_feature_build_plan(plan_id: str = Path(min_length=1), business_date: date | None = None) -> dict[str, object]:
    plan = feature_build_plan_for_date(business_date or date(2026, 5, 28))
    if plan.plan_id != plan_id:
        raise HTTPException(status_code=404, detail="feature build plan not found")
    return plan.model_dump(mode="json")


@router.post("/build-runs")
def run_feature_build(request: FeatureBuildRunRequest) -> dict[str, object]:
    plan = feature_build_plan_for_date(request.business_date)
    validation_status = "accepted" if all(item.status == "published" for item in plan.dependencies) else "blocked"
    status = FeatureBuildStatus.VALIDATED if request.mode == FeatureBuildMode.DRY_RUN else FeatureBuildStatus.PUBLISHED
    run_id = f"feature-build-{request.business_date.isoformat()}-{request.mode.value}"
    event = record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="feature_build_run",
            actor=request.actor,
            actor_role=request.actor_role,
            object_type="feature_mart",
            object_id=plan.feature_version,
            action=f"run_{request.mode.value}",
            reason=f"status={status.value}; validation={validation_status}",
            correlation_id=run_id,
            payload={
                "business_date": request.business_date.isoformat(),
                "feature_version": plan.feature_version,
                "dependency_count": plan.dependency_count,
                "validation_status": validation_status,
            },
        )
    )
    response = FeatureBuildRunResponse(
        run_id=run_id,
        business_date=request.business_date,
        mode=request.mode,
        status=status,
        feature_version=plan.feature_version,
        dependency_count=plan.dependency_count,
        validation_status=validation_status,
        audit_recorded=event is not None,
    )
    return response.model_dump(mode="json")
