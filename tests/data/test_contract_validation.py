from datetime import date

import pytest
from pydantic import ValidationError

from open_fnr_api.data_contracts import (
    ErpPriceLine,
    MdmProductLine,
    MdmStoreLine,
    PosSalesLine,
    PriceRecord,
    PromoPlanLine,
    SalesRecord,
    WmsStockSnapshotLine,
)


def test_sales_contract_rejects_negative_quantity() -> None:
    with pytest.raises(ValidationError):
        SalesRecord(
            business_date=date(2026, 5, 28),
            store_id="S001",
            sku_id="SKU001",
            sales_qty=-1,
            sales_amount=100,
        )


def test_pos_sales_line_accepts_returns_but_rejects_zero_quantity() -> None:
    PosSalesLine(
        receipt_id="R001",
        line_id="1",
        business_date=date(2026, 5, 28),
        store_id="S001",
        sku_id="SKU001",
        sales_qty=1,
        gross_amount=100,
        net_amount=90,
        discount_amount=10,
    )
    PosSalesLine(
        receipt_id="R002",
        line_id="1",
        business_date=date(2026, 5, 28),
        store_id="S001",
        sku_id="SKU001",
        sales_qty=-1,
        gross_amount=100,
        net_amount=100,
    )

    with pytest.raises(ValidationError):
        PosSalesLine(
            receipt_id="R003",
            line_id="1",
            business_date=date(2026, 5, 28),
            store_id="S001",
            sku_id="SKU001",
            sales_qty=0,
            gross_amount=100,
            net_amount=100,
        )


def test_price_contract_rejects_zero_price() -> None:
    with pytest.raises(ValidationError):
        PriceRecord(
            business_date=date(2026, 5, 28),
            store_id="S001",
            sku_id="SKU001",
            regular_price=0,
            selling_price=10,
        )


def test_wms_stock_snapshot_rejects_available_qty_above_on_hand() -> None:
    with pytest.raises(ValidationError):
        WmsStockSnapshotLine(
            snapshot_id="SNAP001",
            snapshot_at="2026-05-28T04:00:00Z",
            business_date=date(2026, 5, 28),
            location_id="STORE001",
            location_type="store",
            sku_id="SKU001",
            on_hand_qty=10,
            reserved_qty=0,
            available_qty=11,
        )


def test_erp_price_line_rejects_extreme_selling_price() -> None:
    with pytest.raises(ValidationError):
        ErpPriceLine(
            price_id="PRICE001",
            sku_id="SKU001",
            location_scope="STORE001",
            valid_from=date(2026, 5, 28),
            regular_price=100,
            selling_price=1001,
        )


def test_mdm_product_and_store_lines_capture_lifecycle_and_replenishment_keys() -> None:
    product = MdmProductLine(
        sku_id="SKU001",
        product_name="Milk",
        category_id="DAIRY",
        category_path="Food/Dairy/Milk",
        supplier_id="SUP001",
        shelf_life_days=7,
        lifecycle_status="active",
        is_fresh=True,
    )
    store = MdmStoreLine(
        store_id="STORE001",
        store_name="Central Store",
        region_id="REG001",
        format_id="SMALL",
        replenishment_calendar_id="CAL001",
        warehouse_id="DC001",
    )

    assert product.lifecycle_status == "active"
    assert product.is_fresh is True
    assert store.replenishment_calendar_id == "CAL001"
    assert store.warehouse_id == "DC001"


def test_promo_plan_line_rejects_price_above_regular_and_captures_display() -> None:
    promo = PromoPlanLine(
        promo_id="PROMO001",
        promo_name="Weekend milk discount",
        sku_id="SKU001",
        store_scope_id="REG001",
        date_from=date(2026, 6, 1),
        date_to=date(2026, 6, 7),
        regular_price=100,
        promo_price=90,
        discount_pct=0.1,
        display_type="endcap",
        display_location="entrance",
        display_capacity_units=120,
    )

    assert promo.display_type == "endcap"
    assert promo.display_capacity_units == 120

    with pytest.raises(ValidationError):
        PromoPlanLine(
            promo_id="PROMO002",
            promo_name="Invalid promo",
            sku_id="SKU001",
            store_scope_id="REG001",
            date_from=date(2026, 6, 1),
            date_to=date(2026, 6, 7),
            regular_price=100,
            promo_price=101,
            discount_pct=0,
        )
