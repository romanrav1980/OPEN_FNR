from datetime import datetime, timezone
from enum import StrEnum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(prefix="/data-scale", tags=["production-data-scale"])


class PartitionStatus(StrEnum):
    LOADED = "loaded"
    VALIDATED = "validated"
    LATE = "late"
    FAILED = "failed"


class DqGateDecision(StrEnum):
    PASS = "pass"
    WARNING = "warning"
    BLOCK = "block"


class DataVolumeProfile(BaseModel):
    profile_id: str
    stores: int = Field(gt=0)
    skus: int = Field(gt=0)
    history_days: int = Field(gt=0)
    forecast_horizon_days: int = Field(gt=0)
    partitions_per_day: int = Field(gt=0)
    expected_fact_rows: int = Field(gt=0)


class PartitionHealth(BaseModel):
    partition_id: str
    domain: str
    business_date: str
    row_count: int = Field(ge=0)
    expected_min_rows: int = Field(ge=0)
    status: PartitionStatus
    freshness_minutes: int = Field(ge=0)
    lineage_source: str


class LineageEdge(BaseModel):
    source: str
    target: str
    rows: int = Field(ge=0)
    checksum: str


INDUSTRIAL_PROFILE = DataVolumeProfile(
    profile_id="industrial-data-profile-001",
    stores=30_000,
    skus=5_500,
    history_days=730,
    forecast_horizon_days=90,
    partitions_per_day=48,
    expected_fact_rows=120_450_000_000,
)

PARTITIONS: tuple[PartitionHealth, ...] = (
    PartitionHealth(
        partition_id="sales_2026_05_28_p001",
        domain="sales",
        business_date="2026-05-28",
        row_count=164_820_000,
        expected_min_rows=150_000_000,
        status=PartitionStatus.VALIDATED,
        freshness_minutes=38,
        lineage_source="POS",
    ),
    PartitionHealth(
        partition_id="stock_2026_05_28_p001",
        domain="stock",
        business_date="2026-05-28",
        row_count=166_100_000,
        expected_min_rows=150_000_000,
        status=PartitionStatus.VALIDATED,
        freshness_minutes=42,
        lineage_source="WMS",
    ),
)

LINEAGE: tuple[LineageEdge, ...] = (
    LineageEdge(source="POS.raw_sales", target="clean.sales_daily", rows=164_820_000, checksum="sha256:sales-p001"),
    LineageEdge(source="WMS.raw_stock", target="clean.stock_daily", rows=166_100_000, checksum="sha256:stock-p001"),
    LineageEdge(source="clean.sales_daily", target="mart.feature_store", rows=164_820_000, checksum="sha256:feature-sales"),
)


def evaluate_industrial_dq_gate(partitions: tuple[PartitionHealth, ...]) -> DqGateDecision:
    if any(partition.status == PartitionStatus.FAILED for partition in partitions):
        return DqGateDecision.BLOCK
    if any(partition.status == PartitionStatus.LATE or partition.row_count < partition.expected_min_rows for partition in partitions):
        return DqGateDecision.WARNING
    return DqGateDecision.PASS


def validate_lineage_completeness(lineage: tuple[LineageEdge, ...]) -> bool:
    required_sources = {"POS.raw_sales", "WMS.raw_stock", "clean.sales_daily"}
    return required_sources.issubset({edge.source for edge in lineage})


@router.get("/profile")
def get_data_volume_profile() -> dict[str, object]:
    return INDUSTRIAL_PROFILE.model_dump(mode="json")


@router.get("/partitions")
def list_partition_health(actor_role: str = "Data Platform Owner") -> dict[str, object]:
    if actor_role != "Data Platform Owner":
        raise HTTPException(status_code=403, detail="Data Platform Owner role required")
    return {"items": [item.model_dump(mode="json") for item in PARTITIONS], "total": len(PARTITIONS)}


@router.get("/lineage")
def list_lineage() -> dict[str, object]:
    return {
        "items": [item.model_dump(mode="json") for item in LINEAGE],
        "complete": validate_lineage_completeness(LINEAGE),
    }


@router.get("/dq-gate")
def get_dq_gate() -> dict[str, object]:
    return {
        "decision": evaluate_industrial_dq_gate(PARTITIONS),
        "evaluated_at": datetime(2026, 5, 28, 17, 0, tzinfo=timezone.utc).isoformat(),
    }
