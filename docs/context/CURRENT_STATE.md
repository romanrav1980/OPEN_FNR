# OPEN FNR Current State

Last updated: 2026-05-29

## Active Work

Industrial hardening continues after real-ingestion I1-I5. The current focus is connecting validated clean source publications to feature mart build planning, ML/replenishment inputs and pilot-readiness rehearsal.

Current backend regression status: 394 automated tests passed.

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
- Security process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Access request BPMN: `processes/security/access_request_process.bpmn20.xml`.
- Role assignment DMN: `processes/security/role_assignment_decision.dmn.xml`.
- Security incident CMMN: `processes/security/security_incident_case.cmmn.xml`.
- UI Admin Console V1 section with live Security API status, roles, region/category scopes, access requests, IdP target provisioning, audit viewer and denied-state explanation.
- HTML test report with screenshot: `docs/test-reports/sprint-22-security-rbac/index.html`.
- IdP provisioning target hardening report: `docs/test-reports/sprint-idp-provisioning-target/index.html`.

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
- Pilot process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Pilot operational BPMN: `processes/pilot/pilot_operational_process.bpmn20.xml`.
- Pilot acceptance DMN: `processes/pilot/pilot_acceptance_decision.dmn.xml`.
- Pilot exception CMMN: `processes/pilot/pilot_exception_case.cmmn.xml`.
- UI Business Pilot Dashboard section with pilot scope, KPI panel, feedback, known issues and acceptance action.
- HTML test report with screenshot: `docs/test-reports/sprint-24-business-pilot/index.html`.

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

- `python -m pytest` -> 394 passed.
- `npm.cmd install` in `apps/frontend` -> completed, 0 vulnerabilities.
- `npm.cmd run build` in `apps/frontend` -> completed.
- `docker compose --env-file infra/test/.env.example -f infra/dev/compose.yaml config --quiet` -> TEST compose config valid.
- `docker compose --env-file infra/stage/.env.example -f infra/dev/compose.yaml config --quiet` -> STAGE compose config valid.
- `docker compose --env-file infra/dev/.env.example -f infra/dev/compose.yaml config --quiet` -> DEV compose config valid.
- `powershell -ExecutionPolicy Bypass -File scripts/dev/health.ps1` -> all dev services OK.
- `docker compose --env-file infra/dev/.env.example -f infra/dev/compose.yaml ps` -> services up.

## Next Step

Real-ingestion I1-I5 is implemented and verified. Next: connect real source adapters or file drops for pilot shadow load, then harden clean canonical tables and Process Engine DQ tasks.

## Post-Sprint Planning Artifacts

- Documentation audit and synchronization: `DOCUMENTATION_AUDIT_AND_SYNC.md`.
- Next delivery plan: `NEXT_DELIVERY_PLAN.md`.
- Industrial hardening sprint plan: `INDUSTRIAL_HARDENING_SPRINTS.md`.
- Deployment environments strategy: `DEPLOYMENT_ENVIRONMENTS_STRATEGY.md`.
- Real data ingestion pipelines: `REAL_DATA_INGESTION_PIPELINES.md`.
- Production security hardening: `PRODUCTION_SECURITY_HARDENING_PLAN.md`.
- UI productization: `UI_PRODUCTIZATION_PLAN.md`.
- Pilot launch: `PILOT_LAUNCH_PLAN.md`.

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
