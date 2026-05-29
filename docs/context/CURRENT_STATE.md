# OPEN FNR Current State

Last updated: 2026-05-29

## Active Work

Industrial hardening continues after real-ingestion I1-I5. The current focus is Supplement 1 production hardening and process observability: source SLA, ML lifecycle, acceptance gates and the new Process Navigator map.

Current backend regression status: 30 focused process navigator/process regression tests passed in the latest checkpoint; previous full regression status was 438 automated tests passed.

Latest planning and navigation additions:

- Supplement 1 sprint plan: `SUPPLEMENT_1_IMPLEMENTATION_SPRINT_PLAN.md`.
- Process Navigator map specification: `PROCESS_NAVIGATOR_MAP_SPEC.md`.
- Process Navigator backend API: `/process-navigator/map`, `/process-navigator/alerts`, `/process-navigator/processes/{process_key}/drilldown`.
- Tactical work plan updated in `NEXT_DELIVERY_PLAN.md`: SUP-1...SUP-10 and PN-1...PN-6 are now part of the delivery backlog.
- PN-2 Process Navigator UI Shell is implemented at `#/process-navigator` with zoom controls, map nodes, selected BPMN detail and alert tables.

## Local Infrastructure

Docker Compose development infrastructure is defined in `infra/dev/compose.yaml`.

Known local URLs are derived from central configuration, not hardcoded in application code:

| Service | URL |
| --- | --- |
| Airflow | `OPEN_FNR_SERVICE_HOST` + `OPEN_FNR_AIRFLOW_PORT` |
| Flowable | `OPEN_FNR_SERVICE_HOST` + `OPEN_FNR_FLOWABLE_PORT` |
| ClickHouse HTTP | `OPEN_FNR_SERVICE_HOST` + `OPEN_FNR_CLICKHOUSE_HTTP_PORT` |
| OpenSearch | `OPEN_FNR_SERVICE_HOST` + `OPEN_FNR_OPENSEARCH_PORT` |
| OpenSearch Dashboards | `OPEN_FNR_SERVICE_HOST` + `OPEN_FNR_OPENSEARCH_DASHBOARDS_PORT` |
| Superset | `OPEN_FNR_SERVICE_HOST` + `OPEN_FNR_SUPERSET_PORT` |

Network configuration rule: IP addresses, host names and port numbers are centralized in `CONFIGURATION_MANIFEST.md`, `.env.example`, `apps/frontend/.env.example`, `apps/backend/open_fnr_api/config.py` and `apps/frontend/src/app_config.ts`.

## Sprint 0 Artifacts

- FastAPI backend skeleton: `apps/backend`.
- React/Vite frontend shell: `apps/frontend`.
- Development BPMN smoke process: `processes/dev-healthcheck`.
- Encoding quality gate: `tests/quality/test_text_encoding.py`.
- Dev helper scripts: `scripts/dev`.

## Sprint 1 Artifacts

- Canonical ingestion contracts: `apps/backend/open_fnr_api/data_contracts.py`.
- Ingestion status API: `apps/backend/open_fnr_api/ingestion.py`.
- Data ingestion process artifacts: `processes/data-ingestion`.
- Airflow DAG skeleton: `orchestration/airflow/dags/daily_ingestion.py`.
- Dev SQL metadata/staging tables: `infra/dev/postgres/init/001_open_fnr.sql`, `infra/dev/clickhouse/init/001_open_fnr.sql`.
- UI Data Load Status section: `apps/frontend/src/main.tsx`, `apps/frontend/src/styles.css`.

## Sprint 2 Artifacts

- DQ API and models: `apps/backend/open_fnr_api/data_quality.py`.
- DQ tests: `tests/backend/test_data_quality.py`.
- DQ process artifacts: `processes/data-quality`.
- DQ storage structures: `open_fnr.dq_rules`, `open_fnr.dq_incidents`, `open_fnr.dq_error_rows`.
- UI Data Quality Console: `apps/frontend/src/main.tsx`, `apps/frontend/src/styles.css`.
- HTML test report with screenshot: `docs/test-reports/sprint-2-data-quality/index.html`.

## Sprint 3 Artifacts

- Feature Mart API and models: `apps/backend/open_fnr_api/feature_mart.py`.
- Feature Mart tests: `tests/backend/test_feature_mart.py`, `tests/data/test_feature_mart_rules.py`.
- Feature Mart process artifacts: `processes/feature-mart`.
- Feature mart build plan/run API: `/feature-mart/build-plans`, `/feature-mart/build-runs`.
- Feature mart build task in Process Engine: `task-feature-build-001`.
- Active matrix and feature store SQL structures in ClickHouse init script.
- Feature version metadata SQL structure in PostgreSQL init script.
- UI Feature Mart Status section with live API loading for build plan dependencies, validation rules and process task actions.
- HTML test report with screenshot: `docs/test-reports/sprint-3-feature-mart/index.html`.
- Feature build plan UI/process test report: `docs/test-reports/sprint-feature-build-plan/index.html`.

## Sprint 4 Artifacts

- Forecast API and metrics: `apps/backend/open_fnr_api/forecast.py`.
- Forecast tests: `tests/backend/test_forecast.py`.
- Regular forecast process artifacts: `processes/forecast`.
- Forecast version metadata SQL table in PostgreSQL init script.
- UI Regular Forecast Baseline section.
- HTML test report with screenshot: `docs/test-reports/sprint-4-regular-baseline/index.html`.

## Daily Pipeline Gate Artifacts

- Daily pipeline gate API: `apps/backend/open_fnr_api/daily_pipeline.py`.
- Pipeline endpoint: `/pipeline/daily-gate/run`.
- Pipeline stages: shadow-load source discovery, source contract DQ, clean canonical publication dry-run, feature mart build dry-run.
- UI Daily Pipeline Gate section with live API loading and per-stage owner/process/task details.
- Pipeline tests: `tests/backend/test_daily_pipeline.py`.
- Daily pipeline UI/process report: `docs/test-reports/sprint-daily-pipeline-gate/index.html`.

## Sprint 5 Artifacts

- Forecast Workbench API slice: `/forecast/workbench`.
- Forecast review BPMN/DMN/CMMN artifacts in `processes/forecast`.
- Forecast Workbench UI filters and chart panel.
- HTML test report with screenshot: `docs/test-reports/sprint-5-forecast-workbench/index.html`.

## Sprint 6 Artifacts

- ML model metadata API: `apps/backend/open_fnr_api/ml_models.py`.
- ML model tests: `tests/backend/test_ml_models.py`.
- Model candidate review BPMN/DMN/CMMN artifacts in `processes/ml`.
- UI Model Monitoring V1 section.
- HTML test report with screenshot: `docs/test-reports/sprint-6-ml-regular-model/index.html`.

## Sprint 7 Artifacts

- Promo API and validation: `apps/backend/open_fnr_api/promo.py`.
- Promo tests: `tests/backend/test_promo.py`.
- Promo BPMN/DMN/CMMN artifacts in `processes/promo`.
- UI Promo Workbench Draft section.
- HTML test report with screenshot: `docs/test-reports/sprint-7-promo-data-validation/index.html`.

## Sprint 8 Artifacts

- Promo uplift forecast API slice: `/promo/forecasts`.
- Regular forecast plus promo uplift separation in `apps/backend/open_fnr_api/promo.py`.
- Promo uplift tests in `tests/backend/test_promo.py`.
- Promo forecast BPMN/DMN/CMMN artifacts in `processes/promo`.
- UI Promo Forecast V1 section with regular/uplift/total forecast and reference promos.
- HTML test report with screenshot: `docs/test-reports/sprint-8-promo-uplift-forecast/index.html`.
- Data integration specification for factual sales, stock, in-transit and open orders: `DATA_INTEGRATION_SPEC.md`.

## Sprint 9 Artifacts

- Process Engine backend API: `apps/backend/open_fnr_api/process_engine.py`.
- Process Engine API tests: `tests/backend/test_process_engine.py`.
- Replenishment approval BPMN skeleton: `processes/process-engine/replenishment_approval_process.bpmn20.xml`.
- Task visibility DMN skeleton: `processes/process-engine/task_visibility_decision.dmn.xml`.
- Process exception CMMN skeleton: `processes/process-engine/process_exception_case.cmmn.xml`.
- UI Process Engine Task Inbox section with role filters, task actions and audit history.
- HTML test report with screenshot: `docs/test-reports/sprint-9-process-engine-foundation/index.html`.

## Sprint 10 Artifacts

