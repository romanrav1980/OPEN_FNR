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
- `OPEN_FNR_PUBLICATION_HTTP_TIMEOUT_SECONDS`.

Browser-to-backend access is controlled by `OPEN_FNR_CORS_ALLOW_ORIGINS`.

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
- Source file landing paths must be controlled by `OPEN_FNR_LANDING_ROOT_PATH`; source adapters must not hardcode local paths.
- Publication, supplier, TMS capacity, Store App task and planogram target URLs must be controlled by the `OPEN_FNR_*_EXPORT_URL`, `OPEN_FNR_SUPPLIER_FORECAST_SHARE_URL`, `OPEN_FNR_TMS_CAPACITY_EXPORT_URL`, `OPEN_FNR_STORE_APP_TASK_EXPORT_URL` and `OPEN_FNR_PLANOGRAM_EXPORT_URL` settings; empty values mean local fallback mode only.

## Quality Gate

`tests/quality/test_no_hardcoded_network_config.py` prevents hardcoded local IPs and known development ports in application code outside the central configuration files.
