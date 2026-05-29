from __future__ import annotations

from datetime import date, datetime, timezone

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Path

from .data_contracts import (
    BatchStatus,
    DataDomain,
    DqSeverity,
    IngestionBatch,
    SOURCE_CONTRACT_REGISTRY,
    SourceBatchManifest,
    contract_summaries,
    source_contract_summaries,
)
from .source_adapters import LocalFileDropAdapter


router = APIRouter(prefix="/data", tags=["data-ingestion"])


class PilotSourceContract(BaseModel):
    source_system: str
    contract_name: str
    owner_role: str
    required_for: tuple[str, ...]


class PilotSourceDiscovery(BaseModel):
    source_system: str
    contract_name: str
    business_date: date
    status: str
    files: int
    row_count: int | None
    checksum: str | None
    idempotency_key: str | None
    owner_role: str
    required_for: tuple[str, ...]
    issue: str | None = None


class PilotRecoveryTask(BaseModel):
    task_id: str
    source_system: str
    contract_name: str
    owner_role: str
    reason: str
    actions: tuple[str, ...]


class PilotShadowLoadPlan(BaseModel):
    business_date: date
    landing_root_path: str
    status: str
    discovered_count: int
    required_count: int
    sources: tuple[PilotSourceDiscovery, ...]
    recovery_tasks: tuple[PilotRecoveryTask, ...]
    next_gate: str


SAMPLE_BATCHES: tuple[IngestionBatch, ...] = (
    IngestionBatch(
        batch_id="sales-2026-05-28-pos",
        domain=DataDomain.SALES,
        business_date=date(2026, 5, 28),
        source_system="POS",
        status=BatchStatus.LOADED,
        row_count=1250000,
        checksum="sha256:sales-dev-20260528",
        severity=DqSeverity.INFO,
        message="Synthetic Sprint 1 status sample",
        loaded_at=datetime(2026, 5, 28, 4, 10, tzinfo=timezone.utc),
    ),
    IngestionBatch(
        batch_id="stock-2026-05-28-wms",
        domain=DataDomain.STOCK,
        business_date=date(2026, 5, 28),
        source_system="WMS",
        status=BatchStatus.PARTIAL,
        row_count=1195000,
        checksum="sha256:stock-dev-20260528",
        severity=DqSeverity.WARNING,
        message="One regional source delayed",
        loaded_at=datetime(2026, 5, 28, 4, 35, tzinfo=timezone.utc),
    ),
)

POS_SALES_MANIFEST = SourceBatchManifest(
    batch_id="pos-sales-2026-05-28-v1",
    source_system="POS",
    contract_name="pos_sales_line",
    contract_version="v1",
    business_date=date(2026, 5, 28),
    row_count=1_250_000,
    checksum="sha256:pos-sales-20260528-v1",
    idempotency_key="POS:pos_sales_line:v1:2026-05-28",
    landed_uri="s3-compatible://open-fnr-landing/pos/business_date=2026-05-28/pos-sales.parquet",
)

DWH_SALES_HISTORY_MANIFEST = SourceBatchManifest(
    batch_id="dwh-sales-history-2026-05-28-v1",
    source_system="DWH",
    contract_name="dwh_sales_history_line",
    contract_version="v1",
    business_date=date(2026, 5, 28),
    row_count=960_000_000,
    checksum="sha256:dwh-sales-history-20260528-v1",
    idempotency_key="DWH:dwh_sales_history_line:v1:2026-05-28",
    landed_uri="s3-compatible://open-fnr-landing/dwh/sales_history/business_date=2026-05-28/dwh-sales-history.parquet",
)

WMS_STOCK_MANIFEST = SourceBatchManifest(
    batch_id="wms-stock-2026-05-28-v1",
    source_system="WMS",
    contract_name="wms_stock_snapshot_line",
    contract_version="v1",
    business_date=date(2026, 5, 28),
    row_count=1_195_000,
    checksum="sha256:wms-stock-20260528-v1",
    idempotency_key="WMS:wms_stock_snapshot_line:v1:2026-05-28",
    landed_uri="s3-compatible://open-fnr-landing/wms/stock/business_date=2026-05-28/wms-stock.parquet",
)

