from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class DataDomain(StrEnum):
    SALES = "sales"
    STOCK = "stock"
    PRICES = "prices"
    PRODUCT_MDM = "product_mdm"
    STORE_MDM = "store_mdm"
    CALENDAR = "calendar"


class BatchStatus(StrEnum):
    WAITING = "waiting"
    LOADED = "loaded"
    FAILED = "failed"
    PARTIAL = "partial"
    ACCEPTED = "accepted"


class DqSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    BLOCKER = "blocker"


class StoreMdmRecord(BaseModel):
    store_id: str = Field(min_length=1, max_length=64)
    store_name: str = Field(min_length=1, max_length=255)
    region_id: str = Field(min_length=1, max_length=64)
    format_id: str = Field(min_length=1, max_length=64)
    timezone: str = Field(default="Europe/Moscow", min_length=1, max_length=64)
    opening_date: date | None = None
    closing_date: date | None = None
    is_active: bool = True


class ProductMdmRecord(BaseModel):
    sku_id: str = Field(min_length=1, max_length=64)
    product_name: str = Field(min_length=1, max_length=255)
    category_id: str = Field(min_length=1, max_length=64)
    brand_id: str | None = Field(default=None, max_length=64)
    uom: str = Field(default="pcs", min_length=1, max_length=16)
    shelf_life_days: int | None = Field(default=None, ge=0)
    is_fresh: bool = False
    is_active: bool = True


class CalendarDayRecord(BaseModel):
    calendar_date: date
    country_code: str = Field(default="RU", min_length=2, max_length=2)
    week_number: int = Field(ge=1, le=53)
    day_of_week: int = Field(ge=1, le=7)
    is_holiday: bool = False
    holiday_name: str | None = Field(default=None, max_length=128)


class SalesRecord(BaseModel):
    business_date: date
    store_id: str = Field(min_length=1, max_length=64)
    sku_id: str = Field(min_length=1, max_length=64)
    sales_qty: float = Field(ge=0)
    sales_amount: float = Field(ge=0)
    receipt_count: int = Field(default=0, ge=0)
    source_system: str = Field(default="POS", min_length=1, max_length=64)


class StockRecord(BaseModel):
    business_date: date
    store_id: str = Field(min_length=1, max_length=64)
    sku_id: str = Field(min_length=1, max_length=64)
    on_hand_qty: float = Field(ge=0)
    reserved_qty: float = Field(default=0, ge=0)
    in_transit_qty: float = Field(default=0, ge=0)
    source_system: str = Field(default="WMS", min_length=1, max_length=64)


class PriceRecord(BaseModel):
    business_date: date
    store_id: str = Field(min_length=1, max_length=64)
    sku_id: str = Field(min_length=1, max_length=64)
    regular_price: float = Field(gt=0)
    selling_price: float = Field(gt=0)
    currency: str = Field(default="RUB", min_length=3, max_length=3)
    source_system: str = Field(default="ERP", min_length=1, max_length=64)

    @field_validator("selling_price")
    @classmethod
    def selling_price_is_not_extreme(cls, value: float, info: Any) -> float:
        regular_price = info.data.get("regular_price")
        if regular_price and value > regular_price * 10:
            msg = "selling_price must not exceed regular_price by more than 10x"
            raise ValueError(msg)
        return value


class IngestionBatch(BaseModel):
    batch_id: str = Field(min_length=1, max_length=128)
    domain: DataDomain
    business_date: date
    source_system: str = Field(min_length=1, max_length=64)
    status: BatchStatus
    row_count: int = Field(ge=0)
    checksum: str = Field(min_length=1, max_length=128)
    severity: DqSeverity = DqSeverity.INFO
    message: str | None = Field(default=None, max_length=512)
    loaded_at: datetime


class SourceBatchManifest(BaseModel):
    batch_id: str = Field(min_length=1, max_length=128)
    source_system: str = Field(min_length=1, max_length=64)
    contract_name: str = Field(min_length=1, max_length=128)
    contract_version: str = Field(min_length=1, max_length=32)
    business_date: date
    row_count: int = Field(ge=0)
    checksum: str = Field(min_length=1, max_length=128)
    idempotency_key: str = Field(min_length=1, max_length=256)
    landed_uri: str = Field(min_length=1, max_length=512)


