from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field, model_validator


class PromoStatus(StrEnum):
    DRAFT = "draft"
    DATA_INCOMPLETE = "data_incomplete"
    READY_FOR_FORECAST = "ready_for_forecast"
    CONFLICT = "conflict"


class PromoMechanic(StrEnum):
    DISCOUNT = "discount"
    MULTIBUY = "multibuy"
    BUNDLE = "bundle"
    LOYALTY = "loyalty"


class PromoDisplayLocation(StrEnum):
    REGULAR_SHELF = "regular_shelf"
    END_CAP = "end_cap"
    ISLAND = "island"
    CHECKOUT = "checkout"


class PromoPlan(BaseModel):
    promo_id: str = Field(min_length=1, max_length=128)
    sku_ids: list[str] = Field(min_length=1)
    store_ids: list[str] = Field(min_length=1)
    start_date: date
    end_date: date
    mechanic: PromoMechanic
    regular_price: float = Field(gt=0)
    promo_price: float = Field(gt=0)
    discount_percent: float = Field(ge=0, le=100)
    display_location: PromoDisplayLocation
    display_capacity_units: int = Field(gt=0)
    status: PromoStatus
    created_by: str = Field(min_length=1, max_length=128)
    updated_at: datetime

    @model_validator(mode="after")
    def validate_dates_and_prices(self) -> "PromoPlan":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")
        if self.promo_price > self.regular_price:
            raise ValueError("promo_price must not exceed regular_price")
        return self


class PromoValidationResult(BaseModel):
    promo_id: str
    status: PromoStatus
    ready_for_forecast: bool
    errors: list[str]
    warnings: list[str]


class PromoForecastStatus(StrEnum):
    READY_FOR_FORECAST = "ready_for_forecast"
    FORECASTING = "forecasting"
    FORECASTED = "forecasted"
    FORECAST_WARNING = "forecast_warning"


class ReferencePromo(BaseModel):
    promo_id: str
    similarity_score: float = Field(ge=0, le=1)
    mechanic: PromoMechanic
    discount_percent: float = Field(ge=0, le=100)
    uplift_factor: float = Field(ge=0)


class PromoForecastDay(BaseModel):
    promo_id: str
    forecast_date: date
    regular_forecast_qty: float = Field(ge=0)
    promo_uplift_qty: float = Field(ge=0)
    total_forecast_qty: float = Field(ge=0)
    post_promo_stock_qty: float = Field(ge=0)


class PromoForecast(BaseModel):
    promo_id: str
    status: PromoForecastStatus
    regular_forecast_version: str
    uplift_version: str
    reference_promos: list[ReferencePromo]
    days: list[PromoForecastDay]
    uplift_accuracy_smoke: float = Field(ge=0, le=1)
    warning: str | None = None


class PromoApprovalStatus(StrEnum):
    CATEGORY_REVIEW = "category_review"
    SUPPLY_REVIEW = "supply_review"
    APPROVED = "approved"
    REWORK = "rework"
    REJECTED = "rejected"


class PromoRiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PromoApprovalStep(BaseModel):
    step_id: str
    role: str
    status: PromoApprovalStatus
    allowed_actions: list[str]
    sla_due_at: datetime
    decision_by: str | None = None
    decision_comment: str | None = None


class PromoApproval(BaseModel):
    promo_id: str
    process_instance_id: str
    status: PromoApprovalStatus
    risk_level: PromoRiskLevel
    risk_reasons: list[str]
    route: list[str]
    blocking_errors: list[str]
    steps: list[PromoApprovalStep]
    publication_ready: bool


router = APIRouter(prefix="/promo", tags=["promo"])