WMS_OPEN_ORDERS_MANIFEST = SourceBatchManifest(
    batch_id="wms-open-orders-2026-05-28-v1",
    source_system="WMS",
    contract_name="wms_open_order_line",
    contract_version="v1",
    business_date=date(2026, 5, 28),
    row_count=185_000,
    checksum="sha256:wms-open-orders-20260528-v1",
    idempotency_key="WMS:wms_open_order_line:v1:2026-05-28",
    landed_uri="s3-compatible://open-fnr-landing/wms/open_orders/business_date=2026-05-28/wms-open-orders.parquet",
)

WMS_IN_TRANSIT_MANIFEST = SourceBatchManifest(
    batch_id="wms-in-transit-2026-05-28-v1",
    source_system="WMS",
    contract_name="wms_in_transit_line",
    contract_version="v1",
    business_date=date(2026, 5, 28),
    row_count=92_000,
    checksum="sha256:wms-in-transit-20260528-v1",
    idempotency_key="WMS:wms_in_transit_line:v1:2026-05-28",
    landed_uri="s3-compatible://open-fnr-landing/wms/in_transit/business_date=2026-05-28/wms-in-transit.parquet",
)

ERP_PRICES_MANIFEST = SourceBatchManifest(
    batch_id="erp-prices-2026-05-28-v1",
    source_system="ERP",
    contract_name="erp_price_line",
    contract_version="v1",
    business_date=date(2026, 5, 28),
    row_count=640_000,
    checksum="sha256:erp-prices-20260528-v1",
    idempotency_key="ERP:erp_price_line:v1:2026-05-28",
    landed_uri="s3-compatible://open-fnr-landing/erp/prices/business_date=2026-05-28/erp-prices.parquet",
)

ERP_ORDER_STATUS_MANIFEST = SourceBatchManifest(
    batch_id="erp-order-statuses-2026-05-28-v1",
    source_system="ERP",
    contract_name="erp_order_export_status_line",
    contract_version="v1",
    business_date=date(2026, 5, 28),
    row_count=44_000,
    checksum="sha256:erp-order-statuses-20260528-v1",
    idempotency_key="ERP:erp_order_export_status_line:v1:2026-05-28",
    landed_uri="s3-compatible://open-fnr-landing/erp/order_statuses/business_date=2026-05-28/erp-order-statuses.parquet",
)

ERP_SUPPLIER_TERMS_MANIFEST = SourceBatchManifest(
    batch_id="erp-supplier-terms-2026-05-28-v1",
    source_system="ERP",
    contract_name="erp_supplier_term_line",
    contract_version="v1",
    business_date=date(2026, 5, 28),
    row_count=320_000,
    checksum="sha256:erp-supplier-terms-20260528-v1",
    idempotency_key="ERP:erp_supplier_term_line:v1:2026-05-28",
    landed_uri="s3-compatible://open-fnr-landing/erp/supplier_terms/business_date=2026-05-28/erp-supplier-terms.parquet",
)

MDM_PRODUCTS_MANIFEST = SourceBatchManifest(
    batch_id="mdm-products-2026-05-28-v1",
    source_system="MDM",
    contract_name="mdm_product_line",
    contract_version="v1",
    business_date=date(2026, 5, 28),
    row_count=1_150_000,
    checksum="sha256:mdm-products-20260528-v1",
    idempotency_key="MDM:mdm_product_line:v1:2026-05-28",
    landed_uri="s3-compatible://open-fnr-landing/mdm/products/business_date=2026-05-28/mdm-products.parquet",
)

MDM_STORES_MANIFEST = SourceBatchManifest(
    batch_id="mdm-stores-2026-05-28-v1",
    source_system="MDM",
    contract_name="mdm_store_line",
    contract_version="v1",
    business_date=date(2026, 5, 28),
    row_count=30_000,
    checksum="sha256:mdm-stores-20260528-v1",
    idempotency_key="MDM:mdm_store_line:v1:2026-05-28",
    landed_uri="s3-compatible://open-fnr-landing/mdm/stores/business_date=2026-05-28/mdm-stores.parquet",
)

