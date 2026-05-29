# OPEN FNR Pilot-Ready Remaining Work

Date: 2026-05-29
Status: handoff after Flowable REST upload gate checkpoint.

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
| Flowable REST upload gate | closed for configurable dry run and execute path | `docs/test-reports/sprint-flowable-rest-upload/index.html` |
| Pilot shadow pack | closed for first runbook/rollback package | `docs/test-reports/sprint-pilot-shadow-pack/index.html` |
| Backend regression | green | `python -m pytest` -> 414 passed |
| Frontend build | green | `npm.cmd run build` |
| DEV/STAGE compose config | green | `docker compose ... config --quiet` |

## Remaining Strategic Blocks

| Block | Goal | First implementation slice | Acceptance signal |
| --- | --- | --- | --- |
| Real inbound source connection | Replace sample manifests with real pilot POS/WMS/ERP/MDM/promo file drops or APIs | First landing gate implemented; next connect actual pilot files/API credentials | Real source files discovered, schema/DQ passed, clean publication ready |
| OIDC/JWT middleware | Authenticate real users and service clients | First FastAPI JWT boundary implemented; next add signature/JWKS verification details | Unauthorized calls rejected, valid token maps to user/roles |
| Shared policy layer | Replace endpoint-local role checks with reusable RBAC/ABAC policy | First `policy.py` implemented for Security API; next migrate remaining domain endpoints | Security tests cover positive/negative object-level access |
| Routed UI productization | Move from single Control Tower to operational pages | First hash-route shell implemented; next split modules into route-specific pages | E2E smoke covers forecast, replenishment, exceptions, admin |
| Process deployment pipeline | Deploy BPMN/DMN/CMMN into Flowable, not only validate XML | REST upload gate implemented; next execute against live Flowable credentials | DEV Flowable receives process definitions with version evidence |
| Production deployment decision | Choose Kubernetes or hardened production Compose | Deployment topology doc and environment matrix | PROD-like dry run has rollback and health checks |
| Pilot rehearsal | Run a limited real-data shadow pilot | Shadow pack implemented; next run with actual source files/API credentials | KPI baseline vs OPEN FNR report signed by business |

## Tactical Next Sprint Order

1. `REAL-PILOT-1 Actual Source Connection`
   - place or connect real POS/WMS/ERP/MDM/PROMO pilot data;
   - run `/data/ingestion/pilot-shadow-load/plan`;
   - run clean publication and daily gate on the real business date.

2. `PROC-DEPLOY-3 Live Flowable Deployment Evidence`
   - run `/process-deployment/packages/current/deploy` with `execute=true` against DEV Flowable;
   - save deployment id/version response from the live runtime;
   - add retry/error handling evidence for Flowable unavailable.

## Current Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| No real source samples yet | Real-data rehearsal cannot be proven end to end | Provide POS/WMS/ERP/MDM/promo files or API specs for `REAL-PILOT-1` |
| OIDC details unknown | Security middleware cannot be production-final | Fill issuer/audience/JWKS env values and add cryptographic signature validation |
| UI still keeps most modules in one file | Productization velocity and test isolation suffer | Continue route split module by module after pilot source wiring |
| Live Flowable deployment not yet executed | BPMN/DMN/CMMN are package-ready but not proven in live runtime | Run `PROC-DEPLOY-3` with credentials and capture deployment id evidence |
| Performance still synthetic/smoke | EPYC sizing not proven on real data | Run pilot-scale synthetic plus first real-data profile before controlled export |

## Saved Context For Resume

- Latest pushed hardening commit before this checkpoint: `4b5a9f1`; current checkpoint is the `Add Flowable REST upload gate` commit in git history.
- Backend regression count after PROC-DEPLOY-2: 414 tests passed.
- Target adapter reports are under `docs/test-reports`.
- The next autonomous implementation should start with `REAL-PILOT-1 Actual Source Connection` when real source files or API credentials are available.
