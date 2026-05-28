type ServiceConfig = {
  host: string;
  apiPort: string;
  airflowPort: string;
  flowablePort: string;
  clickhouseHttpPort: string;
  opensearchDashboardsPort: string;
  supersetPort: string;
};

const env = import.meta.env;

export const serviceConfig: ServiceConfig = {
  host: env.VITE_OPEN_FNR_SERVICE_HOST ?? "127.0.0.1",
  apiPort: env.VITE_OPEN_FNR_API_PORT ?? "8000",
  airflowPort: env.VITE_OPEN_FNR_AIRFLOW_PORT ?? "18088",
  flowablePort: env.VITE_OPEN_FNR_FLOWABLE_PORT ?? "18080",
  clickhouseHttpPort: env.VITE_OPEN_FNR_CLICKHOUSE_HTTP_PORT ?? "18123",
  opensearchDashboardsPort: env.VITE_OPEN_FNR_OPENSEARCH_DASHBOARDS_PORT ?? "15601",
  supersetPort: env.VITE_OPEN_FNR_SUPERSET_PORT ?? "18089",
};

export function localServiceUrl(port: string, path = ""): string {
  const normalizedPath = path.startsWith("/") || path === "" ? path : `/${path}`;
  return `http://${serviceConfig.host}:${port}${normalizedPath}`;
}

export function apiUrl(path = ""): string {
  return localServiceUrl(serviceConfig.apiPort, path);
}