class PosSalesLine(BaseModel):
    receipt_id: str = Field(min_length=1, max_length=128)
    line_id: str = Field(min_length=1, max_length=128)
    business_date: date
    store_id: str = Field(min_length=1, max_length=64)
    sku_id: str = Field(min_length=1, max_length=64)
    sales_qty: float
    gross_amount: float = Field(ge=0)
    net_amount: float = Field(ge=0)
    discount_amount: float = Field(default=0, ge=0)
    currency: str = Field(default="RUB", min_length=3, max_length=3)
    source_system: str = Field(default="POS", min_length=1, max_length=64)

    @field_validator("sales_qty")
    @classmethod
    def sales_qty_can_only_be_negative_for_returns(cls, value: float) -> float:
        if value == 0:
            msg = "sales_qty must be non-zero for POS line"
            raise ValueError(msg)
        return value


class WmsStockSnapshotLine(BaseModel):
    snapshot_id: str = Field(min_length=1, max_length=128)
    snapshot_at: datetime
    business_date: date
    location_id: str = Field(min_length=1, max_length=64)
    location_type: str = Field(min_length=1, max_length=32)
    sku_id: str = Field(min_length=1, max_length=64)
    on_hand_qty: float = Field(ge=0)
    reserved_qty: float = Field(default=0, ge=0)
    available_qty: float = Field(ge=0)
    damaged_qty: float = Field(default=0, ge=0)
    source_system: str = Field(default="WMS", min_length=1, max_length=64)

    @field_validator("available_qty")
    @classmethod
    def available_qty_cannot_exceed_physical_stock(cls, value: float, info: Any) -> float:
        on_hand_qty = info.data.get("on_hand_qty")
        if on_hand_qty is not None and value > on_hand_qty:
            msg = "available_qty must not exceed on_hand_qty"
            raise ValueError(msg)
        return value


class WmsOpenOrderLine(BaseModel):
    order_id: str = Field(min_length=1, max_length=128)
    line_id: str = Field(min_length=1, max_length=128)
    order_date: date
    expected_delivery_date: date
    source_location_id: str = Field(min_length=1, max_length=64)
    target_location_id: str = Field(min_length=1, max_length=64)
    sku_id: str = Field(min_length=1, max_length=64)
    ordered_qty: float = Field(gt=0)
    confirmed_qty: float = Field(default=0, ge=0)
    status: str = Field(min_length=1, max_length=64)
    source_system: str = Field(default="WMS", min_length=1, max_length=64)


class WmsInTransitLine(BaseModel):
    shipment_id: str = Field(min_length=1, max_length=128)
    line_id: str = Field(min_length=1, max_length=128)
    ship_date: date
    eta_date: date
    source_location_id: str = Field(min_length=1, max_length=64)
    target_location_id: str = Field(min_length=1, max_length=64)
    sku_id: str = Field(min_length=1, max_length=64)
    shipped_qty: float = Field(gt=0)
    received_qty: float = Field(default=0, ge=0)
    status: str = Field(min_length=1, max_length=64)
    source_system: str = Field(default="WMS", min_length=1, max_length=64)


class ErpPriceLine(BaseModel):
    price_id: str = Field(min_length=1, max_length=128)
    sku_id: str = Field(min_length=1, max_length=64)
    location_scope: str = Field(min_length=1, max_length=64)
    valid_from: date
    valid_to: date | None = None
    regular_price: float = Field(gt=0)
    selling_price: float = Field(gt=0)
    currency: str = Field(default="RUB", min_length=3, max_length=3)
    vat_rate: float = Field(default=0, ge=0, le=1)
    source_system: str = Field(default="ERP", min_length=1, max_length=64)

    @field_validator("selling_price")
    @classmethod
    def erp_selling_price_is_not_extreme(cls, value: float, info: Any) -> float:
        regular_price = info.data.get("regular_price")
        if regular_price and value > regular_price * 10:
            msg = "selling_price must not exceed regular_price by more than 10x"
            raise ValueError(msg)
        return value


