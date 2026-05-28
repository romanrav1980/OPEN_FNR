from datetime import date

import pytest
from pydantic import ValidationError

from open_fnr_api.data_contracts import PriceRecord, SalesRecord


def test_sales_contract_rejects_negative_quantity() -> None:
    with pytest.raises(ValidationError):
        SalesRecord(
            business_date=date(2026, 5, 28),
            store_id="S001",
            sku_id="SKU001",
            sales_qty=-1,
            sales_amount=100,
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