PROMOS: tuple[PromoPlan, ...] = (
    PromoPlan(
        promo_id="promo-20260601-fresh-001",
        sku_ids=["SKU001", "SKU002"],
        store_ids=["S001", "S002"],
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 7),
        mechanic=PromoMechanic.DISCOUNT,
        regular_price=149.90,
        promo_price=119.90,
        discount_percent=20.0,
        display_location=PromoDisplayLocation.END_CAP,
        display_capacity_units=120,
        status=PromoStatus.READY_FOR_FORECAST,
        created_by="Promo Planner",
        updated_at=datetime(2026, 5, 28, 9, 0, tzinfo=timezone.utc),
    ),
    PromoPlan(
        promo_id="promo-20260605-grocery-002",
        sku_ids=["SKU010"],
        store_ids=["S001"],
        start_date=date(2026, 6, 5),
        end_date=date(2026, 6, 12),
        mechanic=PromoMechanic.MULTIBUY,
        regular_price=89.90,
        promo_price=79.90,
        discount_percent=11.0,
        display_location=PromoDisplayLocation.ISLAND,
        display_capacity_units=80,
        status=PromoStatus.CONFLICT,
        created_by="Promo Planner",
        updated_at=datetime(2026, 5, 28, 9, 30, tzinfo=timezone.utc),
    ),
)

PROMO_FORECASTS: tuple[PromoForecast, ...] = (
    PromoForecast(
        promo_id="promo-20260601-fresh-001",
        status=PromoForecastStatus.FORECASTED,
        regular_forecast_version="regular-baseline-20260528-001",
        uplift_version="promo-uplift-v1-20260528",
        reference_promos=[
            ReferencePromo(
                promo_id="promo-ref-202505-fresh-011",
                similarity_score=0.91,
                mechanic=PromoMechanic.DISCOUNT,
                discount_percent=20,
                uplift_factor=0.42,
            ),
            ReferencePromo(
                promo_id="promo-ref-202504-fresh-007",
                similarity_score=0.84,
                mechanic=PromoMechanic.DISCOUNT,
                discount_percent=18,
                uplift_factor=0.37,
            ),
        ],
        days=[
            PromoForecastDay(
                promo_id="promo-20260601-fresh-001",
                forecast_date=date(2026, 6, 1),
                regular_forecast_qty=120,
                promo_uplift_qty=48,
                total_forecast_qty=168,
                post_promo_stock_qty=340,
            ),
            PromoForecastDay(
                promo_id="promo-20260601-fresh-001",
                forecast_date=date(2026, 6, 2),
                regular_forecast_qty=118,
                promo_uplift_qty=45,
                total_forecast_qty=163,
                post_promo_stock_qty=290,
            ),
        ],
        uplift_accuracy_smoke=0.82,
    ),
)

PROMO_APPROVALS: tuple[PromoApproval, ...] = (
    PromoApproval(
        promo_id="promo-20260601-fresh-001",
        process_instance_id="proc-promo-approval-20260601-001",
        status=PromoApprovalStatus.CATEGORY_REVIEW,
        risk_level=PromoRiskLevel.MEDIUM,
        risk_reasons=["discount over 15%", "post-promo stock remains above safety threshold"],
        route=["Category Manager", "Supply Chain Manager"],
        blocking_errors=[],
        steps=[
            PromoApprovalStep(
                step_id="category-review",
                role="Category Manager",
                status=PromoApprovalStatus.CATEGORY_REVIEW,
                allowed_actions=["approve", "reject", "request_rework", "comment"],
                sla_due_at=datetime(2026, 5, 29, 9, 0, tzinfo=timezone.utc),
            ),
            PromoApprovalStep(
                step_id="supply-review",
                role="Supply Chain Manager",
                status=PromoApprovalStatus.SUPPLY_REVIEW,
                allowed_actions=["approve", "reject", "request_rework", "escalate", "comment"],
                sla_due_at=datetime(2026, 5, 28, 17, 0, tzinfo=timezone.utc),
            ),
        ],
        publication_ready=False,
    ),
    PromoApproval(
        promo_id="promo-20260605-grocery-002",
        process_instance_id="proc-promo-approval-20260605-002",
        status=PromoApprovalStatus.REWORK,
        risk_level=PromoRiskLevel.HIGH,
        risk_reasons=["overlapping promo", "display capacity below forecasted uplift"],
        route=["Category Manager", "Supply Chain Manager"],
        blocking_errors=["overlaps with promo-20260601-fresh-001"],
        steps=[
            PromoApprovalStep(
                step_id="category-rework",
                role="Promo Planner",
                status=PromoApprovalStatus.REWORK,
                allowed_actions=["resubmit", "cancel", "comment"],
                sla_due_at=datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc),
            ),
        ],
        publication_ready=False,
    ),
)


