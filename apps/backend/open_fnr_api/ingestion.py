from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException, Path

from .data_contracts import BatchStatus, DataDomain, DqSeverity, IngestionBatch, SourceBatchManifest, contract_summaries


router = APIRouter(prefix="/data", tags=["data-ingestion"])


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


@router.get("/contracts")
def list_contracts() -> dict[str, object]:
    return {"contracts": contract_summaries()}


@router.get("/ingestion/manifests/pos-sales")
def get_pos_sales_manifest() -> dict[str, object]:
    return POS_SALES_MANIFEST.model_dump(mode="json")


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