- Promo approval API models and endpoints in `apps/backend/open_fnr_api/promo.py`.
- Promo approval route and RBAC task completion extensions in `apps/backend/open_fnr_api/process_engine.py`.
- Promo approval tests in `tests/backend/test_promo.py` and `tests/backend/test_process_engine.py`.
- Promo planning BPMN process: `processes/promo/promo_planning_process.bpmn20.xml`.
- Promo risk and route DMN rules: `processes/promo/promo_risk_classification.dmn.xml`, `processes/promo/promo_approval_route.dmn.xml`.
- Promo shortage CMMN case: `processes/promo/promo_shortage_case.cmmn.xml`.
- UI Promo Approval Process section with risk panel, decision actions, blocking errors, steps and timeline.
- HTML test report with screenshot: `docs/test-reports/sprint-10-promo-approval-process/index.html`.

## Sprint 11 Artifacts

- Replenishment API and projection models: `apps/backend/open_fnr_api/replenishment.py`.
- Replenishment tests: `tests/backend/test_replenishment.py`.
- Replenishment process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Replenishment calculation BPMN: `processes/replenishment/replenishment_calculation_process.bpmn20.xml`.
- Stock projection quality DMN: `processes/replenishment/stock_projection_quality_decision.dmn.xml`.
- Stock projection issue CMMN: `processes/replenishment/stock_projection_issue_case.cmmn.xml`.
- UI Inventory Projection section with projected stock graph, demand/open order/in-transit layers and stock-out warning.
- HTML test report with screenshot: `docs/test-reports/sprint-11-replenishment-foundation/index.html`.

## Sprint 12 Artifacts

- Order proposal API models and endpoints in `apps/backend/open_fnr_api/replenishment.py`.
- Order proposal tests in `tests/backend/test_replenishment.py`.
- Order proposal process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Order proposal BPMN: `processes/replenishment/order_proposal_generation_process.bpmn20.xml`.
- Order auto approval DMN: `processes/replenishment/order_auto_approval_decision.dmn.xml`.
- Order constraint DMN: `processes/replenishment/order_constraint_decision.dmn.xml`.
- Supplier constraint CMMN: `processes/replenishment/supplier_constraint_case.cmmn.xml`.
- UI Order Proposal V1 section with formula breakdown, raw vs rounded order, statuses and constraint flags.
- HTML test report with screenshot: `docs/test-reports/sprint-12-order-proposal-v1/index.html`.

## Sprint 13 Artifacts

- Replenishment Workbench API and adjustment endpoint in `apps/backend/open_fnr_api/replenishment.py`.
- Workbench tests in `tests/backend/test_replenishment.py`.
- Manual review DMN: `processes/replenishment/manual_review_required_decision.dmn.xml`.
- Order exception CMMN: `processes/replenishment/order_exception_case.cmmn.xml`.
- UI Replenishment Workbench section with filters, final orders, adjustment preview, actions and audit trail.
- HTML test report with screenshot: `docs/test-reports/sprint-13-replenishment-workbench-v1/index.html`.

## Sprint 14 Artifacts

- Exception Center API: `apps/backend/open_fnr_api/exceptions.py`.
- Exception Center tests: `tests/backend/test_exceptions.py`.
- Exception escalation BPMN: `processes/exceptions/exception_escalation_process.bpmn20.xml`.
- Exception severity DMN: `processes/exceptions/exception_severity_decision.dmn.xml`.
- Exception owner routing DMN: `processes/exceptions/exception_owner_routing.dmn.xml`.
- Generic exception CMMN: `processes/exceptions/generic_exception_case.cmmn.xml`.
- UI Exception Center section with filters, linked objects, recommended actions, action panel and audit trail.
- HTML test report with screenshot: `docs/test-reports/sprint-14-exception-center-v1/index.html`.

## Sprint 15 Artifacts

- Manual adjustments API: `apps/backend/open_fnr_api/adjustments.py`.
- Manual adjustments tests: `tests/backend/test_adjustments.py`.
- Manual adjustment BPMN: `processes/adjustments/manual_adjustment_process.bpmn20.xml`.
- Adjustment approval DMN: `processes/adjustments/adjustment_approval_required_decision.dmn.xml`.
- Adjustment dispute CMMN: `processes/adjustments/adjustment_dispute_case.cmmn.xml`.
- UI Manual Adjustments section with reason, validity, preview impact, apply/cancel actions and audit timeline.
- HTML test report with screenshot: `docs/test-reports/sprint-15-manual-adjustments/index.html`.

## Sprint 16 Artifacts

- Publication API: `apps/backend/open_fnr_api/publication.py`.
- Publication tests: `tests/backend/test_publication.py`.
- Publication outbound HTTP adapter with per-target env URLs for ERP, WMS, DWH, BI and auto-order integrations.
- Publication BPMN: `processes/publication/publication_process.bpmn20.xml`.
- Publication eligibility DMN: `processes/publication/publication_eligibility_decision.dmn.xml`.
- Export failure CMMN: `processes/publication/export_failure_case.cmmn.xml`.
- UI Publication Console section with package list, statuses, idempotency keys, retry action, error details and linked exceptions.
- HTML test report with screenshot: `docs/test-reports/sprint-16-publication-export-v1/index.html`.
- Outbound publication target hardening report: `docs/test-reports/sprint-outbound-publication-targets/index.html`.

## Sprint 17 Artifacts

- KPI API: `apps/backend/open_fnr_api/kpi.py`.
- KPI tests: `tests/backend/test_kpi.py`.
- Weekly KPI review BPMN: `processes/kpi/weekly_kpi_review_process.bpmn20.xml`.
- KPI alert DMN: `processes/kpi/kpi_alert_decision.dmn.xml`.
- KPI degradation CMMN: `processes/kpi/kpi_degradation_case.cmmn.xml`.
- UI Accuracy And KPI Dashboard section with filters, trend visual, KPI table, review task and SKU drill-down.
- HTML test report with screenshot: `docs/test-reports/sprint-17-accuracy-kpi-dashboards/index.html`.

## Sprint 18 Artifacts

- Fresh replenishment models and endpoints in `apps/backend/open_fnr_api/replenishment.py`.
- Fresh tests in `tests/backend/test_replenishment.py`.
- Fresh order review BPMN: `processes/fresh/fresh_order_review_process.bpmn20.xml`.
- Fresh spoilage risk DMN: `processes/fresh/fresh_spoilage_risk_decision.dmn.xml`.
- High spoilage risk CMMN: `processes/fresh/high_spoilage_risk_case.cmmn.xml`.
- UI Fresh Workbench section with shelf-life batches, FEFO, waste graph, availability-vs-waste preview and fresh adjustment.
- HTML test report with screenshot: `docs/test-reports/sprint-18-fresh-v1/index.html`.

## Sprint 19 Artifacts

- SKU lifecycle API: `apps/backend/open_fnr_api/lifecycle.py`.
- SKU lifecycle tests: `tests/backend/test_lifecycle.py`.
- SKU phase-in BPMN: `processes/lifecycle/sku_phase_in_process.bpmn20.xml`.
- SKU phase-out BPMN: `processes/lifecycle/sku_phase_out_process.bpmn20.xml`.
- Lifecycle order allowed DMN: `processes/lifecycle/lifecycle_order_allowed_decision.dmn.xml`.
- Clearance risk CMMN: `processes/lifecycle/clearance_risk_case.cmmn.xml`.
- UI SKU Lifecycle section with reference product, cold-start forecast, termination date, replacement link and clearance risk warning.
- HTML test report with screenshot: `docs/test-reports/sprint-19-lifecycle-sku-v1/index.html`.

## Sprint 20 Artifacts

- Multi-echelon API: `apps/backend/open_fnr_api/multi_echelon.py`.
- Multi-echelon tests: `tests/backend/test_multi_echelon.py`.
- DC replenishment process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- DC replenishment BPMN: `processes/multi-echelon/dc_replenishment_process.bpmn20.xml`.
- DC allocation priority DMN: `processes/multi-echelon/dc_allocation_priority_decision.dmn.xml`.
- DC shortage CMMN: `processes/multi-echelon/dc_shortage_case.cmmn.xml`.
- UI Supply Chain Dashboard section with DC demand, shortage, allocation preview, drill-down and action panel.
- HTML test report with screenshot: `docs/test-reports/sprint-20-multi-echelon-v1/index.html`.

## Sprint 21 Artifacts

- Performance API: `apps/backend/open_fnr_api/performance.py`.
- Performance tests: `tests/backend/test_performance.py`.
- Synthetic scale helper: `scripts/performance/generate-synthetic-scale.ps1`.
- Performance process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Performance test run BPMN: `processes/performance/performance_test_run_process.bpmn20.xml`.
- Performance gate DMN: `processes/performance/performance_gate_decision.dmn.xml`.
- Performance regression CMMN: `processes/performance/performance_regression_case.cmmn.xml`.
- UI Performance Gate 1 section with pilot-scale profile, metric table, bottlenecks, gate actions and waiver case.
- HTML test report with screenshot: `docs/test-reports/sprint-21-performance-gate-1/index.html`.

## Sprint 22 Artifacts

