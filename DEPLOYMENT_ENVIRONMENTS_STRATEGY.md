# OPEN FNR Deployment Environments Strategy

Date: 2026-05-28

## Purpose

Define how OPEN FNR is deployed across DEV, TEST, STAGE and PROD without hardcoded IP addresses or ports.

## Environment Matrix

| Environment | Purpose | Data | Deployment |
| --- | --- | --- | --- |
| DEV | local development | synthetic/mock | Docker Compose |
| TEST | automated integration tests | synthetic/masked | Docker Compose |
| STAGE | business UAT and release rehearsal | masked or pilot real data | Docker Compose first, Kubernetes later |
| PROD | production operations | real data | Kubernetes recommended |

## Current Implementation

| Contour | Status | Files |
| --- | --- | --- |
| DEV | available | `infra/dev/compose.yaml`, `infra/dev/.env.example` |
| TEST | configured | `infra/test/.env.example`, `infra/test/README.md` |
| STAGE | configured | `infra/stage/.env.example`, `infra/stage/README.md` |
| PROD | planned | to be added after orchestrator decision |

`infra/dev/compose.yaml` is parameterized by `OPEN_FNR_PROJECT`, so multiple local contours can run without container name collisions.

Runtime settings that must stay aligned across `.env.example` and `infra/*/.env.example`:

| Setting | DEV | TEST | STAGE | Purpose |
| --- | --- | --- | --- | --- |
| `OPEN_FNR_RUNTIME_MODE` | `dev` | `test` | `stage` | runtime contour marker |
| `OPEN_FNR_MOCK_MODE` | `true` | `true` | `false` | repository and fallback selection |
| `OPEN_FNR_AUDIT_ENABLED` | `true` | `true` | `true` | configurable business process audit |
| `OPEN_FNR_LANDING_ROOT_PATH` | `data/landing/dev` | `data/landing/test` | `data/landing/stage` | source file landing root |

## Commands

DEV:

```powershell
docker compose --env-file infra/dev/.env.example -f infra/dev/compose.yaml up -d
```

TEST:

```powershell
docker compose --env-file infra/test/.env.example -f infra/dev/compose.yaml up -d
```

STAGE:

```powershell
docker compose --env-file infra/stage/.env.example -f infra/dev/compose.yaml up -d
```

## Production Direction

Production should use Kubernetes when high availability is required:

- separate namespaces for application, data, observability and process engine;
- secrets through Kubernetes Secrets or external secret operator;
- persistent volumes for PostgreSQL, ClickHouse, OpenSearch and Superset;
- network policies;
- ingress with TLS;
- readiness/liveness probes;
- resource requests and limits;
- rolling deployment and rollback.

Docker Compose may be used only for non-critical single-node pilot rehearsal.

## Application Containers

The Compose file includes optional `app` profile services:

```powershell
docker compose --env-file infra/dev/.env.example -f infra/dev/compose.yaml --profile app up -d
```

| Service | Image source | Purpose |
| --- | --- | --- |
| `backend` | `apps/backend/Dockerfile` | FastAPI application container |
| `frontend` | `apps/frontend/Dockerfile` | Static React build served by nginx |

Backend container runtime uses per-service host variables for container network access while local host ports remain configured through `infra/*/.env.example`.

## Configuration Rule

All addresses, host names and ports must come from:

- `.env.example`;
- `infra/*/.env.example`;
- `apps/backend/open_fnr_api/config.py`;
- `apps/frontend/src/app_config.ts`;
- runtime secret/config management in production.

Feature code must not hardcode IP addresses or port numbers.

## Next Steps

1. Add production Kubernetes manifests or Helm chart after production orchestrator decision.
2. Add CI job to start TEST contour and run integration tests.
3. Add STAGE deployment checklist and release approval workflow.
4. Add backup/restore scripts for PostgreSQL and ClickHouse.
5. Add environment-specific runbooks.
