from open_fnr_api.config import Settings


def test_settings_build_service_urls_from_central_host_and_ports() -> None:
    settings = Settings(
        service_host="10.0.0.10",
        clickhouse_http_port=8123,
        flowable_port=8080,
        airflow_port=8088,
        opensearch_port=9200,
        superset_port=8089,
    )

    assert settings.clickhouse_ping_url == "http://10.0.0.10:8123/ping"
    assert settings.flowable_engine_url == "http://10.0.0.10:8080/flowable-rest/service/management/engine"
    assert settings.airflow_health_url == "http://10.0.0.10:8088/health"
    assert settings.opensearch_url == "http://10.0.0.10:9200"
    assert settings.superset_health_url == "http://10.0.0.10:8089/health"


def test_settings_expose_runtime_mode_and_mock_mode() -> None:
    settings = Settings(runtime_mode="test", mock_mode=False)

    assert settings.runtime_mode == "test"
    assert settings.mock_mode is False
