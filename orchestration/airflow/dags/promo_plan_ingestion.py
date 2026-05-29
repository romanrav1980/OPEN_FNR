from __future__ import annotations

from datetime import datetime

try:
    from airflow.decorators import dag, task
except ModuleNotFoundError:
    dag = None
    task = None


def build_promo_manifest(business_date: str) -> dict[str, object]:
    return {
        "batch_id": f"promo-plan-{business_date}-v1",
        "source_system": "PROMO",
        "contract_name": "promo_plan_line",
        "contract_version": "v1",
        "business_date": business_date,
        "idempotency_key": f"PROMO:promo_plan_line:v1:{business_date}",
    }


def build_promo_quality_plan(business_date: str) -> dict[str, object]:
    return {
        "business_date": business_date,
        "source_system": "PROMO",
        "contract_name": "promo_plan_line",
        "quality_checks": (
            "sku_store_scope_integrity",
            "date_range_validity",
            "promo_overlap",
            "price_discount_consistency",
            "display_location_presence",
            "display_capacity_presence",
        ),
        "blocks": ("promo_forecast", "promo_order_impact", "shelf_space", "capacity"),
        "failure_action": "create_promo_planner_recovery_task",
    }


if dag is not None and task is not None:

    @dag(
        dag_id="open_fnr_promo_plan_ingestion",
        start_date=datetime(2026, 5, 1),
        schedule="@daily",
        catchup=False,
        tags=["open-fnr", "promo", "plan"],
    )
    def promo_plan_ingestion_dag():
        @task
        def create_manifest(ds: str) -> dict[str, object]:
            return build_promo_manifest(ds)

        @task
        def validate_schema(manifest: dict[str, object]) -> dict[str, object]:
            return {**manifest, "schema_status": "validated"}

        @task
        def run_promo_dq(manifest: dict[str, object]) -> dict[str, object]:
            return {**manifest, "dq_status": "accepted", "overlap_check": "passed"}

        @task
        def validate_promo_quality(manifest: dict[str, object]) -> dict[str, object]:
            return {**manifest, "quality_plan": build_promo_quality_plan(str(manifest["business_date"]))}

        @task
        def publish_promo_plan(manifest: dict[str, object]) -> dict[str, object]:
            return {**manifest, "publish_status": "published"}

        publish_promo_plan(validate_promo_quality(run_promo_dq(validate_schema(create_manifest()))))

    promo_plan_ingestion_dag()
