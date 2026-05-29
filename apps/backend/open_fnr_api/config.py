import os

from pydantic import BaseModel, Field


class ServiceEndpoint(BaseModel):
    name: str
    url: str
    required_statuses: tuple[int, ...] = (200,)


def env_str(name: str, default: str) -> str:
    return os.getenv(f"OPEN_FNR_{name}", default)


def env_int(name: str, default: int) -> int:
    return int(os.getenv(f"OPEN_FNR_{name}", str(default)))


def env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(f"OPEN_FNR_{name}")
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_csv(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw = os.getenv(f"OPEN_FNR_{name}")
    if raw is None:
        return default
    return tuple(item.strip() for item in raw.split(",") if item.strip())


class Settings(BaseModel):
    app_name: str = env_str("APP_NAME", "OPEN FNR API")
    version: str = env_str("VERSION", "0.1.0")
    service_host: str = Field(default_factory=lambda: env_str("SERVICE_HOST", "127.0.0.1"))
    postgres_host: str = Field(default_factory=lambda: env_str("POSTGRES_HOST", ""))
    clickhouse_host: str = Field(default_factory=lambda: env_str("CLICKHOUSE_HOST", ""))
    flowable_host: str = Field(default_factory=lambda: env_str("FLOWABLE_HOST", ""))
    airflow_host: str = Field(default_factory=lambda: env_str("AIRFLOW_HOST", ""))
    opensearch_host: str = Field(default_factory=lambda: env_str("OPENSEARCH_HOST", ""))
    superset_host: str = Field(default_factory=lambda: env_str("SUPERSET_HOST", ""))
    api_port: int = Field(default_factory=lambda: env_int("API_PORT", 8000), ge=1, le=65535)
    frontend_port: int = Field(default_factory=lambda: env_int("FRONTEND_PORT", 13000), ge=1, le=65535)
    postgres_port: int = Field(default_factory=lambda: env_int("POSTGRES_PORT", 15432), ge=1, le=65535)
    clickhouse_http_port: int = Field(default_factory=lambda: env_int("CLICKHOUSE_HTTP_PORT", 18123), ge=1, le=65535)
    flowable_port: int = Field(default_factory=lambda: env_int("FLOWABLE_PORT", 18080), ge=1, le=65535)
    airflow_port: int = Field(default_factory=lambda: env_int("AIRFLOW_PORT", 18088), ge=1, le=65535)
    opensearch_port: int = Field(default_factory=lambda: env_int("OPENSEARCH_PORT", 19200), ge=1, le=65535)
    opensearch_dashboards_port: int = Field(default_factory=lambda: env_int("OPENSEARCH_DASHBOARDS_PORT", 15601), ge=1, le=65535)
    superset_port: int = Field(default_factory=lambda: env_int("SUPERSET_PORT", 18089), ge=1, le=65535)
    postgres_user: str = Field(default_factory=lambda: env_str("POSTGRES_USER", "open_fnr"))
    postgres_password: str = Field(default_factory=lambda: env_str("POSTGRES_PASSWORD", "open_fnr_dev"))
    postgres_database: str = Field(default_factory=lambda: env_str("POSTGRES_DATABASE", "open_fnr"))
    clickhouse_user: str = Field(default_factory=lambda: env_str("CLICKHOUSE_USER", "open_fnr"))
    clickhouse_password: str = Field(default_factory=lambda: env_str("CLICKHOUSE_PASSWORD", "open_fnr_dev"))
    clickhouse_database: str = Field(default_factory=lambda: env_str("CLICKHOUSE_DATABASE", "open_fnr"))
    erp_export_url: str = Field(default_factory=lambda: env_str("ERP_EXPORT_URL", ""))
    wms_export_url: str = Field(default_factory=lambda: env_str("WMS_EXPORT_URL", ""))
    dwh_export_url: str = Field(default_factory=lambda: env_str("DWH_EXPORT_URL", ""))
    bi_export_url: str = Field(default_factory=lambda: env_str("BI_EXPORT_URL", ""))
    auto_order_export_url: str = Field(default_factory=lambda: env_str("AUTO_ORDER_EXPORT_URL", ""))
    publication_http_timeout_seconds: int = Field(
        default_factory=lambda: env_int("PUBLICATION_HTTP_TIMEOUT_SECONDS", 30),
        ge=1,
        le=300,
    )
    landing_root_path: str = Field(default_factory=lambda: env_str("LANDING_ROOT_PATH", "data/landing"))
    runtime_mode: str = Field(default_factory=lambda: env_str("RUNTIME_MODE", "dev"))
    mock_mode: bool = Field(default_factory=lambda: env_bool("MOCK_MODE", True))
    audit_enabled: bool = Field(default_factory=lambda: env_bool("AUDIT_ENABLED", True))
    cors_allow_origins: tuple[str, ...] = Field(
        default_factory=lambda: env_csv("CORS_ALLOW_ORIGINS", ("http://127.0.0.1:13000", "http://localhost:13000"))
    )

    def http_url(self, host: str, port: int, path: str = "") -> str:
        normalized_path = path if path.startswith("/") or path == "" else f"/{path}"
        resolved_host = host or self.service_host
        return f"http://{resolved_host}:{port}{normalized_path}"

    def tcp_host(self, host: str) -> str:
        return host or self.service_host

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.tcp_host(self.postgres_host)}:{self.postgres_port}/{self.postgres_database}"
        )

    @property
    def clickhouse_ping_url(self) -> str:
        return self.http_url(self.clickhouse_host, self.clickhouse_http_port, "/ping")

    @property
    def flowable_engine_url(self) -> str:
        return self.http_url(self.flowable_host, self.flowable_port, "/flowable-rest/service/management/engine")

    @property
    def airflow_health_url(self) -> str:
        return self.http_url(self.airflow_host, self.airflow_port, "/health")

    @property
    def opensearch_url(self) -> str:
        return self.http_url(self.opensearch_host, self.opensearch_port)

    @property
    def superset_health_url(self) -> str:
        return self.http_url(self.superset_host, self.superset_port, "/health")

    def service_endpoints(self) -> list[ServiceEndpoint]:
        return [
            ServiceEndpoint(name="clickhouse", url=self.clickhouse_ping_url),
            ServiceEndpoint(name="flowable", url=self.flowable_engine_url, required_statuses=(200, 401)),
            ServiceEndpoint(name="airflow", url=self.airflow_health_url),
            ServiceEndpoint(name="opensearch", url=self.opensearch_url),
            ServiceEndpoint(name="superset", url=self.superset_health_url),
        ]


settings = Settings()
