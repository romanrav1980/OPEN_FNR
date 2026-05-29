from __future__ import annotations

from datetime import datetime
import os

try:
    from airflow.decorators import dag, task
except ModuleNotFoundError:
    dag = None
    task = None


def business_week_from_date(ds: str) -> str:
    parsed = datetime.fromisoformat(ds)
    year, week, _ = parsed.isocalendar()
    return f"{year}-W{week:02d}"


def build_process_health_digest_request(business_week: str, environment: str) -> dict[str, object]:
    return {
        "endpoint_path": "/process-navigator/reports/weekly",
        "query": {
            "business_week": business_week,
            "env": environment,
        },
        "service_host_env": "OPEN_FNR_SERVICE_HOST",
        "service_port_env": "OPEN_FNR_API_PORT",
        "notification_route": "process_health_digest",
        "superset_dataset_ref": "process_alert_history",
    }


def build_process_health_digest_message(report_payload: dict[str, object]) -> dict[str, object]:
    return {
        "route": "process_health_digest",
        "subject": f"OPEN FNR process health digest {report_payload['business_week']}",
        "business_week": report_payload["business_week"],
        "environment": report_payload["environment"],
        "root_causes": report_payload.get("root_causes", []),
        "sla_breaches": report_payload.get("sla_breaches", []),
        "superset_dataset_ref": report_payload.get("superset_dataset_ref", "process_alert_history"),
    }


if dag is not None and task is not None:

    @dag(
        dag_id="open_fnr_process_health_digest",
        start_date=datetime(2026, 5, 1),
        schedule="@weekly",
        catchup=False,
        tags=["open-fnr", "process-navigator", "digest"],
    )
    def process_health_digest_dag():
        @task
        def build_request(ds: str) -> dict[str, object]:
            return build_process_health_digest_request(
                business_week_from_date(ds),
                os.environ.get("OPEN_FNR_RUNTIME_MODE", "dev"),
            )

        @task
        def fetch_weekly_report(request: dict[str, object]) -> dict[str, object]:
            query = request["query"]
            return {
                "business_week": query["business_week"],
                "environment": query["env"],
                "root_causes": [],
                "sla_breaches": [],
                "superset_dataset_ref": request["superset_dataset_ref"],
            }

        @task
        def route_digest(report_payload: dict[str, object]) -> dict[str, object]:
            return build_process_health_digest_message(report_payload)

        route_digest(fetch_weekly_report(build_request()))

    process_health_digest_dag()
