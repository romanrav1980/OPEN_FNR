from __future__ import annotations

from datetime import date
from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .audit import AuditEventCreate, record_audit_event_if_enabled


router = APIRouter(prefix="/data/clean-publication", tags=["data-ingestion"])


class CleanPublicationRunMode(StrEnum):
    DRY_RUN = "dry_run"
    MOCK_RUN = "mock_run"
    CLICKHOUSE = "clickhouse"


class CleanPublicationPlan(BaseModel):
    plan_id: str = Field(min_length=1, max_length=128)
    source_system: str = Field(min_length=1, max_length=64)
    contract_name: str = Field(min_length=1, max_length=128)
    raw_table: str = Field(min_length=1, max_length=128)
    clean_table: str = Field(min_length=1, max_length=128)
    source_batch_id: str = Field(min_length=1, max_length=128)
    business_date: date
    idempotency_strategy: str
    delete_sql: str
    insert_sql: str
    quality_status: str = "accepted"


class CleanPublicationRunRequest(BaseModel):
    business_date: date
    actor: str = Field(min_length=1, max_length=128)
    actor_role: str = Field(default="Data Platform Owner", min_length=1, max_length=64)
    mode: CleanPublicationRunMode = CleanPublicationRunMode.DRY_RUN


class CleanPublicationPlanRunResult(BaseModel):
    plan_id: str
    source_batch_id: str
    clean_table: str
    status: str
    executed_statements: tuple[str, ...]
    affected_rows: int = Field(ge=0)


class CleanPublicationRunResponse(BaseModel):
    run_id: str
    business_date: date
    mode: CleanPublicationRunMode
    status: str
    plan_count: int = Field(ge=0)
    results: tuple[CleanPublicationPlanRunResult, ...]
    audit_recorded: bool


def clean_publication_plans_for_date(business_date: date) -> tuple[CleanPublicationPlan, ...]:
    date_sql = business_date.isoformat()
    return (
        CleanPublicationPlan(
            plan_id=f"clean-sales-{date_sql}",
            source_system="POS",
            contract_name="pos_sales_line",
            raw_table="open_fnr.raw_pos_sales_lines",
            clean_table="open_fnr.clean_sales_daily",
            source_batch_id=f"pos-sales-{date_sql}-v1",
            business_date=business_date,
            idempotency_strategy="delete_by_source_batch_then_insert",
            delete_sql=f"ALTER TABLE open_fnr.clean_sales_daily DELETE WHERE source_batch_id = 'pos-sales-{date_sql}-v1'",
            insert_sql=(
                "INSERT INTO open_fnr.clean_sales_daily "
                "SELECT business_date, store_id, sku_id, sum(sales_qty), sum(gross_amount), "
                "sum(net_amount), sum(discount_amount), uniqExact(receipt_id), "
                "abs(sumIf(sales_qty, sales_qty < 0)), batch_id, 'accepted', now() "
                "FROM open_fnr.raw_pos_sales_lines "
                f"WHERE batch_id = 'pos-sales-{date_sql}-v1' "
                "GROUP BY business_date, store_id, sku_id, batch_id"
            ),
        ),
        CleanPublicationPlan(
            plan_id=f"clean-stock-{date_sql}",
            source_system="WMS",
            contract_name="wms_stock_snapshot_line",
            raw_table="open_fnr.raw_wms_stock_snapshots",
            clean_table="open_fnr.clean_stock_snapshot_daily",
            source_batch_id=f"wms-stock-{date_sql}-v1",
            business_date=business_date,
            idempotency_strategy="delete_by_source_batch_then_insert",
            delete_sql=f"ALTER TABLE open_fnr.clean_stock_snapshot_daily DELETE WHERE source_batch_id = 'wms-stock-{date_sql}-v1'",
            insert_sql=(
                "INSERT INTO open_fnr.clean_stock_snapshot_daily "
                "SELECT business_date, location_id, location_type, sku_id, on_hand_qty, reserved_qty, "
                "available_qty, damaged_qty, batch_id, 'accepted', now() "
                "FROM open_fnr.raw_wms_stock_snapshots "
                f"WHERE batch_id = 'wms-stock-{date_sql}-v1'"
            ),
        ),
        CleanPublicationPlan(
            plan_id=f"clean-open-orders-{date_sql}",
            source_system="WMS",
            contract_name="wms_open_order_line",
            raw_table="open_fnr.raw_wms_open_orders",
            clean_table="open_fnr.clean_open_orders",
            source_batch_id=f"wms-open-orders-{date_sql}-v1",
            business_date=business_date,
            idempotency_strategy="delete_by_source_batch_then_insert",
            delete_sql=f"ALTER TABLE open_fnr.clean_open_orders DELETE WHERE source_batch_id = 'wms-open-orders-{date_sql}-v1'",
            insert_sql=(
                "INSERT INTO open_fnr.clean_open_orders "
                "SELECT order_id, line_id, order_date, expected_delivery_date, source_location_id, "
                "target_location_id, sku_id, ordered_qty, confirmed_qty, status, batch_id, 'accepted', now() "
                "FROM open_fnr.raw_wms_open_orders "
                f"WHERE batch_id = 'wms-open-orders-{date_sql}-v1'"
            ),
        ),
        CleanPublicationPlan(
            plan_id=f"clean-in-transit-{date_sql}",
            source_system="WMS",
            contract_name="wms_in_transit_line",
            raw_table="open_fnr.raw_wms_in_transit",
            clean_table="open_fnr.clean_in_transit",
            source_batch_id=f"wms-in-transit-{date_sql}-v1",
            business_date=business_date,
            idempotency_strategy="delete_by_source_batch_then_insert",
            delete_sql=f"ALTER TABLE open_fnr.clean_in_transit DELETE WHERE source_batch_id = 'wms-in-transit-{date_sql}-v1'",
            insert_sql=(
                "INSERT INTO open_fnr.clean_in_transit "
                "SELECT shipment_id, line_id, ship_date, eta_date, source_location_id, target_location_id, "
                "sku_id, shipped_qty, received_qty, status, batch_id, 'accepted', now() "
                "FROM open_fnr.raw_wms_in_transit "
                f"WHERE batch_id = 'wms-in-transit-{date_sql}-v1'"
            ),
        ),
        CleanPublicationPlan(
            plan_id=f"clean-prices-{date_sql}",
            source_system="ERP",
            contract_name="erp_price_line",
            raw_table="open_fnr.raw_erp_prices",
            clean_table="open_fnr.clean_prices",
            source_batch_id=f"erp-prices-{date_sql}-v1",
            business_date=business_date,
            idempotency_strategy="delete_by_source_batch_then_insert",
            delete_sql=f"ALTER TABLE open_fnr.clean_prices DELETE WHERE source_batch_id = 'erp-prices-{date_sql}-v1'",
            insert_sql=(
                "INSERT INTO open_fnr.clean_prices "
                "SELECT sku_id, location_scope, valid_from, valid_to, regular_price, selling_price, "
                "currency, vat_rate, batch_id, 'accepted', now() "
                "FROM open_fnr.raw_erp_prices "
                f"WHERE batch_id = 'erp-prices-{date_sql}-v1'"
            ),
        ),
        CleanPublicationPlan(
            plan_id=f"clean-promo-{date_sql}",
            source_system="PROMO",
            contract_name="promo_plan_line",
            raw_table="open_fnr.raw_promo_plans",
            clean_table="open_fnr.clean_promo_plans",
            source_batch_id=f"promo-plan-{date_sql}-v1",
            business_date=business_date,
            idempotency_strategy="delete_by_source_batch_then_insert",
            delete_sql=f"ALTER TABLE open_fnr.clean_promo_plans DELETE WHERE source_batch_id = 'promo-plan-{date_sql}-v1'",
            insert_sql=(
                "INSERT INTO open_fnr.clean_promo_plans "
                "SELECT promo_id, sku_id, store_scope_id, date_from, date_to, regular_price, promo_price, "
                "discount_pct, display_type, display_location, display_capacity_units, mechanics, "
                "forecast_lock, batch_id, 'accepted', now() "
                "FROM open_fnr.raw_promo_plans "
                f"WHERE batch_id = 'promo-plan-{date_sql}-v1'"
            ),
        ),
    )