PROMO_PLAN_MANIFEST = SourceBatchManifest(
    batch_id="promo-plan-2026-05-28-v1",
    source_system="PROMO",
    contract_name="promo_plan_line",
    contract_version="v1",
    business_date=date(2026, 5, 28),
    row_count=84_000,
    checksum="sha256:promo-plan-20260528-v1",
    idempotency_key="PROMO:promo_plan_line:v1:2026-05-28",
    landed_uri="s3-compatible://open-fnr-landing/promo/plans/business_date=2026-05-28/promo-plan.parquet",
)

SOURCE_PIPELINE_READINESS: tuple[dict[str, object], ...] = (
    {
        "source_system": "POS",
        "pipeline": "pos_sales",
        "contracts": ["pos_sales_line"],
        "status": "ready_for_shadow_load",
        "supports_projected_stock": False,
        "supports_forecast": True,
        "blocking_gates": ["schema", "row_count", "checksum", "dq"],
    },
    {
        "source_system": "DWH",
        "pipeline": "dwh_sales_history",
        "contracts": ["dwh_sales_history_line"],
        "status": "ready_for_shadow_load",
        "supports_projected_stock": False,
        "supports_forecast": True,
        "blocking_gates": ["schema", "row_count", "checksum", "date_range", "dq"],
    },
    {
        "source_system": "WMS",
        "pipeline": "wms_inventory",
        "contracts": ["wms_stock_snapshot_line", "wms_open_order_line", "wms_in_transit_line"],
        "status": "ready_for_shadow_load",
        "supports_projected_stock": True,
        "supports_forecast": False,
        "blocking_gates": ["schema", "row_count", "checksum", "dq"],
    },
    {
        "source_system": "ERP",
        "pipeline": "erp_commercial",
        "contracts": ["erp_price_line", "erp_order_export_status_line", "erp_supplier_term_line"],
        "status": "ready_for_shadow_load",
        "supports_projected_stock": False,
        "supports_forecast": True,
        "blocking_gates": ["schema", "row_count", "checksum", "dq", "export_reconciliation"],
    },
    {
        "source_system": "MDM",
        "pipeline": "mdm_reference",
        "contracts": ["mdm_product_line", "mdm_store_line"],
        "status": "ready_for_shadow_load",
        "supports_projected_stock": True,
        "supports_forecast": True,
        "blocking_gates": ["schema", "row_count", "checksum", "referential_integrity"],
    },
    {
        "source_system": "PROMO",
        "pipeline": "promo_plan",
        "contracts": ["promo_plan_line"],
        "status": "ready_for_shadow_load",
        "supports_projected_stock": True,
        "supports_forecast": True,
        "blocking_gates": ["schema", "row_count", "checksum", "overlap_dq", "display_capacity_dq"],
    },
)

PILOT_REQUIRED_SOURCE_CONTRACTS: tuple[PilotSourceContract, ...] = (
    PilotSourceContract(
        source_system="POS",
        contract_name="pos_sales_line",
        owner_role="Data Engineer",
        required_for=("regular_forecast", "promo_forecast", "demand_projection"),
    ),
    PilotSourceContract(
        source_system="DWH",
        contract_name="dwh_sales_history_line",
        owner_role="Sales Data Owner",
        required_for=("training_history", "backtesting", "regular_forecast", "promo_forecast"),
    ),
    PilotSourceContract(
        source_system="WMS",
        contract_name="wms_stock_snapshot_line",
        owner_role="Supply Chain Data Owner",
        required_for=("projected_stock", "replenishment", "true_inventory"),
    ),
    PilotSourceContract(
        source_system="WMS",
        contract_name="wms_open_order_line",
        owner_role="Supply Chain Data Owner",
        required_for=("projected_stock", "replenishment", "multi_echelon"),
    ),
    PilotSourceContract(
        source_system="WMS",
        contract_name="wms_in_transit_line",
        owner_role="Supply Chain Data Owner",
        required_for=("projected_stock", "replenishment", "capacity"),
    ),
    PilotSourceContract(
        source_system="ERP",
        contract_name="erp_price_line",
        owner_role="Commercial Data Owner",
        required_for=("regular_forecast", "promo_forecast", "procurement"),
    ),
    PilotSourceContract(
        source_system="ERP",
        contract_name="erp_order_export_status_line",
        owner_role="Integration Owner",
        required_for=("publication_reconciliation", "order_status_monitoring"),
    ),
    PilotSourceContract(
        source_system="ERP",
        contract_name="erp_supplier_term_line",
        owner_role="Commercial Data Owner",
        required_for=("replenishment", "procurement", "supplier_collaboration"),
    ),
    PilotSourceContract(
        source_system="MDM",
        contract_name="mdm_product_line",
        owner_role="MDM Data Owner",
        required_for=("assortment", "fresh", "lifecycle", "hierarchy"),
    ),
    PilotSourceContract(
        source_system="MDM",
        contract_name="mdm_store_line",
        owner_role="MDM Data Owner",
        required_for=("store_scope", "replenishment_calendar", "routing"),
    ),
    PilotSourceContract(
        source_system="PROMO",
        contract_name="promo_plan_line",
        owner_role="Promo Planner",
        required_for=("promo_forecast", "shelf_space", "display_capacity"),
    ),
)


