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


class Settings(BaseModel):
    app_name: str = env_str("APP_NAME", "OPEN FNR API")
    version: str = env_str("VERSION", "0.1.0")
    service_host: str = Field(default_factory=lambda: env_str("SERVICE_HOST", "127.0.0.1"))
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
    runtime_mode: str = Field(default_factory=lambda: env_str("RUNTIME_MODE", "dev"))
    mock_mode: bool = Field(default_factory=lambda: env_bool("MOCK_MODE", True))
    audit_enabled: bool = Field(default_factory=lambda: env_bool("AUDIT_ENABLED", False))

    def http_url(self, port: int, path: str = "") -> str:
        normalized_path = path if path.startswith("/") or path == "" else f"/{path}"
        return f"http://{self.service_host}:{port}{normalized_path}"

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.service_host}:{self.postgres_port}/{self.postgres_database}"
        )

    @property
    def clickhouse_ping_url(self) -> str:
        return self.http_url(self.clickhouse_http_port, "/ping")

    @property
    def flowable_engine_url(self) -> str:
        return self.http_url(self.flowable_port, "/flowable-rest/service/management/engine")

    @property
    def airflow_health_url(self) -> str:
        return self.http_url(self.airflow_port, "/health")

    @property
    def opensearch_url(self) -> str:
        return self.http_url(self.opensearch_port)

    @property
    def superset_health_url(self) -> str:
        return self.http_url(self.superset_port, "/health")

    def service_endpoints(self) -> list[ServiceEndpoint]:
        return [
            ServiceEndpoint(name="clickhouse", url=self.clickhouse_ping_url),
            ServiceEndpoint(name="flowable", url=self.flowable_engine_url, required_statuses=(200, 401)),
            ServiceEndpoint(name="airflow", url=self.airflow_health_url),
            ServiceEndpoint(name="opensearch", url=self.opensearch_url),
            ServiceEndpoint(name="superset", url=self.superset_health_url),
        ]


settings = Settings()