- Security API: `apps/backend/open_fnr_api/security.py`.
- Security tests: `tests/backend/test_security.py`.
- IdP provisioning send API with service account gate, local fallback and configurable `OPEN_FNR_IDP_PROVISIONING_URL`.
- JWT/OIDC auth middleware and `/auth/context` API: `apps/backend/open_fnr_api/auth.py`.
- Shared policy layer for roles, service accounts and object scope: `apps/backend/open_fnr_api/policy.py`.
- Security process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Access request BPMN: `processes/security/access_request_process.bpmn20.xml`.
- Role assignment DMN: `processes/security/role_assignment_decision.dmn.xml`.
- Security incident CMMN: `processes/security/security_incident_case.cmmn.xml`.
- UI Admin Console V1 section with live Security API status, roles, region/category scopes, access requests, IdP target provisioning, audit viewer and denied-state explanation.
- HTML test report with screenshot: `docs/test-reports/sprint-22-security-rbac/index.html`.
- IdP provisioning target hardening report: `docs/test-reports/sprint-idp-provisioning-target/index.html`.
- JWT/OIDC boundary test report: `docs/test-reports/sprint-jwt-oidc-boundary/index.html`.
- Shared policy layer test report: `docs/test-reports/sprint-shared-policy-layer/index.html`.

## Sprint 23 Artifacts

- Stage rehearsal API: `apps/backend/open_fnr_api/stage.py`.
- Stage rehearsal tests: `tests/backend/test_stage.py`.
- Stage process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Stage daily cycle BPMN: `processes/stage/stage_daily_cycle_process.bpmn20.xml`.
- Stage go/no-go DMN: `processes/stage/stage_go_no_go_decision.dmn.xml`.
- Stage UAT CMMN: `processes/stage/stage_uat_case.cmmn.xml`.
- UI Stage Rehearsal section with full daily cycle, stage snapshot, UAT checklist and go/no-go readiness.
- HTML test report with screenshot: `docs/test-reports/sprint-23-stage-rehearsal/index.html`.

## Sprint 24 Artifacts

- Business Pilot API: `apps/backend/open_fnr_api/pilot.py`.
- Business Pilot tests: `tests/backend/test_pilot.py`.
- Pilot shadow pack API: `/pilot/shadow-pack`.
- Pilot process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Pilot operational BPMN: `processes/pilot/pilot_operational_process.bpmn20.xml`.
- Pilot acceptance DMN: `processes/pilot/pilot_acceptance_decision.dmn.xml`.
- Pilot exception CMMN: `processes/pilot/pilot_exception_case.cmmn.xml`.
- UI Business Pilot Dashboard section with pilot scope, KPI panel, feedback, known issues and acceptance action.
- HTML test report with screenshot: `docs/test-reports/sprint-24-business-pilot/index.html`.
- Pilot shadow pack test report: `docs/test-reports/sprint-pilot-shadow-pack/index.html`.

## Sprint 25 Artifacts

- Production Data Scale API: `apps/backend/open_fnr_api/data_scale.py`.
- Production Data Scale tests: `tests/backend/test_data_scale.py`.
- Data-scale process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Industrial data load BPMN: `processes/data-scale/industrial_data_load_process.bpmn20.xml`.
- Industrial DQ gate DMN: `processes/data-scale/industrial_dq_gate_decision.dmn.xml`.
- Large-scale data incident CMMN: `processes/data-scale/large_scale_data_incident_case.cmmn.xml`.
- UI Production Data Scale section with industrial profile, partition health, lineage and DQ gate actions.
- HTML test report with screenshot: `docs/test-reports/sprint-25-production-data-scale/index.html`.

## Sprint 26 Artifacts

- ML Governance API: `apps/backend/open_fnr_api/ml_governance.py`.
- ML Governance tests: `tests/backend/test_ml_governance.py`.
- ML governance process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Model release BPMN: `processes/ml-governance/model_release_process.bpmn20.xml`.
- Model release gate DMN: `processes/ml-governance/model_release_gate_decision.dmn.xml`.
- Model drift CMMN: `processes/ml-governance/model_drift_case.cmmn.xml`.
- UI Model Monitoring V2 section with drift panel, shadow comparison, release approval and rollback actions.
- HTML test report with screenshot: `docs/test-reports/sprint-26-production-ml-retraining/index.html`.

## Sprint 27 Artifacts

- Replenishment Scale API: `apps/backend/open_fnr_api/replenishment_scale.py`.
- Replenishment Scale tests: `tests/backend/test_replenishment_scale.py`.
- Replenishment scale process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Industrial replenishment BPMN: `processes/replenishment-scale/industrial_replenishment_process.bpmn20.xml`.
- Bulk auto approval DMN: `processes/replenishment-scale/bulk_auto_approval_decision.dmn.xml`.
- Replenishment scale exception CMMN: `processes/replenishment-scale/replenishment_scale_exception_case.cmmn.xml`.
- UI Production Replenishment Scale section with partitioned proposal counts, bulk approval, retention and async export.
- HTML test report with screenshot: `docs/test-reports/sprint-27-production-replenishment-scale/index.html`.

## Sprint 28 Artifacts

- Process Governance API: `apps/backend/open_fnr_api/process_governance.py`.
- Process Governance tests: `tests/backend/test_process_governance.py`.
- Process deployment package API: `apps/backend/open_fnr_api/process_deployment.py`.
- Process deployment tests: `tests/backend/test_process_deployment.py`.
- Process governance definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Process change management BPMN: `processes/process-governance/process_change_management_process.bpmn20.xml`.
- Process change risk DMN: `processes/process-governance/process_change_risk_decision.dmn.xml`.
- Process incident CMMN: `processes/process-governance/process_incident_case.cmmn.xml`.
- UI Process Governance section with process versions, change request, deployment, migration and rollback actions.
- HTML test report with screenshot: `docs/test-reports/sprint-28-process-governance/index.html`.

## Sprint 29 Artifacts

- Observability API: `apps/backend/open_fnr_api/observability.py`.
- Observability tests: `tests/backend/test_observability.py`.
- Observability process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Incident management BPMN: `processes/observability/incident_management_process.bpmn20.xml`.
- Incident severity DMN: `processes/observability/incident_severity_decision.dmn.xml`.
- Production incident CMMN: `processes/observability/production_incident_case.cmmn.xml`.
- UI Ops Dashboard section with alerts, incidents, runbooks, trace/log search and action panel.
- HTML test report with screenshot: `docs/test-reports/sprint-29-observability-support/index.html`.

## Sprint 30 Artifacts

- Release Gate API: `apps/backend/open_fnr_api/release_gate.py`.
- Release Gate tests: `tests/backend/test_release_gate.py`.
- Release gate process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Release go/no-go BPMN: `processes/release-gate/release_go_no_go_process.bpmn20.xml`.
- Release readiness DMN: `processes/release-gate/release_readiness_decision.dmn.xml`.
- Release risk CMMN: `processes/release-gate/release_risk_case.cmmn.xml`.
- UI Release Readiness Dashboard section with checklist, risks and go/no-go actions.
- HTML test report with screenshot: `docs/test-reports/sprint-30-industrial-release-gate/index.html`.

## Sprint 31 Artifacts

- Procurement API: `apps/backend/open_fnr_api/procurement.py`.
- Procurement tests: `tests/backend/test_procurement.py`.
- Procurement ERP export send API with service account gate, local fallback and configurable `OPEN_FNR_ERP_EXPORT_URL`.
- Procurement process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Purchase proposal BPMN: `processes/procurement/purchase_proposal_process.bpmn20.xml`.
- Supplier selection DMN: `processes/procurement/supplier_selection_decision.dmn.xml`.
- Supplier share exception DMN: `processes/procurement/supplier_share_exception_decision.dmn.xml`.
- Supplier constraint CMMN: `processes/procurement/supplier_constraint_case.cmmn.xml`.
- UI Purchase Proposal section with supplier comparison, target share warning and configurable ERP target export action.
- HTML test report with screenshot: `docs/test-reports/sprint-31-procurement-optimization/index.html`.
- Procurement ERP target hardening report: `docs/test-reports/sprint-procurement-erp-target/index.html`.

## Sprint 32 Artifacts

- Shelf Space API: `apps/backend/open_fnr_api/shelf_space.py`.
- Shelf Space tests: `tests/backend/test_shelf_space.py`.
- Planogram export send API with service account gate, local fallback and configurable `OPEN_FNR_PLANOGRAM_EXPORT_URL`.
- Shelf Space process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Shelf space review BPMN: `processes/shelf-space/shelf_space_review_process.bpmn20.xml`.
- Display capacity DMN: `processes/shelf-space/display_capacity_decision.dmn.xml`.
- Direct-to-shelf DMN: `processes/shelf-space/direct_to_shelf_decision.dmn.xml`.
- Shelf capacity exception CMMN: `processes/shelf-space/shelf_capacity_exception_case.cmmn.xml`.
- UI Shelf Space section with planogram, zone filters, display warnings, API status, planogram target export and direct-to-shelf recommendation.
- HTML test report with screenshot: `docs/test-reports/sprint-32-shelf-space-optimization/index.html`.
- Planogram target hardening report: `docs/test-reports/sprint-planogram-target/index.html`.

