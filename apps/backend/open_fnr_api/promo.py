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