def execute_clean_publication_plan(
    plan: CleanPublicationPlan,
    mode: CleanPublicationRunMode,
) -> CleanPublicationPlanRunResult:
    if mode == CleanPublicationRunMode.DRY_RUN:
        return CleanPublicationPlanRunResult(
            plan_id=plan.plan_id,
            source_batch_id=plan.source_batch_id,
            clean_table=plan.clean_table,
            status="validated",
            executed_statements=(),
            affected_rows=0,
        )
    if mode == CleanPublicationRunMode.MOCK_RUN:
        return CleanPublicationPlanRunResult(
            plan_id=plan.plan_id,
            source_batch_id=plan.source_batch_id,
            clean_table=plan.clean_table,
            status="mock_executed",
            executed_statements=(plan.delete_sql, plan.insert_sql),
            affected_rows=0,
        )
    raise HTTPException(status_code=501, detail="clickhouse execution is not implemented yet")


@router.get("/plans")
def list_clean_publication_plans(business_date: date) -> dict[str, object]:
    plans = clean_publication_plans_for_date(business_date)
    return {"items": [plan.model_dump(mode="json") for plan in plans], "total": len(plans)}


@router.get("/plans/{plan_id}")
def get_clean_publication_plan(plan_id: str, business_date: date) -> dict[str, object]:
    for plan in clean_publication_plans_for_date(business_date):
        if plan.plan_id == plan_id:
            return plan.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="clean publication plan not found")


@router.post("/runs")
def run_clean_publication(request: CleanPublicationRunRequest) -> dict[str, object]:
    plans = clean_publication_plans_for_date(request.business_date)
    results = tuple(execute_clean_publication_plan(plan, request.mode) for plan in plans)
    status = "ready" if request.mode == CleanPublicationRunMode.DRY_RUN else "completed"
    run_id = f"clean-publication-{request.business_date.isoformat()}-{request.mode.value}"
    event = record_audit_event_if_enabled(
        AuditEventCreate(
            event_type="clean_publication_run",
            actor=request.actor,
            actor_role=request.actor_role,
            object_type="clean_publication",
            object_id=run_id,
            action=f"run_{request.mode.value}",
            reason=f"status={status}; plan_count={len(plans)}",
            correlation_id=run_id,
            payload={
                "business_date": request.business_date.isoformat(),
                "mode": request.mode.value,
                "plan_count": len(plans),
                "status": status,
            },
        )
    )
    response = CleanPublicationRunResponse(
        run_id=run_id,
        business_date=request.business_date,
        mode=request.mode,
        status=status,
        plan_count=len(plans),
        results=results,
        audit_recorded=event is not None,
    )
    return response.model_dump(mode="json")
