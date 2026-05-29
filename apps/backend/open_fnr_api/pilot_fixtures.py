from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field

from .shadow_load import SOURCE_MANIFESTS


class PilotFixtureFile(BaseModel):
    source_system: str
    contract_name: str
    business_date: date
    file_path: str = Field(min_length=1)
    manifest_path: str = Field(min_length=1)


class PilotFixtureResult(BaseModel):
    landing_root_path: str
    business_date: date
    files: tuple[PilotFixtureFile, ...]


def sample_payload_for_contract(contract_name: str) -> dict[str, object]:
    samples: dict[str, dict[str, object]] = {
        "pos_sales_line": {"receipt_id": "R001", "line_id": "1", "store_id": "S001", "sku_id": "SKU001", "sales_qty": 1},
        "dwh_sales_history_line": {"history_id": "H001", "store_id": "S001", "sku_id": "SKU001", "sales_qty": 1},
        "wms_stock_snapshot_line": {"snapshot_id": "SNAP001", "location_id": "S001", "sku_id": "SKU001", "available_qty": 10},
        "wms_open_order_line": {"order_id": "ORD001", "line_id": "1", "target_location_id": "S001", "sku_id": "SKU001"},
        "wms_in_transit_line": {"shipment_id": "SHIP001", "line_id": "1", "target_location_id": "S001", "sku_id": "SKU001"},
        "erp_price_line": {"price_id": "PRICE001", "sku_id": "SKU001", "location_scope": "S001", "selling_price": 99.9},
        "erp_order_export_status_line": {"export_id": "EXP001", "proposal_id": "PROP001", "status": "accepted"},
        "erp_supplier_term_line": {"supplier_term_id": "TERM001", "supplier_id": "SUP001", "sku_id": "SKU001", "pack_size_qty": 6},
        "mdm_product_line": {"sku_id": "SKU001", "category_id": "fresh", "lifecycle_status": "active"},
        "mdm_store_line": {"store_id": "S001", "region_id": "77", "format_id": "supermarket"},
        "promo_plan_line": {"promo_id": "PROMO001", "sku_id": "SKU001", "store_scope_id": "S001", "discount_pct": 0.1},
    }
    return samples[contract_name]


def generate_pilot_landing_pack(landing_root_path: str | Path, business_date: date) -> PilotFixtureResult:
    root_path = Path(landing_root_path)
    files: list[PilotFixtureFile] = []
    for manifest in SOURCE_MANIFESTS:
        source_dir = (
            root_path
            / manifest.source_system.lower()
            / manifest.contract_name
            / f"business_date={business_date.isoformat()}"
        )
        source_dir.mkdir(parents=True, exist_ok=True)
        file_path = source_dir / f"{manifest.contract_name}.json"
        manifest_path = source_dir / "manifest.json"
        file_path.write_text(
            json.dumps(sample_payload_for_contract(manifest.contract_name), ensure_ascii=False),
            encoding="utf-8",
        )
        manifest_payload = {
            "source_system": manifest.source_system,
            "contract_name": manifest.contract_name,
            "business_date": business_date.isoformat(),
            "row_count": 1,
            "checksum": f"sha256:pilot-{manifest.contract_name}-{business_date.isoformat()}",
            "idempotency_key": (
                f"{manifest.source_system}:{manifest.contract_name}:"
                f"{manifest.contract_version}:{business_date.isoformat()}"
            ),
            "files": [file_path.name],
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        files.append(
            PilotFixtureFile(
                source_system=manifest.source_system,
                contract_name=manifest.contract_name,
                business_date=business_date,
                file_path=file_path.as_posix(),
                manifest_path=manifest_path.as_posix(),
            )
        )

    return PilotFixtureResult(
        landing_root_path=root_path.as_posix(),
        business_date=business_date,
        files=tuple(files),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate OPEN FNR pilot landing sample pack.")
    parser.add_argument("--business-date", required=True, help="Business date in YYYY-MM-DD format.")
    parser.add_argument("--landing-root-path", required=True, help="Target landing root path.")
    args = parser.parse_args()

    result = generate_pilot_landing_pack(
        landing_root_path=args.landing_root_path,
        business_date=date.fromisoformat(args.business_date),
    )
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
