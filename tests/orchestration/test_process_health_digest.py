from orchestration.airflow.dags.process_health_digest import (
    build_process_health_digest_message,
    build_process_health_digest_request,
    business_week_from_date,
)


def test_business_week_from_date_uses_iso_week() -> None:
    assert business_week_from_date("2026-05-29") == "2026-W22"


def test_process_health_digest_request_uses_configured_service_boundary() -> None:
    request = build_process_health_digest_request("2026-W22", "stage")

    assert request["endpoint_path"] == "/process-navigator/reports/weekly"
    assert request["query"] == {"business_week": "2026-W22", "env": "stage"}
    assert request["service_host_env"] == "OPEN_FNR_SERVICE_HOST"
    assert request["service_port_env"] == "OPEN_FNR_API_PORT"
    assert request["superset_dataset_ref"] == "process_alert_history"


def test_process_health_digest_message_keeps_stakeholder_payload() -> None:
    message = build_process_health_digest_message(
        {
            "business_week": "2026-W22",
            "environment": "prod",
            "root_causes": [{"alert_key": "pos_late"}],
            "sla_breaches": [{"process_key": "forecast_review_process"}],
            "superset_dataset_ref": "process_alert_history",
        }
    )

    assert message["route"] == "process_health_digest"
    assert message["business_week"] == "2026-W22"
    assert message["environment"] == "prod"
    assert message["root_causes"] == [{"alert_key": "pos_late"}]
    assert message["sla_breaches"] == [{"process_key": "forecast_review_process"}]
