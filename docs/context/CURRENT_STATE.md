# OPEN FNR Current State

Last updated: 2026-05-28

## Active Work

Sprint 23 implementation is complete.

## Local Infrastructure

Docker Compose development infrastructure is defined in `infra/dev/compose.yaml`.

Known local URLs:

| Service | URL |
| --- | --- |
| Airflow | `http://127.0.0.1:18088` |
| Flowable | `http://127.0.0.1:18080` |
| ClickHouse HTTP | `http://127.0.0.1:18123` |
| OpenSearch | `http://127.0.0.1:19200` |
| OpenSearch Dashboards | `http://127.0.0.1:15601` |
| Superset | `http://127.0.0.1:18089` |

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
- Active matrix and feature store SQL structures in ClickHouse init script.
- Feature version metadata SQL structure in PostgreSQL init script.
- UI Feature Mart Status section.
- HTML test report with screenshot: `docs/test-reports/sprint-3-feature-mart/index.html`.

## Sprint 4 Artifacts

- Forecast API and metrics: `apps/backend/open_fnr_api/forecast.py`.
- Forecast tests: `tests/backend/test_forecast.py`.
- Regular forecast process artifacts: `processes/forecast`.
- Forecast version metadata SQL table in PostgreSQL init script.
- UI Regular Forecast Baseline section.
- HTML test report with screenshot: `docs/test-reports/sprint-4-regular-baseline/index.html`.

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
- Publication BPMN: `processes/publication/publication_process.bpmn20.xml`.
- Publication eligibility DMN: `processes/publication/publication_eligibility_decision.dmn.xml`.
- Export failure CMMN: `processes/publication/export_failure_case.cmmn.xml`.
- UI Publication Console section with package list, statuses, idempotency keys, retry action, error details and linked exceptions.
- HTML test report with screenshot: `docs/test-reports/sprint-16-publication-export-v1/index.html`.

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
- Security process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Access request BPMN: `processes/security/access_request_process.bpmn20.xml`.
- Role assignment DMN: `processes/security/role_assignment_decision.dmn.xml`.
- Security incident CMMN: `processes/security/security_incident_case.cmmn.xml`.
- UI Admin Console V1 section with roles, region/category scopes, access requests, audit viewer and denied-state explanation.
- HTML test report with screenshot: `docs/test-reports/sprint-22-security-rbac/index.html`.

## Sprint 23 Artifacts

- Stage rehearsal API: `apps/backend/open_fnr_api/stage.py`.
- Stage rehearsal tests: `tests/backend/test_stage.py`.
- Stage process definitions registered in `apps/backend/open_fnr_api/process_engine.py`.
- Stage daily cycle BPMN: `processes/stage/stage_daily_cycle_process.bpmn20.xml`.
- Stage go/no-go DMN: `processes/stage/stage_go_no_go_decision.dmn.xml`.
- Stage UAT CMMN: `processes/stage/stage_uat_case.cmmn.xml`.
- UI Stage Rehearsal section with full daily cycle, stage snapshot, UAT checklist and go/no-go readiness.
- HTML test report with screenshot: `docs/test-reports/sprint-23-stage-rehearsal/index.html`.

## Verification

- `python -m pytest` -> 188 passed.
- `npm.cmd install` in `apps/frontend` -> completed, 0 vulnerabilities.
- `npm.cmd run build` in `apps/frontend` -> completed.
- `powershell -ExecutionPolicy Bypass -File scripts/dev/health.ps1` -> all dev services OK.
- `docker compose --env-file infra/dev/.env.example -f infra/dev/compose.yaml ps` -> services up.

## Next Step

Commit Sprint 23 checkpoint to `romanrav1980/OPEN_FNR`, then start Sprint 24: Business Pilot Release.
