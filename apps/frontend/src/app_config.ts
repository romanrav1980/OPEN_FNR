type ServiceConfig = {
  host: string;
  apiPort: string;
  airflowPort: string;
  flowablePort: string;
  clickhouseHttpPort: string;
  opensearchDashboardsPort: string;
  supersetPort: string;
  runtimeMode: string;
  allowedEnvironments: string[];
  processNavigatorPollZoom01Seconds: number;
  processNavigatorPollZoom23Seconds: number;
  processNavigatorPollAlertsSeconds: number;
  processNavigatorPollInfrastructureSeconds: number;
};

const env = import.meta.env;

function numberFromEnv(value: string | undefined, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function listFromEnv(value: string | undefined, fallback: string[]): string[] {
  const items = value
    ?.split(",")
    .map((item) => item.trim())
    .filter(Boolean);
  return items && items.length > 0 ? items : fallback;
}

export const serviceConfig: ServiceConfig = {
  host: env.VITE_OPEN_FNR_SERVICE_HOST ?? "127.0.0.1",
  apiPort: env.VITE_OPEN_FNR_API_PORT ?? "8000",
  airflowPort: env.VITE_OPEN_FNR_AIRFLOW_PORT ?? "18088",
  flowablePort: env.VITE_OPEN_FNR_FLOWABLE_PORT ?? "18080",
  clickhouseHttpPort: env.VITE_OPEN_FNR_CLICKHOUSE_HTTP_PORT ?? "18123",
  opensearchDashboardsPort: env.VITE_OPEN_FNR_OPENSEARCH_DASHBOARDS_PORT ?? "15601",
  supersetPort: env.VITE_OPEN_FNR_SUPERSET_PORT ?? "18089",
  runtimeMode: env.VITE_OPEN_FNR_RUNTIME_MODE ?? "dev",
  allowedEnvironments: listFromEnv(env.VITE_OPEN_FNR_ALLOWED_ENVIRONMENTS, ["dev", "test", "stage", "prod"]),
  processNavigatorPollZoom01Seconds: numberFromEnv(env.VITE_OPEN_FNR_PROCESS_NAVIGATOR_POLL_ZOOM_0_1_SECONDS, 60),
  processNavigatorPollZoom23Seconds: numberFromEnv(env.VITE_OPEN_FNR_PROCESS_NAVIGATOR_POLL_ZOOM_2_3_SECONDS, 30),
  processNavigatorPollAlertsSeconds: numberFromEnv(env.VITE_OPEN_FNR_PROCESS_NAVIGATOR_POLL_ALERTS_SECONDS, 30),
  processNavigatorPollInfrastructureSeconds: numberFromEnv(
    env.VITE_OPEN_FNR_PROCESS_NAVIGATOR_POLL_INFRASTRUCTURE_SECONDS,
    60,
  ),
};

export function localServiceUrl(port: string, path = ""): string {
  const normalizedPath = path.startsWith("/") || path === "" ? path : `/${path}`;
  return `http://${serviceConfig.host}:${port}${normalizedPath}`;
}

export function apiUrl(path = ""): string {
  return localServiceUrl(serviceConfig.apiPort, path);
}