def build_pilot_shadow_load_plan(business_date: date, adapter: LocalFileDropAdapter | None = None) -> PilotShadowLoadPlan:
    source_adapter = adapter or LocalFileDropAdapter()
    sources: list[PilotSourceDiscovery] = []
    recovery_tasks: list[PilotRecoveryTask] = []
    for contract in PILOT_REQUIRED_SOURCE_CONTRACTS:
        files = source_adapter.discover(contract.source_system, contract.contract_name, business_date)
        manifest = source_adapter.load_manifest_sidecar(contract.source_system, contract.contract_name, business_date)
        discovered_file_names = {file.file_name for file in files}
        status = "discovered"
        issue = None
        if not files:
            status = "missing_files"
            issue = "no supported source files found"
        elif manifest is None:
            status = "manifest_missing"
            issue = "manifest.json sidecar is missing"
        elif set(manifest.files) - discovered_file_names:
            status = "manifest_mismatch"
            issue = "manifest references files that were not discovered"

        source = PilotSourceDiscovery(
            source_system=contract.source_system,
            contract_name=contract.contract_name,
            business_date=business_date,
            status=status,
            files=len(files),
            row_count=manifest.row_count if manifest is not None else None,
            checksum=manifest.checksum if manifest is not None else None,
            idempotency_key=manifest.idempotency_key if manifest is not None else None,
            owner_role=contract.owner_role,
            required_for=contract.required_for,
            issue=issue,
        )
        sources.append(source)
        if issue is not None:
            recovery_tasks.append(
                PilotRecoveryTask(
                    task_id=f"recover-{contract.source_system.lower()}-{contract.contract_name}-{business_date.isoformat()}",
                    source_system=contract.source_system,
                    contract_name=contract.contract_name,
                    owner_role=contract.owner_role,
                    reason=issue,
                    actions=("request_resend", "reload_landing", "rerun_shadow_load"),
                )
            )

    discovered_count = sum(1 for source in sources if source.status == "discovered")
    return PilotShadowLoadPlan(
        business_date=business_date,
        landing_root_path=str(source_adapter.landing_root_path),
        status="ready_for_clean_publication" if discovered_count == len(sources) else "recovery_required",
        discovered_count=discovered_count,
        required_count=len(sources),
        sources=tuple(sources),
        recovery_tasks=tuple(recovery_tasks),
        next_gate="clean_publication" if discovered_count == len(sources) else "source_recovery",
    )


@router.get("/contracts")
def list_contracts() -> dict[str, object]:
    return {
        "freeze_status": "ri_1_frozen",
        "contracts": contract_summaries(),
        "source_contracts": source_contract_summaries(),
        "source_contract_count": len(SOURCE_CONTRACT_REGISTRY),
    }


@router.get("/ingestion/manifests/pos-sales")
def get_pos_sales_manifest() -> dict[str, object]:
    return POS_SALES_MANIFEST.model_dump(mode="json")


@router.get("/ingestion/manifests/dwh-sales-history")
def get_dwh_sales_history_manifest() -> dict[str, object]:
    return DWH_SALES_HISTORY_MANIFEST.model_dump(mode="json")


