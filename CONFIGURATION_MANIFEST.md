# OPEN FNR Configuration Manifest

Status: mandatory project rule.

## Network Configuration Rule

IP addresses, host names and port numbers must not be hardcoded inside feature code, UI modules, process logic or tests.

All network addresses must be read from central project configuration:

- Backend: `apps/backend/open_fnr_api/config.py`
- Frontend: `apps/frontend/src/app_config.ts`
- Backend environment example: `.env.example`
- Frontend environment example: `apps/frontend/.env.example`
- Docker/development infrastructure: `infra/dev/.env.example` and `infra/dev/compose.yaml`

Backend runtime supports both a shared `OPEN_FNR_SERVICE_HOST` for local host access and per-service hosts such as `OPEN_FNR_POSTGRES_HOST`, `OPEN_FNR_CLICKHOUSE_HOST`, `OPEN_FNR_FLOWABLE_HOST`, `OPEN_FNR_AIRFLOW_HOST`, `OPEN_FNR_OPENSEARCH_HOST` and `OPEN_FNR_SUPERSET_HOST` for container networks.

Audit retention is controlled by `OPEN_FNR_AUDIT_RETENTION_DAYS`. Business-process event audit remains enabled by default through `OPEN_FNR_AUDIT_ENABLED=true`.

External integration endpoints must also be configured, not embedded in code. Outbound publication uses:

- `OPEN_FNR_ERP_EXPORT_URL`;
- `OPEN_FNR_WMS_EXPORT_URL`;
- `OPEN_FNR_DWH_EXPORT_URL`;
- `OPEN_FNR_BI_EXPORT_URL`;
- `OPEN_FNR_AUTO_ORDER_EXPORT_URL`;
- `OPEN_FNR_SUPPLIER_FORECAST_SHARE_URL`;
- `OPEN_FNR_TMS_CAPACITY_EXPORT_URL`;
- `OPEN_FNR_STORE_APP_TASK_EXPORT_URL`;
- `OPEN_FNR_PLANOGRAM_EXPORT_URL`;
- `OPEN_FNR_IDP_PROVISIONING_URL`;
- `OPEN_FNR_PUBLICATION_HTTP_TIMEOUT_SECONDS`.

Browser-to-backend access is controlled by `OPEN_FNR_CORS_ALLOW_ORIGINS`.

Authentication and OIDC/JWT boundary settings are centralized as:

- `OPEN_FNR_AUTH_ENABLED`;
- `OPEN_FNR_AUTH_DEV_BYPASS_ENABLED`;
- `OPEN_FNR_OIDC_ISSUER`;
- `OPEN_FNR_OIDC_AUDIENCE`;
- `OPEN_FNR_OIDC_JWKS_URL`.

Process Navigator settings are centralized as:

- `OPEN_FNR_ALLOWED_ENVIRONMENTS`;
- `OPEN_FNR_RUNTIME_MODE`;
- `OPEN_FNR_PROCESS_NAVIGATOR_CONFORMANCE_CACHE_TTL_SECONDS`;
- `OPEN_FNR_PROCESS_NAVIGATOR_CONFORMANCE_MAX_SECONDS`;
- `OPEN_FNR_PROCESS_NAVIGATOR_ALERT_DEDUP_WINDOW_SECONDS`;
- `OPEN_FNR_PROCESS_NAVIGATOR_POLL_ZOOM_0_1_SECONDS`;
- `OPEN_FNR_PROCESS_NAVIGATOR_POLL_ZOOM_2_3_SECONDS`;
- `OPEN_FNR_PROCESS_NAVIGATOR_POLL_ALERTS_SECONDS`;
- `OPEN_FNR_PROCESS_NAVIGATOR_POLL_INFRASTRUCTURE_SECONDS`;
- `OPEN_FNR_PROCESS_NAVIGATOR_ALERT_PAGE_SIZE`;
- `OPEN_FNR_PROCESS_NAVIGATOR_ALERT_MAX_PAGE_SIZE`;
- `OPEN_FNR_PROCESS_NAVIGATOR_BUSINESS_KEY_TYPES`;
- `OPEN_FNR_PROCESS_NAVIGATOR_BUSINESS_KEY_SEPARATOR`.

## Allowed Exceptions

The following files may contain default local development addresses because they are configuration sources:

- `.env.example`
- `apps/frontend/.env.example`
- `infra/test/.env.example`
- `infra/stage/.env.example`
- `apps/backend/open_fnr_api/config.py`
- `apps/frontend/src/app_config.ts`
- `infra/dev/.env.example`
- `infra/dev/compose.yaml`
- development scripts that only read or pass configuration values

## Required Practice

- New backend services must add host/port/path settings to `Settings`.
- New frontend links must use `localServiceUrl(...)`.
- New frontend API calls must use `apiUrl(...)`.
- Tests must assert behavior through configuration, not embedded addresses.
- Sprint reports may mention command evidence, but executable code must stay configuration-driven.
- Business process audit must be controlled by `OPEN_FNR_AUDIT_ENABLED`; default is enabled.
- Authentication must be controlled by `OPEN_FNR_AUTH_ENABLED`; DEV/TEST bypass must be controlled by `OPEN_FNR_AUTH_DEV_BYPASS_ENABLED` and disabled in STAGE/PROD configuration.
- Source file landing paths must be controlled by `OPEN_FNR_LANDING_ROOT_PATH`; source adapters must not hardcode local paths.
- Process artifact deployment paths must be controlled by `OPEN_FNR_PROCESS_ARTIFACTS_ROOT_PATH`; Flowable deployment packaging must not hardcode environment-specific paths.
- Flowable runtime upload must use configured `OPEN_FNR_FLOWABLE_HOST`, `OPEN_FNR_FLOWABLE_PORT`, `OPEN_FNR_FLOWABLE_HTTP_TIMEOUT_SECONDS`, `OPEN_FNR_FLOWABLE_REST_USERNAME` and `OPEN_FNR_FLOWABLE_REST_PASSWORD`; UI and API dry runs must not perform network upload unless `execute=true`.
- DEV/TEST may use explicit Flowable image credentials in `.env.example`; STAGE/PROD must inject runtime credentials from secrets and keep `OPEN_FNR_FLOWABLE_REST_PASSWORD` out of committed environment files.
- Publication, supplier, TMS capacity, Store App task, planogram and IdP/IAM target URLs must be controlled by the `OPEN_FNR_*_EXPORT_URL`, `OPEN_FNR_SUPPLIER_FORECAST_SHARE_URL`, `OPEN_FNR_TMS_CAPACITY_EXPORT_URL`, `OPEN_FNR_STORE_APP_TASK_EXPORT_URL`, `OPEN_FNR_PLANOGRAM_EXPORT_URL` and `OPEN_FNR_IDP_PROVISIONING_URL` settings; empty values mean local fallback mode only.
- Process Navigator environment selector, refresh intervals, conformance TTL, conformance timeout, alert deduplication window, pagination limits and business key formats must be controlled by `OPEN_FNR_PROCESS_NAVIGATOR_*` settings and `OPEN_FNR_ALLOWED_ENVIRONMENTS`.

## Quality Gate

`tests/quality/test_no_hardcoded_network_config.py` prevents hardcoded local IPs and known development ports in application code outside the central configuration files.