## Sprint 33 Artifacts

- Capacity API: `apps/backend/open_fnr_api/capacity.py`.
- Capacity tests: `tests/backend/test_capacity.py`.
- Capacity TMS export send API with service account gate, local fallback and configurable `OPEN_FNR_TMS_CAPACITY_EXPORT_URL`.
- Capacity process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Capacity smoothing BPMN: `processes/capacity/capacity_smoothing_process.bpmn20.xml`.
- Capacity overload DMN: `processes/capacity/capacity_overload_decision.dmn.xml`.
- Order shift priority DMN: `processes/capacity/order_shift_priority_decision.dmn.xml`.
- Capacity overload CMMN: `processes/capacity/capacity_overload_case.cmmn.xml`.
- UI Capacity Workbench section with overload calendar, smoothing preview, affected orders, live API status and configurable TMS target export action.
- HTML test report with screenshot: `docs/test-reports/sprint-33-capacity-workload/index.html`.
- Capacity TMS target hardening report: `docs/test-reports/sprint-capacity-tms-target/index.html`.

## Sprint 34 Artifacts

- Supply Chain Diagnostics API: `apps/backend/open_fnr_api/diagnostics.py`.
- Diagnostics tests: `tests/backend/test_diagnostics.py`.
- Diagnostics process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Diagnostic insight review BPMN: `processes/diagnostics/diagnostic_insight_review_process.bpmn20.xml`.
- Root cause classification DMN: `processes/diagnostics/root_cause_classification_decision.dmn.xml`.
- Diagnostic case CMMN: `processes/diagnostics/diagnostic_case.cmmn.xml`.
- UI Supply Chain Diagnostics section with root cause card, evidence rows, linked objects and exception action.
- HTML test report with screenshot: `docs/test-reports/sprint-34-supply-chain-diagnostics/index.html`.

## Sprint 35 Artifacts

- Supplier Collaboration API: `apps/backend/open_fnr_api/supplier_collaboration.py`.
- Supplier Collaboration tests: `tests/backend/test_supplier_collaboration.py`.
- Supplier forecast share send API with service account gate, local fallback and configurable HTTP target URL.
- Supplier collaboration process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Supplier collaboration BPMN: `processes/supplier-collaboration/supplier_collaboration_process.bpmn20.xml`.
- Supplier risk DMN: `processes/supplier-collaboration/supplier_risk_decision.dmn.xml`.
- Supplier shortage CMMN: `processes/supplier-collaboration/supplier_shortage_case.cmmn.xml`.
- UI Supplier Collaboration section with forecast share, supplier confirmation, performance and exception actions.
- HTML test report with screenshot: `docs/test-reports/sprint-35-supplier-collaboration/index.html`.
- Supplier forecast sharing target hardening report: `docs/test-reports/sprint-supplier-forecast-sharing-target/index.html`.

## Sprint 36 Artifacts

- Store Management API: `apps/backend/open_fnr_api/store_management.py`.
- Store Management tests: `tests/backend/test_store_management.py`.
- Store App task dispatch API with service account gate, local fallback and configurable `OPEN_FNR_STORE_APP_TASK_EXPORT_URL`.
- Store management process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Store task BPMN: `processes/store-management/store_task_process.bpmn20.xml`.
- True inventory confidence DMN: `processes/store-management/true_inventory_confidence_decision.dmn.xml`.
- Store task priority DMN: `processes/store-management/store_task_priority_decision.dmn.xml`.
- Inventory mismatch CMMN: `processes/store-management/inventory_mismatch_case.cmmn.xml`.
- UI True Inventory And Store Management section with virtual stock, confidence, store tasks, API status, Store App target dispatch and feedback audit.
- HTML test report with screenshot: `docs/test-reports/sprint-36-true-inventory-store-management/index.html`.
- Store App task target hardening report: `docs/test-reports/sprint-store-app-task-target/index.html`.

## Verification

- `python -m pytest` -> 438 passed.
- `npm.cmd install` in `apps/frontend` -> completed, 0 vulnerabilities.
- `npm.cmd run build` in `apps/frontend` -> completed.
- `docker compose --env-file infra/test/.env.example -f infra/dev/compose.yaml config --quiet` -> TEST compose config valid.
- `docker compose --env-file infra/stage/.env.example -f infra/dev/compose.yaml config --quiet` -> STAGE compose config valid.
- `docker compose --env-file infra/dev/.env.example -f infra/dev/compose.yaml config --quiet` -> DEV compose config valid.
- `powershell -ExecutionPolicy Bypass -File scripts/dev/health.ps1` -> all dev services OK.
- `docker compose --env-file infra/dev/.env.example -f infra/dev/compose.yaml ps` -> services up.

## Next Step

Real-ingestion I1-I5 contracts, pilot shadow-load source wiring, outbound target adapters, JWT/OIDC boundary with RS256/JWKS verification and IdP readiness gate, shared policy layer, routed UI shell, Flowable deployment package, Flowable REST upload gate, live Flowable runtime evidence, source batch BPMN repair, BPMN cognitive quality gate, process runtime strategy, Supplement 1 governance gates and pilot shadow pack are implemented and verified. Next: configure real IdP values, then connect actual pilot source files/API credentials and run a real-data rehearsal.

## Post-Sprint Planning Artifacts

- Documentation audit and synchronization: `DOCUMENTATION_AUDIT_AND_SYNC.md`.
- Next delivery plan: `NEXT_DELIVERY_PLAN.md`.
- Industrial hardening sprint plan: `INDUSTRIAL_HARDENING_SPRINTS.md`.
- Deployment environments strategy: `DEPLOYMENT_ENVIRONMENTS_STRATEGY.md`.
- Real data ingestion pipelines: `REAL_DATA_INGESTION_PIPELINES.md`.
- Production security hardening: `PRODUCTION_SECURITY_HARDENING_PLAN.md`.
- UI productization: `UI_PRODUCTIZATION_PLAN.md`.
- Pilot launch: `PILOT_LAUNCH_PLAN.md`.
- Pilot-ready remaining work handoff: `PILOT_READY_REMAINING_WORK.md`.
- Real source landing wiring test report: `docs/test-reports/sprint-real-source-landing-wiring/index.html`.
- Routed UI shell test report: `docs/test-reports/sprint-routed-ui-shell/index.html`.
- Flowable deployment package test report: `docs/test-reports/sprint-flowable-deployment-package/index.html`.
- Flowable REST upload gate test report: `docs/test-reports/sprint-flowable-rest-upload/index.html`.
- Live Flowable deployment evidence report: `docs/test-reports/sprint-flowable-live-deployment/index.html`.
- Source batch BPMN repair report: `docs/test-reports/sprint-source-batch-bpmn-repair/index.html`.
- Process runtime strategy report: `docs/test-reports/sprint-process-runtime-strategy/index.html`.
- JWT/JWKS signature verification report: `docs/test-reports/sprint-jwt-jwks-signature/index.html`.
- IdP readiness gate report: `docs/test-reports/sprint-idp-readiness-gate/index.html`.
- Supplement 1 adoption matrix: `SUPPLEMENT_1_ADOPTION_MATRIX.md`.
- BPMN cognitive quality gate report: `docs/test-reports/sprint-bpmn-cognitive-quality/index.html`.

## H1 Industrial Hardening Artifacts

- Runtime and mock mode settings: `apps/backend/open_fnr_api/config.py`.
- Business audit recording flag: `OPEN_FNR_AUDIT_ENABLED=true` by default.
- Outbound publication target URLs configurable through `OPEN_FNR_ERP_EXPORT_URL`, `OPEN_FNR_WMS_EXPORT_URL`, `OPEN_FNR_DWH_EXPORT_URL`, `OPEN_FNR_BI_EXPORT_URL`, `OPEN_FNR_AUTO_ORDER_EXPORT_URL`, `OPEN_FNR_SUPPLIER_FORECAST_SHARE_URL`, `OPEN_FNR_TMS_CAPACITY_EXPORT_URL`, `OPEN_FNR_STORE_APP_TASK_EXPORT_URL`, `OPEN_FNR_PLANOGRAM_EXPORT_URL` and `OPEN_FNR_IDP_PROVISIONING_URL`.
- Repository boundary and in-memory audit repository: `apps/backend/open_fnr_api/repositories.py`.
- Audit API: `apps/backend/open_fnr_api/audit.py`.
- PostgreSQL audit and integration batch tables: `infra/dev/postgres/init/001_open_fnr.sql`.
- CI workflow: `.github/workflows/ci.yml`.
- Audit tests: `tests/backend/test_audit.py`.

## H2 Industrial Hardening Artifacts

