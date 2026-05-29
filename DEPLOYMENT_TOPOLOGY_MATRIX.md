# OPEN FNR Deployment Topology Matrix

Status: DEP-1 foundation  
Date: 2026-05-29

## Environment Matrix

| Environment | Runtime mode | Mock mode | Auth | Dev bypass | Orchestrator | Data |
| --- | --- | --- | --- | --- | --- | --- |
| DEV | `dev` | `true` | configurable | allowed | Docker Compose | synthetic/mock |
| TEST | `test` | `true` | configurable | allowed | Docker Compose | synthetic/masked |
| STAGE | `stage` | `false` | required | forbidden | Docker Compose first | masked or pilot real |
| PROD | `prod` | `false` | required | forbidden | Kubernetes recommended | real |

## Configuration Sources

| Environment | Template |
| --- | --- |
| DEV | `infra/dev/.env.example` |
| TEST | `infra/test/.env.example` |
| STAGE | `infra/stage/.env.example` |
| PROD | `infra/prod/.env.example` |

## Production Rules

- Production secrets must be injected by the orchestrator and must not appear in git.
- Production service URLs, hosts and ports must come from environment variables.
- Production must disable mock mode and auth dev bypass.
- Production must keep audit enabled.
- Kubernetes manifests or Helm chart are handled in DEP-2/DEP-3 after this topology gate.
