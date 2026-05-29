# OPEN FNR Pilot-Ready Remaining Work

Date: 2026-05-29
Status: handoff after IdP readiness gate checkpoint.

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
| Live Flowable runtime evidence | closed for runtime-safe BPMN subset | `docs/test-reports/sprint-flowable-live-deployment/index.html` |
| Source batch BPMN repair | closed for 38 / 38 runtime-deployable BPMN | `docs/test-reports/sprint-source-batch-bpmn-repair/index.html` |
| Process runtime strategy | closed for BPMN runtime and DMN/CMMN governance boundary | `docs/test-reports/sprint-process-runtime-strategy/index.html` |
| JWT/JWKS signature verification | closed for RS256 production auth boundary | `docs/test-reports/sprint-jwt-jwks-signature/index.html` |
| IdP readiness gate | closed for issuer/audience/JWKS readiness diagnostics | `docs/test-reports/sprint-idp-readiness-gate/index.html` |
| Pilot shadow pack | closed for first runbook/rollback package | `docs/test-reports/sprint-pilot-shadow-pack/index.html` |
| Backend regression | green | `python -m pytest` -> 418 passed |
| Frontend build | green | `npm.cmd run build` |
| DEV/STAGE compose config | green | `docker compose ... config --quiet` |

## Remaining Strategic Blocks

| Block | Goal | First implementation slice | Acceptance signal |
| --- | --- | --- | --- |
| Real inbound source connection | Replace sample manifests with real pilot POS/WMS/ERP/MDM/promo file drops or APIs | First landing gate implemented; next connect actual pilot files/API credentials | Real source files discovered, schema/DQ passed, clean publication ready |
| OIDC/JWT middleware | Authenticate real users and service clients | RS256/JWKS signature verification and IdP readiness gate implemented; next connect real IdP values | Unauthorized calls rejected, valid signed token maps to user/roles |
| Shared policy layer | Replace endpoint-local role checks with reusable RBAC/ABAC policy | First `policy.py` implemented for Security API; next migrate remaining domain endpoints | Security tests cover positive/negative object-level access |
| Routed UI productization | Move from single Control Tower to operational pages | First hash-route shell implemented; next split modules into route-specific pages | E2E smoke covers forecast, replenishment, exceptions, admin |
| Process deployment pipeline | Deploy BPMN runtime subset and govern DMN/CMMN artifacts | Live DEV Flowable deployment completed for 38 runtime-safe BPMN files; DMN/CMMN boundary documented in API | Optional future DMN/CMMN runtime adapter |
| Production deployment decision | Choose Kubernetes or hardened production Compose | Deployment topology doc and environment matrix | PROD-like dry run has rollback and health checks |
| Pilot rehearsal | Run a limited real-data shadow pilot | Shadow pack implemented; next run with actual source files/API credentials | KPI baseline vs OPEN FNR report signed by business |

## Tactical Next Sprint Order

1. `REAL-PILOT-1 Actual Source Connection`
   - place or connect real POS/WMS/ERP/MDM/PROMO pilot data;
   - run `/data/ingestion/pilot-shadow-load/plan`;
   - run clean publication and daily gate on the real business date.

2. `REAL-IDP-1 IdP Configuration Rehearsal`
   - configure real issuer/audience/JWKS URL in STAGE;
   - run signed-token smoke with real IdP;
   - verify role/group claim mapping with business roles.

## Current Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| No real source samples yet | Real-data rehearsal cannot be proven end to end | Provide POS/WMS/ERP/MDM/promo files or API specs for `REAL-PILOT-1` |
| Real OIDC details unknown | Security middleware cannot be connected to the enterprise IdP yet | Fill issuer/audience/JWKS env values and run real signed-token smoke |
| UI still keeps most modules in one file | Productization velocity and test isolation suffer | Continue route split module by module after pilot source wiring |
| DMN/CMMN runtime adapters are optional future work | Decision/case artifacts are governed but not Flowable-runtime-executed | Keep strategy visible in API/UI and approve adapters only if business needs runtime execution |
| Performance still synthetic/smoke | EPYC sizing not proven on real data | Run pilot-scale synthetic plus first real-data profile before controlled export |

## Saved Context For Resume

- Latest pushed hardening commit before this checkpoint: `d562db6`; current checkpoint is the IdP readiness gate work.
- Backend regression count after REAL-IDP-1: 425 tests passed.
- Target adapter reports are under `docs/test-reports`.
- The next autonomous implementation should start with `REAL-PILOT-1 Actual Source Connection` when real source files or API credentials are available.