- PostgreSQL connection management: `apps/backend/open_fnr_api/database.py`.
- PostgreSQL audit repository: `apps/backend/open_fnr_api/repositories.py`.
- Schema migration baseline: `open_fnr.schema_migrations` in `infra/dev/postgres/init/001_open_fnr.sql`.
- Repository tests: `tests/backend/test_repositories.py`.

## H3 Industrial Hardening Artifacts

- ClickHouse industrial mart DDL: `infra/dev/clickhouse/init/001_open_fnr.sql`.
- Mart metadata repository: `apps/backend/open_fnr_api/mart_repositories.py`.
- Mart metadata API: `apps/backend/open_fnr_api/marts.py`.
- Mart tests: `tests/backend/test_marts.py`, `tests/data/test_clickhouse_mart_schema.py`.

## I1 Real Data Ingestion Artifacts

- POS receipt-line contract: `PosSalesLine` in `apps/backend/open_fnr_api/data_contracts.py`.
- POS manifest endpoint: `/data/ingestion/manifests/pos-sales`.
- Pilot shadow-load plan endpoint: `/data/ingestion/pilot-shadow-load/plan`.
- Required pilot source contract matrix: `PILOT_REQUIRED_SOURCE_CONTRACTS` in `apps/backend/open_fnr_api/ingestion.py`.
- POS ingestion DAG skeleton: `orchestration/airflow/dags/pos_sales_ingestion.py`.
- Raw ClickHouse landing table: `open_fnr.raw_pos_sales_lines`.
- POS ingestion tests: `tests/backend/test_ingestion.py`, `tests/data/test_contract_validation.py`, `tests/data/test_clickhouse_pos_sales_schema.py`, `tests/orchestration/test_pos_sales_ingestion.py`.

## I2 Real Data Ingestion Artifacts

- WMS stock, open order and in-transit contracts: `apps/backend/open_fnr_api/data_contracts.py`.
- WMS manifest endpoints: `/data/ingestion/manifests/wms-stock`, `/data/ingestion/manifests/wms-open-orders`, `/data/ingestion/manifests/wms-in-transit`.
- WMS inventory DAG skeleton: `orchestration/airflow/dags/wms_inventory_ingestion.py`.
- Raw ClickHouse landing tables: `open_fnr.raw_wms_stock_snapshots`, `open_fnr.raw_wms_open_orders`, `open_fnr.raw_wms_in_transit`.
- WMS ingestion tests: `tests/backend/test_ingestion.py`, `tests/data/test_clickhouse_wms_schema.py`, `tests/orchestration/test_wms_inventory_ingestion.py`.

## I3 Real Data Ingestion Artifacts

- ERP price and order export status contracts: `apps/backend/open_fnr_api/data_contracts.py`.
- ERP manifest endpoints: `/data/ingestion/manifests/erp-prices`, `/data/ingestion/manifests/erp-order-statuses`.
- ERP commercial DAG skeleton: `orchestration/airflow/dags/erp_commercial_ingestion.py`.
- Raw ClickHouse landing tables: `open_fnr.raw_erp_prices`, `open_fnr.raw_erp_order_export_statuses`.
- ERP ingestion tests: `tests/backend/test_ingestion.py`, `tests/data/test_clickhouse_erp_schema.py`, `tests/orchestration/test_erp_commercial_ingestion.py`.

## I4 Real Data Ingestion Artifacts

- MDM product and store contracts: `apps/backend/open_fnr_api/data_contracts.py`.
- MDM manifest endpoints: `/data/ingestion/manifests/mdm-products`, `/data/ingestion/manifests/mdm-stores`.
- MDM reference DAG skeleton: `orchestration/airflow/dags/mdm_reference_ingestion.py`.
- Raw ClickHouse landing tables: `open_fnr.raw_mdm_products`, `open_fnr.raw_mdm_stores`.
- MDM ingestion tests: `tests/backend/test_ingestion.py`, `tests/data/test_clickhouse_mdm_schema.py`, `tests/orchestration/test_mdm_reference_ingestion.py`.

## I5 Real Data Ingestion Artifacts

- Promo plan contract: `apps/backend/open_fnr_api/data_contracts.py`.
- Promo manifest endpoint: `/data/ingestion/manifests/promo-plan`.
- Promo plan DAG skeleton: `orchestration/airflow/dags/promo_plan_ingestion.py`.
- Raw ClickHouse landing table: `open_fnr.raw_promo_plans`.
- Promo ingestion tests: `tests/backend/test_ingestion.py`, `tests/data/test_clickhouse_promo_schema.py`, `tests/orchestration/test_promo_plan_ingestion.py`.

## Real Ingestion Gate Artifacts

- Source readiness endpoint: `/data/ingestion/readiness`.
- Shadow-load gate API: `/data/ingestion/shadow-load/run`.
- Shadow-load gate creates recovery tasks for missing files and source-contract DQ blockers.
- Configurable local file source adapter: `apps/backend/open_fnr_api/source_adapters.py`.
- Local file discovery endpoint: `/data/source-adapters/local-files/discover`.
- Local file manifest sidecar support: `manifest.json` beside source files.
- Local file discovery excludes `manifest.json` from source data files and treats it only as sidecar metadata.
- Pilot landing sample generator: `apps/backend/open_fnr_api/pilot_fixtures.py`, `scripts/dev/generate-pilot-landing.ps1`.
- Pilot shadow-load discovery runner: `apps/backend/open_fnr_api/shadow_load.py`, `scripts/dev/run-shadow-load.ps1`.
- Source contract DQ plans: `/data-quality/source-contract-plans`.
- Source contract DQ execution API: `/data-quality/source-contract-runs`.
- DEV/TEST/STAGE Docker Compose validation uses a shared compose file with per-contour env files; service ports and Superset secret are parameterized through environment settings.
- Clean canonical ClickHouse tables for sales, stock, open orders, in-transit, prices and promo plans.
- Clean publication plan API: `/data/clean-publication/plans`.
- Clean publication run API: `/data/clean-publication/runs` with `dry_run`, `mock_run` and ClickHouse HTTP execution mode.
- Source batch publication BPMN/DMN/CMMN artifacts for Process Engine recovery and audit flow.
- Process Engine clean publication confirmation task: `task-clean-publication-001`.
- Pilot shadow load gate rules: `REAL_DATA_INGESTION_PIPELINES.md`.
- Developer/user presentation: `docs/presentations/real-ingestion-sprints-i1-i5/index.html`.

## Block Presentations

- Extended coverage sprints 31-36: `docs/presentations/extended-coverage-sprints-31-36/index.html`.
- Real ingestion sprints I1-I5: `docs/presentations/real-ingestion-sprints-i1-i5/index.html`.

## Process Navigator Supplement 1 Expansion

- Neighbor-agent additions in `PROCESS_NAVIGATOR_MAP_SPEC_SUPPLEMENT_1.md` are accepted as authoritative additions: async conformance, performance SLA, lazy loading, refresh strategy, RBAC matrix, business key tracking, alert deduplication and v2 boundaries.
- New implementation plan: `PROCESS_NAVIGATOR_IMPLEMENTATION_PLAN.md`.
- `NEXT_DELIVERY_PLAN.md` now tracks PN-3 through PN-12.
- PN-3 has started with backend contract hardening:
  - environment validation for `/process-navigator/*`;
  - snapshot mode on `/process-navigator/map`;
  - alert pagination fields;
  - generated timestamps and data freshness fields;
  - config settings in `apps/backend/open_fnr_api/config.py`, `.env.example` and `CONFIGURATION_MANIFEST.md`;
  - initial backend contracts for conformance, performance, versions, infrastructure health, business key tracking and weekly reports.
- PN-4 has started with a BPMN trace conformance evaluator:
  - `build_bpmn_flow_model()` parses executable BPMN flow nodes and sequence edges;
  - `evaluate_bpmn_trace()` detects `skipped_mandatory_step` and `unexpected_sequence`;
  - conformance async endpoints now use the trace evaluator for representative BPMN execution.
- PN-5 foundation has started with computed process performance metrics:
  - cycle time is derived from task/audit timestamps where available;
  - waiting and processing time are derived from human task timestamps;
  - throughput is grouped by business day;
  - rework rate is derived from `REWORK_REQUESTED` audit events.
- PN-6 has started with alert correlation and deduplication:
  - `deduplicate_alerts()` groups repeated alerts by source, process/domain and severity;
  - `correlate_alert_cause_chains()` builds BFS causal chains across process dependencies;
  - map responses expose `causal_edges` for cascaded degraded/blocked process nodes.
- PN-7 has started with config-driven business key tracking:
  - business key types and separator are controlled by `OPEN_FNR_PROCESS_NAVIGATOR_BUSINESS_KEY_TYPES` and `OPEN_FNR_PROCESS_NAVIGATOR_BUSINESS_KEY_SEPARATOR`;
  - `/process-navigator/tracking` supports `sku-store`, `forecast-run`, `order-proposal`, `replenishment-cycle` and `promo`;
  - tracking trail instance IDs are masked.
