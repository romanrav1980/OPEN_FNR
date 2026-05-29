from __future__ import annotations

from datetime import datetime

try:
    from airflow.decorators import dag, task
except ModuleNotFoundError:
    dag = None
    task = None


def build_erp_manifest(contract_name: str, business_date: str) -> dict[str, object]:
    return {
        "batch_id": f"{contract_name.replace('_', '-')}-{business_date}-v1",
        "source_system": "ERP",
        "contract_name": contract_name,
        "contract_version": "v1",
        "business_date": business_date,
        "idempotency_key": f"ERP:{contract_name}:v1:{business_date}",
    }


def build_erp_reconciliation_plan(business_date: str) -> dict[str, object]:
    contracts = (
        {
            "contract_name": "erp_price_line",
            "reconciliation_keys": ("sku_id", "location_scope", "valid_from"),
            "blocks": ("regular_forecast", "promo_forecast", "replenishment"),
            "sla": "before_forecast_and_replenishment_cutoff",
        },
        {
            "contract_name": "erp_supplier_term_line",
            "reconciliation_keys": ("supplier_id", "sku_id", "location_scope", "valid_from"),
            "blocks": ("replenishment", "procurement", "supplier_collaboration"),
            "sla": "before_replenishment_cutoff",
        },
        {
            "contract_name": "erp_order_export_status_line",
            "reconciliation_keys": ("export_id", "proposal_id", "external_order_id"),
            "blocks": ("publication_reconciliation", "order_status_monitoring"),
            "sla": "before_export_reconciliation_cutoff",
        },
    )
    return {
        "business_date": business_date,
        "source_system": "ERP",
        "contracts": contracts,
        "required_count": len(contracts),
        "failure_action": "create_integration_owner_recovery_task",
    }


if dag is not None and task is not None:

    @dag(
        dag_id="open_fnr_erp_commercial_ingestion",
        start_date=datetime(2026, 5, 1),
        schedule="@daily",
        catchup=False,
        tags=["open-fnr", "erp", "commercial"],
    )
    def erp_commercial_ingestion_dag():
        @task
        def create_manifests(ds: str) -> list[dict[str, object]]:
            return [
                build_erp_manifest("erp_price_line", ds),
                build_erp_manifest("erp_order_export_status_line", ds),
                build_erp_manifest("erp_supplier_term_line", ds),
            ]

        @task
        def validate_schema(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            return [{**manifest, "schema_status": "validated"} for manifest in manifests]

        @task
        def run_dq(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            return [{**manifest, "dq_status": "accepted"} for manifest in manifests]

        @task
        def reconcile_commercial_inputs(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            plan = build_erp_reconciliation_plan(str(manifests[0]["business_date"]))
            return [{**manifest, "reconciliation_status": "accepted", "reconciliation_plan": plan} for manifest in manifests]

        @task
        def publish_commercial_data(manifests: list[dict[str, object]]) -> list[dict[str, object]]:
            return [{**manifest, "publish_status": "published"} for manifest in manifests]

        publish_commercial_data(reconcile_commercial_inputs(run_dq(validate_schema(create_manifests()))))

    erp_commercial_ingestion_dag()
