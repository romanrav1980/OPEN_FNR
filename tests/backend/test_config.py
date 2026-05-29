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


def test_settings_allow_per_service_hosts_for_container_networks() -> None:
    settings = Settings(
        service_host="host-machine",
        postgres_host="postgres",
        clickhouse_host="clickhouse",
        flowable_host="flowable",
        airflow_host="airflow-webserver",
        opensearch_host="opensearch",
        superset_host="superset",
        postgres_port=5432,
        clickhouse_http_port=8123,
        flowable_port=8080,
        airflow_port=8080,
        opensearch_port=9200,
        superset_port=8088,
    )

    assert settings.postgres_dsn == "postgresql://open_fnr:open_fnr_dev@postgres:5432/open_fnr"
    assert settings.clickhouse_ping_url == "http://clickhouse:8123/ping"
    assert settings.flowable_engine_url == "http://flowable:8080/flowable-rest/service/management/engine"
    assert settings.airflow_health_url == "http://airflow-webserver:8080/health"
    assert settings.opensearch_url == "http://opensearch:9200"
    assert settings.superset_health_url == "http://superset:8088/health"


def test_settings_expose_runtime_mode_and_mock_mode() -> None:
    settings = Settings(
        runtime_mode="test",
        mock_mode=False,
        audit_enabled=True,
        auth_enabled=True,
        auth_dev_bypass_enabled=False,
        oidc_issuer="https://idp.example.org",
        oidc_audience="open-fnr-api",
        oidc_jwks_url="https://idp.example.org/.well-known/jwks.json",
    )

    assert settings.runtime_mode == "test"
    assert settings.mock_mode is False
    assert settings.audit_enabled is True
    assert settings.auth_enabled is True
    assert settings.auth_dev_bypass_enabled is False
    assert settings.oidc_issuer == "https://idp.example.org"
    assert settings.oidc_audience == "open-fnr-api"
    assert settings.oidc_jwks_url == "https://idp.example.org/.well-known/jwks.json"


def test_audit_is_enabled_by_default_and_can_be_disabled() -> None:
    assert Settings().audit_enabled is True
    assert Settings(audit_enabled=False).audit_enabled is False


def test_landing_root_path_is_configurable() -> None:
    settings = Settings(landing_root_path="custom/landing", process_artifacts_root_path="custom/processes")

    assert settings.landing_root_path == "custom/landing"
    assert settings.process_artifacts_root_path == "custom/processes"


def test_cors_origins_are_centralized_settings() -> None:
    settings = Settings(cors_allow_origins=("http://ui.local:13000",))

    assert settings.cors_allow_origins == ("http://ui.local:13000",)


def test_clickhouse_credentials_are_centralized_settings() -> None:
    settings = Settings(
        clickhouse_user="ch_user",
        clickhouse_password="ch_password",
        clickhouse_database="ch_database",
    )

    assert settings.clickhouse_user == "ch_user"
    assert settings.clickhouse_password == "ch_password"
    assert settings.clickhouse_database == "ch_database"


def test_publication_target_urls_are_centralized_settings() -> None:
    settings = Settings(
        erp_export_url="http://erp.local/orders",
        wms_export_url="http://wms.local/orders",
        dwh_export_url="http://dwh.local/forecast",
        supplier_forecast_share_url="http://supplier.local/share",
        tms_capacity_export_url="http://tms.local/capacity",
        store_app_task_export_url="http://store-app.local/tasks",
        planogram_export_url="http://planogram.local/decisions",
        idp_provisioning_url="http://idp.local/provision",
        publication_http_timeout_seconds=11,
    )

    assert settings.erp_export_url == "http://erp.local/orders"
    assert settings.wms_export_url == "http://wms.local/orders"
    assert settings.dwh_export_url == "http://dwh.local/forecast"
    assert settings.supplier_forecast_share_url == "http://supplier.local/share"
    assert settings.tms_capacity_export_url == "http://tms.local/capacity"
    assert settings.store_app_task_export_url == "http://store-app.local/tasks"
    assert settings.planogram_export_url == "http://planogram.local/decisions"
    assert settings.idp_provisioning_url == "http://idp.local/provision"
    assert settings.publication_http_timeout_seconds == 11