- PN-8 has started with backend RBAC boundary:
  - navigator endpoints accept `actor_role` while JWT auth is not yet mandatory in DEV;
  - role checks reuse shared `policy.py`;
  - `Supplier User`/`supplier` roles are blocked at backend level;
  - store roles are limited to zoom 0-1.
- PN-9 has completed the Process Navigator UI detail panel:
  - the UI consumes conformance, performance, versions and infrastructure health contracts;
  - process cards show conformance and active-version hints;
  - the detail panel exposes conformance, P95 cycle time, version breakdown and infrastructure risk;
  - the alert table separates root alerts from cascaded effects and displays cause chains;
  - contextual help footnotes link UI elements to task specs, process specs and BPMN artifacts.
- PN-9 evidence report:
  - `docs/test-reports/sprint-pn-9-process-navigator-ui/index.html`;
  - `docs/test-reports/sprint-pn-9-process-navigator-ui/screenshots/process-navigator-ui.png`.
- PN-10 has completed accessibility and refresh hardening:
  - frontend config now includes runtime mode, allowed environments and Process Navigator polling intervals;
  - Process Navigator UI has an environment selector and sends `env` to map, alert, drilldown, conformance, performance, versions and infrastructure endpoints;
  - the UI shows auto-refresh interval, generated timestamp and data freshness;
  - manual refresh increments a refresh tick without changing route state;
  - keyboard Escape zooms one semantic level out;
  - focus-visible styles, 44 CSS px touch targets and reduced-motion CSS are present.
- PN-10 evidence report:
  - `docs/test-reports/sprint-pn-10-accessibility-refresh/index.html`;
  - `docs/test-reports/sprint-pn-10-accessibility-refresh/screenshots/process-navigator-refresh.png`.
- PN-11 has completed reporting and Superset payload:
  - Airflow DAG skeleton `orchestration/airflow/dags/process_health_digest.py`;
  - weekly digest request keeps endpoint path, query, service host env and service port env separate;
  - stakeholder message preserves root causes, SLA breaches and `process_alert_history` dataset reference;
  - backend weekly report contract now verifies `env`, summary arrays and Superset dataset ref.
- PN-11 evidence report:
  - `docs/test-reports/sprint-pn-11-reporting-superset/index.html`;
  - `docs/test-reports/sprint-pn-11-reporting-superset/screenshots/process-navigator-report-context.png`.
- PN-12 has completed final load/regression/presentation:
  - performance smoke tests added in `tests/performance/test_process_navigator_performance.py`;
  - final regression report created at `docs/test-reports/sprint-pn-final/index.html`;
  - final Process Navigator screenshot created at `docs/test-reports/sprint-pn-final/screenshots/process-navigator-final.png`;
  - developer/user presentation created at `docs/presentations/process-navigator-pn3-pn12/index.html`.
- Process Navigator implementation plan now marks PN-3..PN-12 as completed; remaining PN sprints: 0.
- Process Navigator backend tests now cover 26 scenarios in `tests/backend/test_process_navigator.py`.
- Verification:
  - `npm.cmd run build` in `apps/frontend` -> passed.
  - `pytest tests/backend/test_process_navigator.py tests/orchestration/test_process_health_digest.py tests/performance/test_process_navigator_performance.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 34 passed, 1 warning about `.pytest_cache` permissions.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 469 passed, 1 warning about `.pytest_cache` permissions.

## Remaining Project Focused Plan

- New tactical plan: `REMAINING_PROJECT_FOCUSED_SPRINT_PLAN.md`.
- The plan wraps all remaining work into focused releases and sprints:
  - `IH-1..IH-4` industrial hardening;
  - `RI-1..RI-6` real integrations;
  - `SEC-1..SEC-4` production security;
  - `UI-1..UI-5` UI productization;
  - `ML-1..ML-5` ML/replenishment production;
  - `DEP-1..DEP-4` deployment and operations;
  - `PILOT-1..PILOT-5` pilot launch.
- Focus rule: one active release at a time and at most one preparation sprint in discovery.
- Recommended next sprint: `IH-1 Persistence Inventory And Repository Boundaries`, followed by `IH-2 PostgreSQL Persistence And Migrations`.
- `NEXT_DELIVERY_PLAN.md` now references this focused sprint plan and uses it as the tactical source for remaining work.

## IH-1 Persistence Inventory

- IH-1 completed.
- New inventory document: `docs/persistence/PERSISTENCE_INVENTORY.md`.
- Production persistence targets are classified as:
  - `P0`: production decision state, target PostgreSQL in IH-2/IH-3;
  - `P1`: operational pilot/reconciliation state;
  - `P2`: analytical/model state, target ClickHouse and/or artifact metadata;
  - `D1`: DEV fixtures allowed while `OPEN_FNR_MOCK_MODE=true`;
  - `C1`: governed configuration/rule catalogs.
- Core P0 targets identified:
  - adjustments, exceptions, process tasks/audit, publication packages, order proposals/final orders, security users/service accounts/access requests and store tasks.
- Target repository names and IH-2 migration order are defined.
- Architecture guard added: `tests/architecture/test_persistence_inventory.py`.
- Verification:
  - `pytest tests/architecture/test_persistence_inventory.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 6 passed, 1 warning about `.pytest_cache` permissions.
- Next sprint: `IH-2 PostgreSQL Persistence And Migrations`.

## IH-2 PostgreSQL Persistence Foundation

- IH-2 completed as persistence foundation.
- Completion note: `docs/context/IH2_COMPLETION.md`.
- PostgreSQL schema foundation added in `infra/dev/postgres/init/001_open_fnr.sql`:
  - `open_fnr.process_tasks`;
  - `open_fnr.process_task_events`;
  - `open_fnr.operational_decisions`;
  - `open_fnr.publication_packages`;
  - `open_fnr.export_attempts`.
- Repository foundation added in `apps/backend/open_fnr_api/repositories.py`:
  - `ProcessTaskRecord`, `ProcessTaskEventRecord`, `OperationalDecisionRecord`;
  - `ProcessTaskRepository`, `OperationalDecisionRepository`;
  - in-memory implementations for `OPEN_FNR_MOCK_MODE=true`;
  - PostgreSQL implementations with upsert/idempotency behavior.
- Process runtime boundary:
  - `/process/tasks/{task_id}/complete` still returns the same API payload;
  - completion now writes completed task state and task events through `process_task_repository`.
- Publication/export boundary:
  - publication send/retry still returns the same API payload;
  - send/retry now writes `OperationalDecisionRecord` through `operational_decision_repository` with idempotency key.
- Replenishment decision boundary:
  - order proposal adjustment still returns the same API payload;
  - adjustment now writes `OperationalDecisionRecord` through `operational_decision_repository` with idempotency key.
- Store task decision boundary:
  - store task completion still returns the same API payload;
  - completion now writes `OperationalDecisionRecord` through `operational_decision_repository` with idempotency key and photo reference.
- Manual adjustment decision boundary:
  - adjustment action endpoints still return the same API payload;
  - apply/cancel/reject style actions now write `OperationalDecisionRecord`.
- Exception decision boundary:
  - exception action endpoint still returns the same API payload;
  - take/resolve/ignore/escalate actions now write `OperationalDecisionRecord`.
- `REMAINING_PROJECT_FOCUSED_SPRINT_PLAN.md` marks `IH-2` as in progress.
- `docs/persistence/PERSISTENCE_INVENTORY.md` now includes IH-2 foundation status and remaining domain-table migration list.
- Tests added/updated:
  - `tests/backend/test_repositories.py`;
  - `tests/backend/test_process_engine.py`;
  - `tests/backend/test_publication.py`;
  - `tests/backend/test_replenishment.py`;
  - `tests/backend/test_store_management.py`;
  - `tests/backend/test_adjustments.py`;
  - `tests/backend/test_exceptions.py`;
  - `tests/data/test_postgres_operational_schema.py`.
- Verification:
  - `pytest tests/backend/test_repositories.py tests/data/test_postgres_operational_schema.py tests/architecture/test_persistence_inventory.py` -> 10 passed, 1 warning about `.pytest_cache` permissions.
  - `pytest tests/backend/test_publication.py tests/backend/test_process_engine.py tests/backend/test_repositories.py` -> 27 passed, 1 warning about `.pytest_cache` permissions.
  - `pytest tests/backend/test_replenishment.py tests/backend/test_publication.py tests/backend/test_process_engine.py` -> 40 passed, 1 warning about `.pytest_cache` permissions.
  - `pytest tests/backend/test_store_management.py tests/backend/test_replenishment.py tests/backend/test_publication.py tests/backend/test_process_engine.py` -> 49 passed, 1 warning about `.pytest_cache` permissions.
  - `pytest tests/backend/test_adjustments.py tests/backend/test_exceptions.py tests/backend/test_store_management.py tests/backend/test_replenishment.py tests/backend/test_publication.py tests/backend/test_process_engine.py` -> 61 passed, 1 warning about `.pytest_cache` permissions.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 482 passed, 1 warning about `.pytest_cache` permissions.