def build_total_forecast(regular_forecast_qty: float, promo_uplift_qty: float) -> float:
    return regular_forecast_qty + promo_uplift_qty


def classify_promo_risk(discount_percent: float, uplift_factor: float, post_promo_stock_qty: float) -> PromoRiskLevel:
    if discount_percent >= 30 or uplift_factor >= 0.75 or post_promo_stock_qty < 50:
        return PromoRiskLevel.HIGH
    if discount_percent >= 15 or uplift_factor >= 0.35 or post_promo_stock_qty < 150:
        return PromoRiskLevel.MEDIUM
    return PromoRiskLevel.LOW


def validate_promo(plan: PromoPlan) -> PromoValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if not plan.sku_ids:
        errors.append("sku_ids are required")
    if not plan.store_ids:
        errors.append("store_ids are required")
    if plan.discount_percent == 0:
        warnings.append("discount_percent is zero")
    if plan.display_capacity_units < len(plan.sku_ids) * 10:
        warnings.append("display_capacity_units may be too low for selected SKU count")
    for other in PROMOS:
        if other.promo_id == plan.promo_id:
            continue
        same_store = set(plan.store_ids) & set(other.store_ids)
        same_sku = set(plan.sku_ids) & set(other.sku_ids)
        overlap = plan.start_date <= other.end_date and other.start_date <= plan.end_date
        if same_store and same_sku and overlap:
            errors.append(f"overlaps with {other.promo_id}")

    status = PromoStatus.READY_FOR_FORECAST if not errors else PromoStatus.CONFLICT
    return PromoValidationResult(
        promo_id=plan.promo_id,
        status=status,
        ready_for_forecast=not errors,
        errors=errors,
        warnings=warnings,
    )


@router.get("/plans")
def list_promo_plans() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in PROMOS], "total": len(PROMOS)}


@router.get("/plans/{promo_id}")
def get_promo_plan(promo_id: str = Path(min_length=1)) -> dict[str, object]:
    for promo in PROMOS:
        if promo.promo_id == promo_id:
            return promo.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="promo not found")


@router.get("/plans/{promo_id}/validation")
def get_promo_validation(promo_id: str = Path(min_length=1)) -> dict[str, object]:
    for promo in PROMOS:
        if promo.promo_id == promo_id:
            return validate_promo(promo).model_dump(mode="json")
    raise HTTPException(status_code=404, detail="promo not found")


@router.get("/forecasts")
def list_promo_forecasts() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in PROMO_FORECASTS], "total": len(PROMO_FORECASTS)}


@router.get("/forecasts/{promo_id}")
def get_promo_forecast(promo_id: str = Path(min_length=1)) -> dict[str, object]:
    for forecast in PROMO_FORECASTS:
        if forecast.promo_id == promo_id:
            return forecast.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="promo forecast not found")


@router.get("/approvals")
def list_promo_approvals() -> dict[str, object]:
    return {"items": [item.model_dump(mode="json") for item in PROMO_APPROVALS], "total": len(PROMO_APPROVALS)}


@router.get("/approvals/{promo_id}")
def get_promo_approval(promo_id: str = Path(min_length=1)) -> dict[str, object]:
    for approval in PROMO_APPROVALS:
        if approval.promo_id == promo_id:
            return approval.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="promo approval not found")
