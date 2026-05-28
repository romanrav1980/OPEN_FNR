from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel, Field

from .config import settings
from .data_contracts import SourceBatchManifest
from .ingestion import (
    ERP_ORDER_STATUS_MANIFEST,
    ERP_PRICES_MANIFEST,
    MDM_PRODUCTS_MANIFEST,
    MDM_STORES_MANIFEST,
    POS_SALES_MANIFEST,
    PROMO_PLAN_MANIFEST,
    WMS_IN_TRANSIT_MANIFEST,
    WMS_OPEN_ORDERS_MANIFEST,
    WMS_STOCK_MANIFEST,
)
from .source_adapters import LocalFileDropAdapter, SourceFile


SOURCE_MANIFESTS: tuple[SourceBatchManifest, ...] = (
    POS_SALES_MANIFEST,
    WMS_STOCK_MANIFEST,
    WMS_OPEN_ORDERS_MANIFEST,
    WMS_IN_TRANSIT_MANIFEST,
    ERP_PRICES_MANIFEST,
    ERP_ORDER_STATUS_MANIFEST,
    MDM_PRODUCTS_MANIFEST,
    MDM_STORES_MANIFEST,
    PROMO_PLAN_MANIFEST,
)


class ShadowLoadContractResult(BaseModel):
    source_system: str
    contract_name: str
    business_date: date
    status: str
    discovered_files: tuple[SourceFile, ...]
    discovered_file_count: int = Field(ge=0)
    discovered_size_bytes: int = Field(ge=0)
    expected_row_count: int = Field(ge=0)
    idempotency_key: str


class ShadowLoadReport(BaseModel):
    business_date: date
    landing_root_path: str
    status: str
    total_contracts: int = Field(ge=0)
    discovered_contracts: int = Field(ge=0)
    missing_contracts: int = Field(ge=0)
    results: tuple[ShadowLoadContractResult, ...]


def manifests_for_business_date(business_date: date) -> tuple[SourceBatchManifest, ...]:
    manifests: list[SourceBatchManifest] = []
    for manifest in SOURCE_MANIFESTS:
        manifests.append(
            manifest.model_copy(
                update={
                    "business_date": business_date,
                    "idempotency_key": (
                        f"{manifest.source_system}:{manifest.contract_name}:"
                        f"{manifest.contract_version}:{business_date.isoformat()}"
                    ),
                }
            )
        )
    return tuple(manifests)


def run_shadow_load_discovery(
    business_date: date,
    landing_root_path: str | Path | None = None,
    manifests: Iterable[SourceBatchManifest] | None = None,
) -> ShadowLoadReport:
    root_path = Path(landing_root_path or settings.landing_root_path)
    adapter = LocalFileDropAdapter(root_path)
    manifest_list = tuple(manifests or manifests_for_business_date(business_date))
    results: list[ShadowLoadContractResult] = []

    for manifest in manifest_list:
        files = adapter.discover(manifest.source_system, manifest.contract_name, business_date)
        file_size = sum(file.size_bytes for file in files)
        results.append(
            ShadowLoadContractResult(
                source_system=manifest.source_system,
                contract_name=manifest.contract_name,
                business_date=business_date,
                status="discovered" if files else "missing_files",
                discovered_files=files,
                discovered_file_count=len(files),
                discovered_size_bytes=file_size,
                expected_row_count=manifest.row_count,
                idempotency_key=manifest.idempotency_key,
            )
        )

    discovered_contracts = sum(1 for result in results if result.status == "discovered")
    missing_contracts = len(results) - discovered_contracts
    return ShadowLoadReport(
        business_date=business_date,
        landing_root_path=root_path.as_posix(),
        status="ready_for_validation" if missing_contracts == 0 else "incomplete",
        total_contracts=len(results),
        discovered_contracts=discovered_contracts,
        missing_contracts=missing_contracts,
        results=tuple(results),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run OPEN FNR pilot shadow-load source discovery.")
    parser.add_argument("--business-date", required=True, help="Business date in YYYY-MM-DD format.")
    parser.add_argument("--landing-root-path", default=None, help="Optional source landing root override.")
    args = parser.parse_args()

    report = run_shadow_load_discovery(
        business_date=date.fromisoformat(args.business_date),
        landing_root_path=args.landing_root_path,
    )
    print(json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
