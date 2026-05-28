from datetime import date

import pytest
from pydantic import ValidationError

from open_fnr_api.data_contracts import ErpPriceLine, PosSalesLine, PriceRecord, SalesRecord, WmsStockSnapshotLine


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