class ErpOrderExportStatusLine(BaseModel):
    export_id: str = Field(min_length=1, max_length=128)
    proposal_id: str = Field(min_length=1, max_length=128)
    external_order_id: str | None = Field(default=None, max_length=128)
    exported_at: datetime
    target_system: str = Field(min_length=1, max_length=64)
    status: str = Field(min_length=1, max_length=64)
    retry_count: int = Field(default=0, ge=0)
    error_code: str | None = Field(default=None, max_length=64)
    error_message: str | None = Field(default=None, max_length=512)
    source_system: str = Field(default="ERP", min_length=1, max_length=64)


class MdmProductLine(BaseModel):
    sku_id: str = Field(min_length=1, max_length=64)
    product_name: str = Field(min_length=1, max_length=255)
    category_id: str = Field(min_length=1, max_length=64)
    category_path: str = Field(min_length=1, max_length=512)
    brand_id: str | None = Field(default=None, max_length=64)
    supplier_id: str | None = Field(default=None, max_length=64)
    uom: str = Field(default="pcs", min_length=1, max_length=16)
    shelf_life_days: int | None = Field(default=None, ge=0)
    lifecycle_status: str = Field(default="active", min_length=1, max_length=64)
    replacement_sku_id: str | None = Field(default=None, max_length=64)
    is_fresh: bool = False
    is_active: bool = True
    source_system: str = Field(default="MDM", min_length=1, max_length=64)


class MdmStoreLine(BaseModel):
    store_id: str = Field(min_length=1, max_length=64)
    store_name: str = Field(min_length=1, max_length=255)
    region_id: str = Field(min_length=1, max_length=64)
    format_id: str = Field(min_length=1, max_length=64)
    timezone: str = Field(default="Europe/Moscow", min_length=1, max_length=64)
    opening_date: date | None = None
    closing_date: date | None = None
    replenishment_calendar_id: str | None = Field(default=None, max_length=64)
    warehouse_id: str | None = Field(default=None, max_length=64)
    is_active: bool = True
    source_system: str = Field(default="MDM", min_length=1, max_length=64)


class PromoPlanLine(BaseModel):
    promo_id: str = Field(min_length=1, max_length=128)
    promo_name: str = Field(min_length=1, max_length=255)
    sku_id: str = Field(min_length=1, max_length=64)
    store_scope_id: str = Field(min_length=1, max_length=128)
    date_from: date
    date_to: date
    regular_price: float = Field(gt=0)
    promo_price: float = Field(gt=0)
    discount_pct: float = Field(ge=0, le=1)
    display_type: str | None = Field(default=None, max_length=64)
    display_location: str | None = Field(default=None, max_length=128)
    display_capacity_units: float | None = Field(default=None, ge=0)
    mechanics: str | None = Field(default=None, max_length=128)
    forecast_lock: bool = False
    source_system: str = Field(default="PROMO", min_length=1, max_length=64)

    @field_validator("promo_price")
    @classmethod
    def promo_price_cannot_exceed_regular_price(cls, value: float, info: Any) -> float:
        regular_price = info.data.get("regular_price")
        if regular_price is not None and value > regular_price:
            msg = "promo_price must not exceed regular_price"
            raise ValueError(msg)
        return value


SCHEMA_REGISTRY: dict[DataDomain, type[BaseModel]] = {
    DataDomain.SALES: PosSalesLine,
    DataDomain.STOCK: WmsStockSnapshotLine,
    DataDomain.PRICES: ErpPriceLine,
    DataDomain.PRODUCT_MDM: MdmProductLine,
    DataDomain.STORE_MDM: MdmStoreLine,
    DataDomain.CALENDAR: CalendarDayRecord,
}


def contract_summaries() -> list[dict[str, Any]]:
    return [
        {
            "domain": domain.value,
            "model": model.__name__,
            "schema": model.model_json_schema(),
        }
        for domain, model in SCHEMA_REGISTRY.items()
    ]