## IH-3 Production Audit Event Storage

- IH-3 completed.
- Completion note: `docs/context/IH3_COMPLETION.md`.
- Audit retention configuration added:
  - `OPEN_FNR_AUDIT_RETENTION_DAYS`;
  - default is 1095 days.
- Audit repository now supports:
  - filtered search by actor, object type, object id, event type and correlation id;
  - retention purge by cutoff.
- Audit API now supports:
  - `GET /audit/events` with investigation filters;
  - `GET /audit/retention-plan`;
  - `POST /audit/retention/purge?actor_role=...` guarded to `Admin` and `Auditor`.
- PostgreSQL audit indexes added:
  - `ix_audit_events_correlation`;
  - `ix_audit_events_type`.
- Runbook added: `docs/runbooks/AUDIT_RETENTION_RUNBOOK.md`.
- Verification:
  - `pytest tests/backend/test_audit.py tests/backend/test_repositories.py tests/data/test_postgres_operational_schema.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 17 passed, 1 warning about `.pytest_cache` permissions.

## IH-4 Backup Restore Smoke

- IH-4 completed.
- Completion note: `docs/context/IH4_COMPLETION.md`.
- Backup/restore configuration added:
  - `OPEN_FNR_BACKUP_ROOT_PATH`;
  - `OPEN_FNR_BACKUP_RETENTION_DAYS`;
  - ClickHouse database/user/password entries in `.env.example`.
- Line ending policy updated: PowerShell scripts now use UTF-8/LF through `.gitattributes`.
- Backup smoke script:
  - `scripts/dev/backup-smoke.ps1`;
  - default `plan` mode;
  - explicit `execute` mode;
  - PostgreSQL dump checksum;
  - ClickHouse backup command through configured database and backup disk.
- Restore smoke script:
  - `scripts/dev/restore-smoke.ps1`;
  - default `plan` mode;
  - explicit `execute` mode;
  - mandatory backup manifest path;
  - dedicated restore database variables;
  - checksum validation before restore.
- Runbook added: `docs/runbooks/BACKUP_RESTORE_RUNBOOK.md`.
- Tests added:
  - `tests/scripts/test_backup_restore_scripts.py`.
- Verification:
  - `pytest tests/scripts/test_backup_restore_scripts.py tests/backend/test_config.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 15 passed, 1 warning about `.pytest_cache` permissions.
  - `backup-smoke.ps1 -Mode plan` and `restore-smoke.ps1 -Mode plan` passed through process-level PowerShell execution policy bypass.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 489 passed, 1 warning about `.pytest_cache` permissions.

## RI-1 Source Contracts Freeze

- RI-1 completed.
- Contract freeze document: `SOURCE_CONTRACTS_FREEZE.md`.
- Machine-checkable source contract registry added in `apps/backend/open_fnr_api/data_contracts.py`:
  - `SourceContractDefinition`;
  - `SOURCE_CONTRACT_MODELS`;
  - `SOURCE_CONTRACT_REGISTRY`;
  - `source_contract_summaries()`.
- `/data/contracts` now exposes:
  - legacy domain schemas;
  - frozen source contract list;
  - `freeze_status=ri_1_frozen`;
  - source contract count.
- Frozen pilot contracts:
  - `pos_sales_line`;
  - `wms_stock_snapshot_line`;
  - `wms_open_order_line`;
  - `wms_in_transit_line`;
  - `erp_price_line`;
  - `erp_order_export_status_line`;
  - `mdm_product_line`;
  - `mdm_store_line`;
  - `promo_plan_line`.
- Each frozen contract carries:
  - source system;
  - model name;
  - primary key;
  - required fields;
  - business owner role;
  - technical owner role;
  - source SLA label;
  - freshness field;
  - idempotency fields;
  - reconciliation keys;
  - required downstream capabilities;
  - blocking DQ checks.
- Tests added/updated:
  - `tests/data/test_source_contract_freeze.py`;
  - `tests/backend/test_ingestion.py`.
- Verification:
  - `pytest tests/backend/test_ingestion.py tests/data/test_contract_validation.py tests/data/test_source_contract_freeze.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 27 passed, 1 warning about `.pytest_cache` permissions.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 492 passed, 1 warning about `.pytest_cache` permissions.

## RI-2 POS And DWH Sales Ingestion

- RI-2 completed as ingestion foundation.
- Completion note: `docs/context/RI2_COMPLETION.md`.
- POS daily sales ingestion foundation remains active:
  - `PosSalesLine`;
  - `pos_sales_line`;
  - `orchestration/airflow/dags/pos_sales_ingestion.py`;
  - `open_fnr.raw_pos_sales_lines`.
- DWH sales history ingestion foundation added:
  - `DwhSalesHistoryLine`;
  - `dwh_sales_history_line`;
  - `GET /data/ingestion/manifests/dwh-sales-history`;
  - `orchestration/airflow/dags/dwh_sales_history_ingestion.py`;
  - `open_fnr.raw_dwh_sales_history`.
- Source readiness now includes DWH as first-class source for:
  - training history;
  - backtesting;
  - regular forecast;
  - promo forecast.
- `SOURCE_CONTRACTS_FREEZE.md` updated with DWH sales history row and SLA/DQ gates.
- Tests added/updated:
  - `tests/orchestration/test_dwh_sales_history_ingestion.py`;
  - `tests/data/test_clickhouse_pos_sales_schema.py`;
  - `tests/data/test_contract_validation.py`;
  - `tests/backend/test_ingestion.py`;
  - `tests/data/test_source_contract_freeze.py`.
- Verification:
  - `pytest tests/backend/test_ingestion.py tests/data/test_contract_validation.py tests/data/test_source_contract_freeze.py tests/data/test_clickhouse_pos_sales_schema.py tests/orchestration/test_pos_sales_ingestion.py tests/orchestration/test_dwh_sales_history_ingestion.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 33 passed, 1 warning about `.pytest_cache` permissions.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 496 passed, 1 warning about `.pytest_cache` permissions.

## RI-3 WMS Stock, In-Transit And Open Orders

- RI-3 completed as ingestion foundation.
- Completion note: `docs/context/RI3_COMPLETION.md`.
- WMS ingestion specification added: `WMS_INVENTORY_INGESTION_SPEC.md`.
- WMS contracts remain frozen in `SOURCE_CONTRACT_REGISTRY`:
  - `wms_stock_snapshot_line`;
  - `wms_open_order_line`;
  - `wms_in_transit_line`.
- Raw ClickHouse schemas are present:
  - `open_fnr.raw_wms_stock_snapshots`;
  - `open_fnr.raw_wms_open_orders`;
  - `open_fnr.raw_wms_in_transit`.
- WMS Airflow DAG now includes:
  - idempotent manifest creation;
  - schema validation;
  - DQ step;
  - reconciliation plan step;
  - clean publication placeholder.
- `build_wms_reconciliation_plan()` defines:
  - reconciliation keys;
  - downstream blockers;
  - SLA label `before_replenishment_cutoff`;
  - failure action for Supply Chain Data Owner recovery.
- Verification:
  - `pytest tests/orchestration/test_wms_inventory_ingestion.py tests/data/test_clickhouse_wms_schema.py tests/data/test_source_contract_freeze.py tests/backend/test_ingestion.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 24 passed, 1 warning about `.pytest_cache` permissions.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 497 passed, 1 warning about `.pytest_cache` permissions.

## RI-4 ERP Prices, Suppliers And Order Status

- RI-4 completed as ingestion foundation.
- Completion note: `docs/context/RI4_COMPLETION.md`.
- ERP commercial ingestion specification added: `ERP_COMMERCIAL_INGESTION_SPEC.md`.
- ERP supplier terms contract added:
  - `ErpSupplierTermLine`;
  - `erp_supplier_term_line`;
  - lead time, MOQ, pack size and order calendar fields.
- ERP manifest endpoint added:
  - `GET /data/ingestion/manifests/erp-supplier-terms`.
- Raw ClickHouse schema added:
  - `open_fnr.raw_erp_supplier_terms`.
- ERP Airflow DAG now includes:
  - price manifest;
  - supplier terms manifest;
  - order export status manifest;
  - reconciliation plan step.
- Verification:
  - `pytest tests/orchestration/test_erp_commercial_ingestion.py tests/data/test_clickhouse_erp_schema.py tests/data/test_contract_validation.py tests/data/test_source_contract_freeze.py tests/backend/test_ingestion.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 33 passed, 1 warning about `.pytest_cache` permissions.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 499 passed, 1 warning about `.pytest_cache` permissions.

## RI-5 MDM And Promo Ingestion