@router.get("/ingestion/manifests/wms-stock")
def get_wms_stock_manifest() -> dict[str, object]:
    return WMS_STOCK_MANIFEST.model_dump(mode="json")


@router.get("/ingestion/manifests/wms-open-orders")
def get_wms_open_orders_manifest() -> dict[str, object]:
    return WMS_OPEN_ORDERS_MANIFEST.model_dump(mode="json")


@router.get("/ingestion/manifests/wms-in-transit")
def get_wms_in_transit_manifest() -> dict[str, object]:
    return WMS_IN_TRANSIT_MANIFEST.model_dump(mode="json")


@router.get("/ingestion/manifests/erp-prices")
def get_erp_prices_manifest() -> dict[str, object]:
    return ERP_PRICES_MANIFEST.model_dump(mode="json")


@router.get("/ingestion/manifests/erp-order-statuses")
def get_erp_order_status_manifest() -> dict[str, object]:
    return ERP_ORDER_STATUS_MANIFEST.model_dump(mode="json")


@router.get("/ingestion/manifests/erp-supplier-terms")
def get_erp_supplier_terms_manifest() -> dict[str, object]:
    return ERP_SUPPLIER_TERMS_MANIFEST.model_dump(mode="json")


@router.get("/ingestion/manifests/mdm-products")
def get_mdm_products_manifest() -> dict[str, object]:
    return MDM_PRODUCTS_MANIFEST.model_dump(mode="json")


@router.get("/ingestion/manifests/mdm-stores")
def get_mdm_stores_manifest() -> dict[str, object]:
    return MDM_STORES_MANIFEST.model_dump(mode="json")


@router.get("/ingestion/manifests/promo-plan")
def get_promo_plan_manifest() -> dict[str, object]:
    return PROMO_PLAN_MANIFEST.model_dump(mode="json")


@router.get("/ingestion/readiness")
def get_ingestion_readiness() -> dict[str, object]:
    pipelines = list(SOURCE_PIPELINE_READINESS)
    ready_count = sum(1 for pipeline in pipelines if pipeline["status"] == "ready_for_shadow_load")
    return {
        "status": "ready_for_shadow_load" if ready_count == len(pipelines) else "incomplete",
        "ready_count": ready_count,
        "total": len(pipelines),
        "pipelines": pipelines,
        "next_gate": "pilot_shadow_load",
    }


@router.get("/source-adapters/local-files/discover")
def discover_local_source_files(source_system: str, contract_name: str, business_date: date) -> dict[str, object]:
    adapter = LocalFileDropAdapter()
    files = adapter.discover(source_system, contract_name, business_date)
    manifest = adapter.load_manifest_sidecar(source_system, contract_name, business_date)
    return {
        "source_system": source_system.upper(),
        "contract_name": contract_name,
        "business_date": business_date.isoformat(),
        "total": len(files),
        "items": [file.model_dump(mode="json") for file in files],
        "manifest": manifest.model_dump(mode="json") if manifest is not None else None,
    }


@router.get("/ingestion/pilot-shadow-load/plan")
def get_pilot_shadow_load_plan(business_date: date) -> dict[str, object]:
    return build_pilot_shadow_load_plan(business_date).model_dump(mode="json")


@router.get("/ingestion/status")
def list_ingestion_status(
    business_date: date | None = None,
    domain: DataDomain | None = None,
    status: BatchStatus | None = None,
) -> dict[str, object]:
    batches = list(SAMPLE_BATCHES)
    if business_date is not None:
        batches = [batch for batch in batches if batch.business_date == business_date]
    if domain is not None:
        batches = [batch for batch in batches if batch.domain == domain]
    if status is not None:
        batches = [batch for batch in batches if batch.status == status]

    return {
        "items": [batch.model_dump(mode="json") for batch in batches],
        "total": len(batches),
    }


@router.get("/ingestion/status/{batch_id}")
def get_ingestion_batch(batch_id: str = Path(min_length=1)) -> dict[str, object]:
    for batch in SAMPLE_BATCHES:
        if batch.batch_id == batch_id:
            return batch.model_dump(mode="json")
    raise HTTPException(status_code=404, detail="batch not found")
