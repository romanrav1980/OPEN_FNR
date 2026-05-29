# OPEN FNR Pilot-Ready Remaining Work

Date: 2026-05-29
Status: handoff after real source landing wiring checkpoint.

## What Is Now Closed

| Area | Status | Evidence |
| --- | --- | --- |
| Central configuration for network addresses | closed | `CONFIGURATION_MANIFEST.md`, `tests/quality/test_no_hardcoded_network_config.py` |
| Audit flag default | closed | `OPEN_FNR_AUDIT_ENABLED=true`, backend audit tests |
| Publication outbound targets | closed for adapter layer | ERP/WMS/DWH/BI/auto-order configurable URLs |
| Supplier forecast sharing target | closed for adapter layer | `OPEN_FNR_SUPPLIER_FORECAST_SHARE_URL` |
| Procurement ERP target | closed for adapter layer | `docs/test-reports/sprint-procurement-erp-target/index.html` |
| Capacity TMS target | closed for adapter layer | `docs/test-reports/sprint-capacity-tms-target/index.html` |
| Store App task target | closed for adapter layer | `docs/test-reports/sprint-store-app-task-target/index.html` |
| Planogram target | closed for adapter layer | `docs/test-reports/sprint-planogram-target/index.html` |
| IdP provisioning target | closed for adapter layer | `docs/test-reports/sprint-idp-provisioning-target/index.html` |
| Pilot source landing wiring | closed for first pilot gate | `docs/test-reports/sprint-real-source-landing-wiring/index.html` |
| JWT/OIDC boundary | closed for first security gate | `docs/test-reports/sprint-jwt-oidc-boundary/index.html` |
| Shared policy layer | closed for first RBAC/ABAC gate | `docs/test-reports/sprint-shared-policy-layer/index.html` |
| Routed UI shell | closed for first navigation foundation | `docs/test-reports/sprint-routed-ui-shell/index.html` |
| Flowable deployment package | closed for deployment manifest/checksum gate | `docs/test-reports/sprint-flowable-deployment-package/index.html` |
| Backend regression | green | `python -m pytest` -> 409 passed |
| Frontend build | green | `npm.cmd run build` |
| DEV/STAGE compose config | green | `docker compose ... config --quiet` |

## Remaining Strategic Blocks

| Block | Goal | First implementation slice | Acceptance signal |
| --- | --- | --- | --- |
| Real inbound source connection | Replace sample manifests with real pilot POS/WMS/ERP/MDM/promo file drops or APIs | First landing gate implemented; next connect actual pilot files/API credentials | Real source files discovered, schema/DQ passed, clean publication ready |
| OIDC/JWT middleware | Authenticate real users and service clients | First FastAPI JWT boundary implemented; next add signature/JWKS verification details | Unauthorized calls rejected, valid token maps to user/roles |
| Shared policy layer | Replace endpoint-local role checks with reusable RBAC/ABAC policy | First `policy.py` implemented for Security API; next migrate remaining domain endpoints | Security tests cover positive/negative object-level access |
| Routed UI productization | Move from single Control Tower to operational pages | First hash-route shell implemented; next split modules into route-specific pages | E2E smoke covers forecast, replenishment, exceptions, admin |
| Process deployment pipeline | Deploy BPMN/DMN/CMMN into Flowable, not only validate XML | Deployment package API implemented; next add actual REST upload execution | DEV Flowable receives process definitions with version evidence |
| Production deployment decision | Choose Kubernetes or hardened production Compose | Deployment topology doc and environment matrix | PROD-like dry run has rollback and health checks |
| Pilot rehearsal | Run a limited real-data shadow pilot | Select stores/SKU, load history, run forecasts/orders without operational export | KPI baseline vs OPEN FNR report signed by business |

## Tactical Next Sprint Order

1. `PILOT-1 Shadow Pilot Pack`
   - generate pilot scope, source checklist, runbook and rollback plan;
   - run full daily cycle on limited store/SKU scope.

2. `PROC-DEPLOY-2 Flowable REST Upload`
   - send deployment package to Flowable REST;
   - save deployment id/version response;
   - add retry/error handling for Flowable unavailable.

## Current Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| No real source samples yet | Inbound pipeline cannot be proven end to end | Request POS/WMS/ERP/MDM/promo samples or API specs before RDI-1 |
| OIDC details unknown | Security middleware cannot be production-final | Use standards-based JWT config and document required issuer/audience/JWKS |
| UI is still one large file | Productization velocity and test isolation suffer | Start UI-1 with route split and API client, then move module by module |
| Flowable not yet deployment-backed | BPMN/DMN/CMMN are tested as artifacts but not runtime-deployed | Implement deployment script and version evidence |
| Performance still synthetic/smoke | EPYC sizing not proven on real data | Run pilot-scale synthetic plus first real-data profile before controlled export |

## Saved Context For Resume

- Latest pushed hardening commit at previous checkpoint: `87bdc09`.
- Backend regression count after PROC-DEPLOY-1: 409 tests passed.
- Target adapter reports are under `docs/test-reports`.
- The next autonomous implementation should start with `PILOT-1 Shadow Pilot Pack`.