- RI-5 completed as ingestion foundation.
- Completion note: `docs/context/RI5_COMPLETION.md`.
- MDM/Promo ingestion specification added: `MDM_PROMO_INGESTION_SPEC.md`.
- MDM quality plan helper added:
  - `build_mdm_quality_plan()`;
  - hierarchy, lifecycle, fresh attributes, supplier reference, routing and replenishment calendar checks.
- Promo quality plan helper added:
  - `build_promo_quality_plan()`;
  - SKU/store scope, date range, overlap, price/discount, display location and display capacity checks.
- Verification:
  - `pytest tests/orchestration/test_mdm_reference_ingestion.py tests/orchestration/test_promo_plan_ingestion.py tests/data/test_clickhouse_mdm_schema.py tests/data/test_clickhouse_promo_schema.py tests/data/test_source_contract_freeze.py tests/backend/test_ingestion.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 27 passed, 1 warning about `.pytest_cache` permissions.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 501 passed, 1 warning about `.pytest_cache` permissions.

## RI-6 Reconciliation, Retries And Source SLA

- RI-6 completed as operations foundation.
- Completion note: `docs/context/RI6_COMPLETION.md`.
- Real integration operations specification added: `REAL_INTEGRATION_OPERATIONS_SPEC.md`.
- DWH sales history and ERP supplier terms are now included in shadow-load source manifests.
- Source-contract DQ plans now cover all 11 frozen contracts.
- Integration operations API added:
  - `GET /integration/operations/source-readiness`;
  - `GET /integration/operations/retry-plan`;
  - `GET /integration/operations/reconciliation`.
- Source readiness exposes:
  - owner role;
  - source SLA label;
  - blocker and warning counts;
  - retry flag;
  - recovery action;
  - idempotency key.
- Retry plan uses `same_idempotency_key_no_duplicate_clean_rows`.
- Reconciliation summary exposes:
  - reconciliation keys;
  - downstream blockers;
  - per-contract status.
- Tests added/updated:
  - `tests/backend/test_integration_operations.py`;
  - `tests/backend/test_data_quality.py`;
  - `tests/backend/test_dq_execution.py`;
  - `tests/backend/test_shadow_gate.py`.
  - `tests/backend/test_pilot_fixtures.py`.
- Verification:
  - `pytest tests/backend/test_integration_operations.py tests/backend/test_data_quality.py tests/backend/test_dq_execution.py tests/backend/test_shadow_gate.py tests/backend/test_daily_pipeline.py tests/backend/test_pilot_fixtures.py tests/backend/test_ingestion.py tests/data/test_source_contract_freeze.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 43 passed, 1 warning about `.pytest_cache` permissions.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 506 passed, 1 warning about `.pytest_cache` permissions.

## SEC-1 OIDC/JWT Authentication

- SEC-1 completed as authentication foundation.
- Completion note: `docs/context/SEC1_COMPLETION.md`.
- Production authentication specification added: `PRODUCTION_AUTHENTICATION_SPEC.md`.
- JWT validation hardened:
  - `exp` is mandatory;
  - expired tokens are rejected;
  - future `nbf` is rejected outside configured clock skew.
- Config added:
  - `OPEN_FNR_OIDC_CLOCK_SKEW_SECONDS`.
- DEV bypass boundary verified:
  - allowed only in DEV/TEST;
  - rejected in STAGE even if bypass flag is accidentally true.
- Tests added/updated:
  - `tests/backend/test_auth.py`;
  - `tests/backend/test_config.py`.
- Verification:
  - `pytest tests/backend/test_auth.py tests/backend/test_config.py tests/backend/test_security.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 35 passed, 1 warning about `.pytest_cache` permissions.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 509 passed, 1 warning about `.pytest_cache` permissions.

## SEC-2 RBAC And Object-Level Access

- SEC-2 completed as object-access foundation.
- Completion note: `docs/context/SEC2_COMPLETION.md`.
- Object-level access specification added: `OBJECT_LEVEL_ACCESS_SPEC.md`.
- Shared policy now supports supplier scope:
  - `Principal.suppliers`;
  - `has_object_scope(..., supplier_id=...)`;
  - `assert_object_scope(..., supplier_id=...)`.
- Security API added:
  - `GET /security/object-access-check`.
- Existing `GET /security/access-check` now supports optional `supplier_id`.
- Tests added/updated:
  - `tests/backend/test_policy.py`;
  - `tests/backend/test_security.py`.
- Verification:
  - `pytest tests/backend/test_policy.py tests/backend/test_security.py tests/backend/test_auth.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 34 passed, 1 warning about `.pytest_cache` permissions.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 512 passed, 1 warning about `.pytest_cache` permissions.

## SEC-3 Secrets And Service Accounts

- SEC-3 completed as secrets/service-account foundation.
- Completion note: `docs/context/SEC3_COMPLETION.md`.
- Secret management specification added: `SECRET_MANAGEMENT_SPEC.md`.
- `.gitignore` now blocks:
  - local env files;
  - secret/key artifacts;
  - `secrets/` directory.
- Quality gate added:
  - `tests/quality/test_no_committed_secrets.py`.
- Service accounts documented:
  - `svc-airflow-export`;
  - `svc-open-fnr-idp-provisioning`.
- Verification:
  - `pytest tests/quality/test_no_committed_secrets.py tests/backend/test_security.py tests/backend/test_policy.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 25 passed, 1 warning about `.pytest_cache` permissions.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 516 passed, 1 warning about `.pytest_cache` permissions.

## SEC-4 Security Audit And Access Review

- SEC-4 completed as access review foundation.
- Completion note: `docs/context/SEC4_COMPLETION.md`.
- Security access review specification added: `SECURITY_ACCESS_REVIEW_SPEC.md`.
- Access review BPMN added:
  - `processes/security/access_review_process.bpmn20.xml`.
- Security API added:
  - `GET /security/access-review/report`.
- Access review report includes:
  - user roles;
  - region/category/supplier scopes;
  - excessive access flag;
  - recommendation;
  - process key.
- Tests added/updated:
  - `tests/backend/test_security.py`;
  - `tests/backend/test_process_deployment.py`;
  - `tests/process/test_security_access_review_process.py`.
- Verification:
  - `pytest tests/backend/test_security.py tests/backend/test_policy.py tests/process/test_security_access_review_process.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py tests/quality/test_no_committed_secrets.py` -> 28 passed, 1 warning about `.pytest_cache` permissions.
  - `pytest tests/backend/test_process_deployment.py tests/backend/test_security.py tests/process/test_security_access_review_process.py` -> 29 passed, 1 warning about `.pytest_cache` permissions.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 519 passed, 1 warning about `.pytest_cache` permissions.

## UI-1 Routed Application Foundation

- UI-1 completed as routed application foundation.
- Completion note: `docs/context/UI1_COMPLETION.md`.
- Specification added: `UI_ROUTED_APPLICATION_FOUNDATION_SPEC.md`.
- Verified existing frontend capabilities:
  - hash routes for major workspaces;
  - active route state from browser hash;
  - centralized API/service config through `app_config.ts`;
  - contextual `HelpFootnote` support for UI controls.
- Tests added:
  - `tests/frontend/test_ui_routed_foundation.py`.
- Evidence report:
  - `docs/test-reports/sprint-ui-1-routed-foundation/index.html`.
- Verification:
  - `pytest tests/frontend/test_ui_routed_foundation.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 6 passed, 1 warning about `.pytest_cache` permissions.
  - `npm.cmd run build` in `apps/frontend` -> passed.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 522 passed, 1 warning about `.pytest_cache` permissions.

## UI-2 Forecast And Replenishment Workbenches

- UI-2 completed as forecast/replenishment workbench foundation.
- Completion note: `docs/context/UI2_COMPLETION.md`.
- Specification added: `UI_FORECAST_REPLENISHMENT_WORKBENCH_SPEC.md`.
- Verified existing frontend capabilities:
  - forecast review and promo uplift workbench sections;
  - inventory projection, order proposal and replenishment workbench sections;
  - manual adjustment and exception audit context;
  - accessible section labels for critical planner panels.
- Tests added:
  - `tests/frontend/test_ui_forecast_replenishment_workbenches.py`.
- Evidence report:
  - `docs/test-reports/sprint-ui-2-forecast-replenishment-workbenches/index.html`.
- Verification:
  - `pytest tests/frontend/test_ui_forecast_replenishment_workbenches.py tests/frontend/test_ui_routed_foundation.py tests/quality/test_text_encoding.py tests/quality/test_no_hardcoded_network_config.py` -> 11 passed, 1 warning about `.pytest_cache` permissions.
  - `npm.cmd run build` in `apps/frontend` -> passed.
  - `$env:PYTHONPATH='apps/backend;.'; pytest --basetemp tmp\pytest-basetemp` -> 527 passed, 1 warning about `.pytest_cache` permissions.
- Remaining focused sprint count after UI-2: 16 sprints (`UI-3..UI-5`, `ML-1..ML-5`, `DEP-1..DEP-4`, `PILOT-1..PILOT-5`).
