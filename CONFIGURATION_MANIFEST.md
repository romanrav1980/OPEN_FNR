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
- Tests must assert behavior through configuration, not embedded addresses.
- Sprint reports may mention command evidence, but executable code must stay configuration-driven.

## Quality Gate

`tests/quality/test_no_hardcoded_network_config.py` prevents hardcoded local IPs and known development ports in application code outside the central configuration files.
