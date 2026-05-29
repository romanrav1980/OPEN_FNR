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


class SourceContractDefinition(BaseModel):
    contract_name: str = Field(min_length=1, max_length=128)
    contract_version: str = Field(default="v1", min_length=1, max_length=32)
    source_system: str = Field(min_length=1, max_length=64)
    model_name: str = Field(min_length=1, max_length=128)
    primary_key: tuple[str, ...]
    required_fields: tuple[str, ...]
    business_owner_role: str = Field(min_length=1, max_length=128)
    technical_owner_role: str = Field(min_length=1, max_length=128)
    source_sla: str = Field(min_length=1, max_length=64)
    freshness_field: str = Field(min_length=1, max_length=64)
    idempotency_fields: tuple[str, ...]
    reconciliation_keys: tuple[str, ...]
    required_for: tuple[str, ...]
    blocking_dq_checks: tuple[str, ...]


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

SOURCE_CONTRACT_MODELS: dict[str, type[BaseModel]] = {
    "pos_sales_line": PosSalesLine,
    "wms_stock_snapshot_line": WmsStockSnapshotLine,
    "wms_open_order_line": WmsOpenOrderLine,
    "wms_in_transit_line": WmsInTransitLine,
    "erp_price_line": ErpPriceLine,
    "erp_order_export_status_line": ErpOrderExportStatusLine,
    "mdm_product_line": MdmProductLine,
    "mdm_store_line": MdmStoreLine,
    "promo_plan_line": PromoPlanLine,
}

