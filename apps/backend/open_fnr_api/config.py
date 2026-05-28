from pydantic import BaseModel


class ServiceEndpoint(BaseModel):
    name: str
    url: str
    required_statuses: tuple[int, ...] = (200,)


class Settings(BaseModel):
    app_name: str = "OPEN FNR API"
    version: str = "0.1.0"
    postgres_dsn: str = "postgresql://open_fnr:open_fnr_dev@localhost:15432/open_fnr"
    clickhouse_ping_url: str = "http://127.0.0.1:18123/ping"
    flowable_engine_url: str = "http://127.0.0.1:18080/flowable-rest/service/management/engine"
    airflow_health_url: str = "http://127.0.0.1:18088/health"
    opensearch_url: str = "http://127.0.0.1:19200"
    superset_health_url: str = "http://127.0.0.1:18089/health"

    def service_endpoints(self) -> list[ServiceEndpoint]:
        return [
            ServiceEndpoint(name="clickhouse", url=self.clickhouse_ping_url),
            ServiceEndpoint(name="flowable", url=self.flowable_engine_url, required_statuses=(200, 401)),
            ServiceEndpoint(name="airflow", url=self.airflow_health_url),
            ServiceEndpoint(name="opensearch", url=self.opensearch_url),
            ServiceEndpoint(name="superset", url=self.superset_health_url),
        ]


settings = Settings()