SOURCE_CONTRACT_REGISTRY: tuple[SourceContractDefinition, ...] = (
    SourceContractDefinition(
        source_system="POS",
        contract_name="pos_sales_line",
        model_name="PosSalesLine",
        primary_key=("receipt_id", "line_id"),
        required_fields=("receipt_id", "line_id", "business_date", "store_id", "sku_id", "sales_qty", "net_amount"),
        business_owner_role="Sales Data Owner",
        technical_owner_role="Data Engineering",
        source_sla="before_forecast_cutoff",
        freshness_field="business_date",
        idempotency_fields=("source_system", "contract_name", "contract_version", "business_date", "checksum"),
        reconciliation_keys=("business_date", "store_id", "sku_id"),
        required_for=("regular_forecast", "promo_forecast", "demand_projection"),
        blocking_dq_checks=("schema", "row_count", "checksum", "duplicates", "referential_integrity", "freshness"),
    ),
    SourceContractDefinition(
        source_system="WMS",
        contract_name="wms_stock_snapshot_line",
        model_name="WmsStockSnapshotLine",
        primary_key=("snapshot_id", "location_id", "sku_id"),
        required_fields=("snapshot_id", "snapshot_at", "business_date", "location_id", "location_type", "sku_id", "on_hand_qty", "available_qty"),
        business_owner_role="Supply Chain Data Owner",
        technical_owner_role="Data Engineering",
        source_sla="before_replenishment_cutoff",
        freshness_field="snapshot_at",
        idempotency_fields=("source_system", "contract_name", "contract_version", "business_date", "checksum"),
        reconciliation_keys=("business_date", "location_id", "sku_id"),
        required_for=("projected_stock", "replenishment", "true_inventory"),
        blocking_dq_checks=("schema", "row_count", "checksum", "duplicates", "referential_integrity", "freshness", "negative_stock"),
    ),
    SourceContractDefinition(
        source_system="WMS",
        contract_name="wms_open_order_line",
        model_name="WmsOpenOrderLine",
        primary_key=("order_id", "line_id"),
        required_fields=("order_id", "line_id", "order_date", "expected_delivery_date", "target_location_id", "sku_id", "ordered_qty", "status"),
        business_owner_role="Supply Chain Data Owner",
        technical_owner_role="Data Engineering",
        source_sla="before_replenishment_cutoff",
        freshness_field="expected_delivery_date",
        idempotency_fields=("source_system", "contract_name", "contract_version", "business_date", "checksum"),
        reconciliation_keys=("order_id", "line_id", "sku_id"),
        required_for=("projected_stock", "replenishment", "multi_echelon"),
        blocking_dq_checks=("schema", "row_count", "checksum", "duplicates", "referential_integrity", "date_order"),
    ),
    SourceContractDefinition(
        source_system="WMS",
        contract_name="wms_in_transit_line",
        model_name="WmsInTransitLine",
        primary_key=("shipment_id", "line_id"),
        required_fields=("shipment_id", "line_id", "ship_date", "eta_date", "source_location_id", "target_location_id", "sku_id", "shipped_qty", "status"),
        business_owner_role="Supply Chain Data Owner",
        technical_owner_role="Data Engineering",
        source_sla="before_replenishment_cutoff",
        freshness_field="eta_date",
        idempotency_fields=("source_system", "contract_name", "contract_version", "business_date", "checksum"),
        reconciliation_keys=("shipment_id", "line_id", "sku_id"),
        required_for=("projected_stock", "replenishment", "capacity"),
        blocking_dq_checks=("schema", "row_count", "checksum", "duplicates", "referential_integrity", "date_order"),
    ),
    SourceContractDefinition(
        source_system="ERP",
        contract_name="erp_price_line",
        model_name="ErpPriceLine",
        primary_key=("price_id",),
        required_fields=("price_id", "sku_id", "location_scope", "valid_from", "regular_price", "selling_price", "currency"),
        business_owner_role="Commercial Data Owner",
        technical_owner_role="Integration Owner",
        source_sla="before_forecast_and_replenishment_cutoff",
        freshness_field="valid_from",
        idempotency_fields=("source_system", "contract_name", "contract_version", "business_date", "checksum"),
        reconciliation_keys=("sku_id", "location_scope", "valid_from"),
        required_for=("regular_forecast", "promo_forecast", "procurement"),
        blocking_dq_checks=("schema", "row_count", "checksum", "duplicates", "referential_integrity", "price_validity"),
    ),
    SourceContractDefinition(
        source_system="ERP",
        contract_name="erp_order_export_status_line",
        model_name="ErpOrderExportStatusLine",
        primary_key=("export_id",),
        required_fields=("export_id", "proposal_id", "exported_at", "target_system", "status"),
        business_owner_role="Integration Owner",
        technical_owner_role="Integration Owner",
        source_sla="before_export_reconciliation_cutoff",
        freshness_field="exported_at",
        idempotency_fields=("source_system", "contract_name", "contract_version", "business_date", "checksum"),
        reconciliation_keys=("export_id", "proposal_id", "external_order_id"),
        required_for=("publication_reconciliation", "order_status_monitoring"),
        blocking_dq_checks=("schema", "row_count", "checksum", "duplicates", "status_validity", "export_reconciliation"),
    ),
    SourceContractDefinition(
        source_system="MDM",
        contract_name="mdm_product_line",
        model_name="MdmProductLine",
        primary_key=("sku_id",),
        required_fields=("sku_id", "product_name", "category_id", "category_path", "lifecycle_status", "is_active"),
        business_owner_role="MDM Data Owner",
        technical_owner_role="Data Engineering",
        source_sla="before_master_data_cutoff",
        freshness_field="source_system",
        idempotency_fields=("source_system", "contract_name", "contract_version", "business_date", "checksum"),
        reconciliation_keys=("sku_id", "category_id", "supplier_id"),
        required_for=("assortment", "fresh", "lifecycle", "hierarchy"),
        blocking_dq_checks=("schema", "row_count", "checksum", "duplicates", "hierarchy_integrity", "lifecycle_validity"),
    ),
    SourceContractDefinition(
        source_system="MDM",
        contract_name="mdm_store_line",
        model_name="MdmStoreLine",
        primary_key=("store_id",),
        required_fields=("store_id", "store_name", "region_id", "format_id", "timezone", "is_active"),
        business_owner_role="MDM Data Owner",
        technical_owner_role="Data Engineering",
        source_sla="before_master_data_cutoff",
        freshness_field="source_system",
        idempotency_fields=("source_system", "contract_name", "contract_version", "business_date", "checksum"),
        reconciliation_keys=("store_id", "region_id", "warehouse_id"),
        required_for=("store_scope", "replenishment_calendar", "routing"),
        blocking_dq_checks=("schema", "row_count", "checksum", "duplicates", "region_integrity", "calendar_integrity"),
    ),
    SourceContractDefinition(
        source_system="PROMO",
        contract_name="promo_plan_line",
        model_name="PromoPlanLine",
        primary_key=("promo_id", "sku_id", "store_scope_id"),
        required_fields=("promo_id", "promo_name", "sku_id", "store_scope_id", "date_from", "date_to", "regular_price", "promo_price", "discount_pct"),
        business_owner_role="Promo Planner",
        technical_owner_role="Data Engineering",
        source_sla="before_promo_forecast_cutoff",
        freshness_field="date_from",
        idempotency_fields=("source_system", "contract_name", "contract_version", "business_date", "checksum"),
        reconciliation_keys=("promo_id", "sku_id", "store_scope_id"),
        required_for=("promo_forecast", "shelf_space", "display_capacity"),
        blocking_dq_checks=("schema", "row_count", "checksum", "duplicates", "promo_overlap", "display_capacity"),
    ),
)


def contract_summaries() -> list[dict[str, Any]]:
    return [
        {
            "domain": domain.value,
            "model": model.__name__,
            "schema": model.model_json_schema(),
        }
        for domain, model in SCHEMA_REGISTRY.items()
    ]


def source_contract_summaries() -> list[dict[str, Any]]:
    return [
        {
            **definition.model_dump(mode="json"),
            "schema": SOURCE_CONTRACT_MODELS[definition.contract_name].model_json_schema(),
        }
        for definition in SOURCE_CONTRACT_REGISTRY
    ]
