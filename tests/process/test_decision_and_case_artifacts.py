from pathlib import Path
from xml.etree import ElementTree


DMN_NS = {"dmn": "https://www.omg.org/spec/DMN/20191111/MODEL/"}
CMMN_NS = {"cmmn": "http://www.omg.org/spec/CMMN/20151109/MODEL"}


def test_data_load_severity_dmn_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/data-ingestion/data_load_severity_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "data_load_severity_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_data_load_incident_cmmn_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/data-ingestion/data_load_incident_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "data_load_incident_case"
    assert tree.find(".//cmmn:humanTask", CMMN_NS) is not None


def test_dq_decisions_are_parseable() -> None:
    for path, decision_id in (
        ("processes/data-quality/dq_severity_decision.dmn.xml", "dq_severity_decision"),
        ("processes/data-quality/publication_block_decision.dmn.xml", "publication_block_decision"),
    ):
        tree = ElementTree.parse(Path(path))
        decision = tree.find("dmn:decision", DMN_NS)

        assert decision is not None
        assert decision.attrib["id"] == decision_id
        assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_data_quality_incident_cmmn_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/data-quality/data_quality_incident_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "data_quality_incident_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Triage DQ incident" in human_task_names
    assert "Approve waiver" in human_task_names


def test_feature_mart_decision_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/feature-mart/active_matrix_inclusion_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "active_matrix_inclusion_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_feature_build_incident_cmmn_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/feature-mart/feature_build_incident_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "feature_build_incident_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Triage feature build failure" in human_task_names
    assert "Approve feature fallback" in human_task_names


def test_forecast_publish_decision_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/forecast/forecast_publish_eligibility_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "forecast_publish_eligibility_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_forecast_run_failure_cmmn_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/forecast/forecast_run_failure_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "forecast_run_failure_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Triage forecast failure" in human_task_names
    assert "Approve baseline publication" in human_task_names


def test_forecast_review_required_decision_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/forecast/forecast_review_required_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "forecast_review_required_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_forecast_anomaly_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/forecast/forecast_anomaly_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "forecast_anomaly_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Investigate forecast anomaly" in human_task_names
    assert "Accept forecast anomaly" in human_task_names


def test_model_approval_decision_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/ml/model_approval_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "model_approval_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_model_degradation_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/ml/model_degradation_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "model_degradation_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Investigate model degradation" in human_task_names
    assert "Activate baseline fallback" in human_task_names


def test_promo_decisions_are_parseable() -> None:
    for path, decision_id in (
        ("processes/promo/promo_completeness_decision.dmn.xml", "promo_completeness_decision"),
        ("processes/promo/promo_overlap_decision.dmn.xml", "promo_overlap_decision"),
    ):
        tree = ElementTree.parse(Path(path))
        decision = tree.find("dmn:decision", DMN_NS)

        assert decision is not None
        assert decision.attrib["id"] == decision_id
        assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_promo_data_issue_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/promo/promo_data_issue_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "promo_data_issue_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Fix required promo fields" in human_task_names
    assert "Resolve promo overlap" in human_task_names


def test_promo_forecast_quality_decision_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/promo/promo_forecast_quality_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "promo_forecast_quality_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_promo_forecast_anomaly_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/promo/promo_forecast_anomaly_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "promo_forecast_anomaly_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review reference promos" in human_task_names
    assert "Adjust uplift draft" in human_task_names


def test_process_engine_task_visibility_decision_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/process-engine/task_visibility_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "task_visibility_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_process_engine_exception_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/process-engine/process_exception_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "process_exception_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Triage process exception" in human_task_names
    assert "Repair process payload" in human_task_names
    assert "Approve manual transition" in human_task_names


def test_promo_approval_decisions_are_parseable() -> None:
    for path, decision_id in (
        ("processes/promo/promo_risk_classification.dmn.xml", "promo_risk_classification"),
        ("processes/promo/promo_approval_route.dmn.xml", "promo_approval_route"),
    ):
        tree = ElementTree.parse(Path(path))
        decision = tree.find("dmn:decision", DMN_NS)

        assert decision is not None
        assert decision.attrib["id"] == decision_id
        assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_promo_shortage_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/promo/promo_shortage_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "promo_shortage_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review shortage risk" in human_task_names
    assert "Adjust promo volume" in human_task_names
    assert "Approve supply mitigation" in human_task_names


def test_stock_projection_quality_decision_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/replenishment/stock_projection_quality_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "stock_projection_quality_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_stock_projection_issue_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/replenishment/stock_projection_issue_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "stock_projection_issue_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review stock-out risk" in human_task_names
    assert "Verify open orders and in-transit" in human_task_names
    assert "Approve projection fallback" in human_task_names


def test_order_proposal_decisions_are_parseable() -> None:
    for path, decision_id in (
        ("processes/replenishment/order_auto_approval_decision.dmn.xml", "order_auto_approval_decision"),
        ("processes/replenishment/order_constraint_decision.dmn.xml", "order_constraint_decision"),
    ):
        tree = ElementTree.parse(Path(path))
        decision = tree.find("dmn:decision", DMN_NS)

        assert decision is not None
        assert decision.attrib["id"] == decision_id
        assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_supplier_constraint_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/replenishment/supplier_constraint_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "supplier_constraint_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review supplier block" in human_task_names
    assert "Find alternative supplier" in human_task_names
    assert "Approve manual order release" in human_task_names


def test_manual_review_required_decision_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/replenishment/manual_review_required_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "manual_review_required_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_order_exception_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/replenishment/order_exception_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "order_exception_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review order exception" in human_task_names
    assert "Approve large adjustment" in human_task_names
    assert "Prepare async export" in human_task_names


def test_exception_center_decisions_are_parseable() -> None:
    for path, decision_id in (
        ("processes/exceptions/exception_severity_decision.dmn.xml", "exception_severity_decision"),
        ("processes/exceptions/exception_owner_routing.dmn.xml", "exception_owner_routing"),
    ):
        tree = ElementTree.parse(Path(path))
        decision = tree.find("dmn:decision", DMN_NS)

        assert decision is not None
        assert decision.attrib["id"] == decision_id
        assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_generic_exception_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/exceptions/generic_exception_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "generic_exception_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Take exception" in human_task_names
    assert "Investigate exception" in human_task_names
    assert "Resolve exception" in human_task_names
    assert "Ignore exception" in human_task_names
    assert "Escalate exception" in human_task_names


def test_adjustment_approval_required_decision_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/adjustments/adjustment_approval_required_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "adjustment_approval_required_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_adjustment_dispute_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/adjustments/adjustment_dispute_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "adjustment_dispute_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review adjustment reason" in human_task_names
    assert "Compare original and adjusted values" in human_task_names
    assert "Approve or cancel adjustment" in human_task_names


def test_publication_eligibility_decision_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/publication/publication_eligibility_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "publication_eligibility_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_export_failure_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/publication/export_failure_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "export_failure_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review export error" in human_task_names
    assert "Retry export" in human_task_names
    assert "Create export failure exception" in human_task_names


def test_kpi_alert_decision_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/kpi/kpi_alert_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "kpi_alert_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_kpi_degradation_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/kpi/kpi_degradation_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "kpi_degradation_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review accuracy drop" in human_task_names
    assert "Assign corrective action" in human_task_names
    assert "Confirm business impact" in human_task_names


def test_fresh_spoilage_risk_decision_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/fresh/fresh_spoilage_risk_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "fresh_spoilage_risk_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_high_spoilage_risk_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/fresh/high_spoilage_risk_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "high_spoilage_risk_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review shelf-life batches" in human_task_names
    assert "Adjust fresh order quantity" in human_task_names
    assert "Approve waste-service tradeoff" in human_task_names


def test_lifecycle_order_allowed_decision_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/lifecycle/lifecycle_order_allowed_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "lifecycle_order_allowed_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_clearance_risk_case_is_parseable() -> None:
    tree = ElementTree.parse(Path("processes/lifecycle/clearance_risk_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "clearance_risk_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review remaining stock" in human_task_names
    assert "Approve clearance markdown" in human_task_names
    assert "Confirm order block" in human_task_names


def test_dc_allocation_priority_decision_is_parseable_and_has_explainable_outputs() -> None:
    tree = ElementTree.parse(Path("processes/multi-echelon/dc_allocation_priority_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "dc_allocation_priority_decision"
    table = tree.find(".//dmn:decisionTable", DMN_NS)
    assert table is not None
    outputs = {
        output.attrib["name"]
        for output in tree.findall(".//dmn:output", DMN_NS)
    }
    rule_ids = {
        rule.attrib["id"]
        for rule in tree.findall(".//dmn:rule", DMN_NS)
    }
    assert outputs == {"allocation_priority", "rule"}
    assert {"rule_high_priority_risk", "rule_medium_risk", "rule_low"}.issubset(rule_ids)


def test_dc_shortage_case_has_required_human_tasks_for_case_lifecycle() -> None:
    tree = ElementTree.parse(Path("processes/multi-echelon/dc_shortage_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "dc_shortage_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review DC shortage" in human_task_names
    assert "Approve allocation rule" in human_task_names
    assert "Notify affected stores" in human_task_names
    assert "Confirm store order cutoff" in human_task_names


def test_performance_gate_decision_is_parseable_and_has_pass_fail_waiver_outputs() -> None:
    tree = ElementTree.parse(Path("processes/performance/performance_gate_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "performance_gate_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None
    outputs = {
        output.attrib["name"]
        for output in tree.findall(".//dmn:output", DMN_NS)
    }
    rule_ids = {
        rule.attrib["id"]
        for rule in tree.findall(".//dmn:rule", DMN_NS)
    }
    assert outputs == {"gate_decision", "next_action"}
    assert {"rule_fail_batch", "rule_waiver_latency", "rule_pass"}.issubset(rule_ids)


def test_performance_regression_case_has_required_lifecycle_tasks() -> None:
    tree = ElementTree.parse(Path("processes/performance/performance_regression_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "performance_regression_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Triage failed metric" in human_task_names
    assert "Assign bottleneck owner" in human_task_names
    assert "Approve performance waiver" in human_task_names
    assert "Confirm gate decision" in human_task_names


def test_role_assignment_decision_is_parseable_and_routes_by_risk() -> None:
    tree = ElementTree.parse(Path("processes/security/role_assignment_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "role_assignment_decision"
    assert tree.find(".//dmn:decisionTable", DMN_NS) is not None
    outputs = {
        output.attrib["name"]
        for output in tree.findall(".//dmn:output", DMN_NS)
    }
    rule_ids = {
        rule.attrib["id"]
        for rule in tree.findall(".//dmn:rule", DMN_NS)
    }
    assert outputs == {"required_approver", "risk"}
    assert {"rule_admin_high_risk", "rule_business_role_region_scope", "rule_viewer_low_risk"}.issubset(rule_ids)


def test_security_incident_case_has_required_lifecycle_tasks() -> None:
    tree = ElementTree.parse(Path("processes/security/security_incident_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "security_incident_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Triage access incident" in human_task_names
    assert "Review audit trail" in human_task_names
    assert "Revoke suspicious access" in human_task_names
    assert "Confirm incident closure" in human_task_names


def test_stage_go_no_go_decision_is_parseable_and_has_ready_and_no_go_rules() -> None:
    tree = ElementTree.parse(Path("processes/stage/stage_go_no_go_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "stage_go_no_go_decision"
    outputs = {
        output.attrib["name"]
        for output in tree.findall(".//dmn:output", DMN_NS)
    }
    rule_ids = {
        rule.attrib["id"]
        for rule in tree.findall(".//dmn:rule", DMN_NS)
    }
    assert outputs == {"decision", "next_action"}
    assert {"rule_no_go_critical", "rule_no_go_failed_step", "rule_go_ready"}.issubset(rule_ids)


def test_stage_uat_case_has_required_business_uat_tasks() -> None:
    tree = ElementTree.parse(Path("processes/stage/stage_uat_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "stage_uat_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Accept stage snapshot" in human_task_names
    assert "Execute forecast UAT" in human_task_names
    assert "Execute replenishment UAT" in human_task_names
    assert "Validate export UAT" in human_task_names
    assert "Confirm pilot go/no-go" in human_task_names


def test_pilot_acceptance_decision_is_parseable_and_has_block_ready_continue_rules() -> None:
    tree = ElementTree.parse(Path("processes/pilot/pilot_acceptance_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "pilot_acceptance_decision"
    outputs = {
        output.attrib["name"]
        for output in tree.findall(".//dmn:output", DMN_NS)
    }
    rule_ids = {
        rule.attrib["id"]
        for rule in tree.findall(".//dmn:rule", DMN_NS)
    }
    assert outputs == {"decision", "action"}
    assert {"rule_block_critical_issue", "rule_ready", "rule_continue_pilot"}.issubset(rule_ids)


def test_pilot_exception_case_has_feedback_defect_and_acceptance_tasks() -> None:
    tree = ElementTree.parse(Path("processes/pilot/pilot_exception_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "pilot_exception_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Triage pilot feedback" in human_task_names
    assert "Assign defect owner" in human_task_names
    assert "Accept or resolve risk" in human_task_names
    assert "Confirm pilot acceptance" in human_task_names


def test_industrial_dq_gate_decision_is_parseable_and_has_pass_warning_block_rules() -> None:
    tree = ElementTree.parse(Path("processes/data-scale/industrial_dq_gate_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "industrial_dq_gate_decision"
    outputs = {
        output.attrib["name"]
        for output in tree.findall(".//dmn:output", DMN_NS)
    }
    rule_ids = {
        rule.attrib["id"]
        for rule in tree.findall(".//dmn:rule", DMN_NS)
    }
    assert outputs == {"decision", "action"}
    assert {"rule_block_failed", "rule_warning_late", "rule_pass"}.issubset(rule_ids)


def test_large_scale_data_incident_case_has_partition_lineage_and_cutoff_tasks() -> None:
    tree = ElementTree.parse(Path("processes/data-scale/large_scale_data_incident_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "large_scale_data_incident_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Triage failed partition" in human_task_names
    assert "Review lineage gap" in human_task_names
    assert "Approve reprocessing" in human_task_names
    assert "Confirm cutoff recovery" in human_task_names


def test_model_release_gate_decision_is_parseable_and_has_approve_block_rollback_rules() -> None:
    tree = ElementTree.parse(Path("processes/ml-governance/model_release_gate_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "model_release_gate_decision"
    outputs = {
        output.attrib["name"]
        for output in tree.findall(".//dmn:output", DMN_NS)
    }
    rule_ids = {
        rule.attrib["id"]
        for rule in tree.findall(".//dmn:rule", DMN_NS)
    }
    assert outputs == {"decision", "action"}
    assert {"rule_block_high_drift", "rule_approve_candidate", "rule_rollback"}.issubset(rule_ids)


def test_model_drift_case_has_drift_shadow_rollback_and_retraining_tasks() -> None:
    tree = ElementTree.parse(Path("processes/ml-governance/model_drift_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "model_drift_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Triage drift alert" in human_task_names
    assert "Review shadow comparison" in human_task_names
    assert "Approve model rollback" in human_task_names
    assert "Confirm retraining plan" in human_task_names


def test_bulk_auto_approval_decision_is_parseable_and_has_manual_and_auto_rules() -> None:
    tree = ElementTree.parse(Path("processes/replenishment-scale/bulk_auto_approval_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "bulk_auto_approval_decision"
    outputs = {
        output.attrib["name"]
        for output in tree.findall(".//dmn:output", DMN_NS)
    }
    rule_ids = {
        rule.attrib["id"]
        for rule in tree.findall(".//dmn:rule", DMN_NS)
    }
    assert outputs == {"decision", "action"}
    assert {"rule_block_partition", "rule_block_runtime", "rule_auto_approve"}.issubset(rule_ids)


def test_replenishment_scale_exception_case_has_bulk_constraint_rerun_and_export_tasks() -> None:
    tree = ElementTree.parse(Path("processes/replenishment-scale/replenishment_scale_exception_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "replenishment_scale_exception_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Triage bulk approval block" in human_task_names
    assert "Review constraint performance" in human_task_names
    assert "Approve partition rerun" in human_task_names
    assert "Confirm async export recovery" in human_task_names


def test_process_change_risk_decision_is_parseable_and_routes_by_tests_instances_and_kind() -> None:
    tree = ElementTree.parse(Path("processes/process-governance/process_change_risk_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "process_change_risk_decision"
    outputs = {
        output.attrib["name"]
        for output in tree.findall(".//dmn:output", DMN_NS)
    }
    rule_ids = {
        rule.attrib["id"]
        for rule in tree.findall(".//dmn:rule", DMN_NS)
    }
    assert outputs == {"risk", "required_approver"}
    assert {"rule_high_failed_tests", "rule_medium_live_instances", "rule_low_no_instances"}.issubset(rule_ids)


def test_process_incident_case_has_deployment_migration_rollback_and_recovery_tasks() -> None:
    tree = ElementTree.parse(Path("processes/process-governance/process_incident_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "process_incident_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Triage process deployment incident" in human_task_names
    assert "Review instance migration" in human_task_names
    assert "Approve process rollback" in human_task_names
    assert "Confirm process recovery" in human_task_names


def test_incident_severity_decision_is_parseable_and_maps_severity_sla() -> None:
    tree = ElementTree.parse(Path("processes/observability/incident_severity_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "incident_severity_decision"
    outputs = {
        output.attrib["name"]
        for output in tree.findall(".//dmn:output", DMN_NS)
    }
    rule_ids = {
        rule.attrib["id"]
        for rule in tree.findall(".//dmn:rule", DMN_NS)
    }
    assert outputs == {"severity", "sla_minutes"}
    assert {"rule_sev1_critical", "rule_sev2_export", "rule_sev3_default"}.issubset(rule_ids)


def test_production_incident_case_has_triage_runbook_escalation_and_recovery_tasks() -> None:
    tree = ElementTree.parse(Path("processes/observability/production_incident_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "production_incident_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Triage alert" in human_task_names
    assert "Execute runbook" in human_task_names
    assert "Escalate to L3" in human_task_names
    assert "Confirm service recovery" in human_task_names


def test_release_readiness_decision_is_parseable_and_has_go_conditional_no_go_rules() -> None:
    tree = ElementTree.parse(Path("processes/release-gate/release_readiness_decision.dmn.xml"))
    decision = tree.find("dmn:decision", DMN_NS)

    assert decision is not None
    assert decision.attrib["id"] == "release_readiness_decision"
    outputs = {
        output.attrib["name"]
        for output in tree.findall(".//dmn:output", DMN_NS)
    }
    rule_ids = {
        rule.attrib["id"]
        for rule in tree.findall(".//dmn:rule", DMN_NS)
    }
    assert outputs == {"decision", "action"}
    assert {"rule_no_go_defects", "rule_conditional_go", "rule_go"}.issubset(rule_ids)


def test_release_risk_case_has_risk_acceptance_handover_and_signoff_tasks() -> None:
    tree = ElementTree.parse(Path("processes/release-gate/release_risk_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "release_risk_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review release risk" in human_task_names
    assert "Accept known risk" in human_task_names
    assert "Confirm support handover risk" in human_task_names
    assert "Sign go/no-go" in human_task_names


def test_supplier_selection_and_share_decisions_are_parseable() -> None:
    for path, decision_id, outputs in (
        ("processes/procurement/supplier_selection_decision.dmn.xml", "supplier_selection_decision", {"decision", "reason"}),
        ("processes/procurement/supplier_share_exception_decision.dmn.xml", "supplier_share_exception_decision", {"exception", "action"}),
    ):
        tree = ElementTree.parse(Path(path))
        decision = tree.find("dmn:decision", DMN_NS)
        assert decision is not None
        assert decision.attrib["id"] == decision_id
        actual_outputs = {
            output.attrib["name"]
            for output in tree.findall(".//dmn:output", DMN_NS)
        }
        assert actual_outputs == outputs


def test_supplier_constraint_case_has_terms_override_export_tasks() -> None:
    tree = ElementTree.parse(Path("processes/procurement/supplier_constraint_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "supplier_constraint_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review target share warning" in human_task_names
    assert "Compare supplier terms" in human_task_names
    assert "Approve supplier override" in human_task_names
    assert "Confirm supplier order export" in human_task_names


def test_display_capacity_and_direct_to_shelf_decisions_are_parseable() -> None:
    for path, decision_id in (
        ("processes/shelf-space/display_capacity_decision.dmn.xml", "display_capacity_decision"),
        ("processes/shelf-space/direct_to_shelf_decision.dmn.xml", "direct_to_shelf_decision"),
    ):
        tree = ElementTree.parse(Path(path))
        decision = tree.find("dmn:decision", DMN_NS)
        assert decision is not None
        assert decision.attrib["id"] == decision_id
        assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_shelf_capacity_exception_case_has_display_location_direct_shelf_and_audit_tasks() -> None:
    tree = ElementTree.parse(Path("processes/shelf-space/shelf_capacity_exception_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "shelf_capacity_exception_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review display over capacity" in human_task_names
    assert "Adjust display location" in human_task_names
    assert "Approve direct-to-shelf" in human_task_names
    assert "Confirm shelf audit" in human_task_names


def test_capacity_overload_and_order_shift_decisions_are_parseable() -> None:
    for path, decision_id in (
        ("processes/capacity/capacity_overload_decision.dmn.xml", "capacity_overload_decision"),
        ("processes/capacity/order_shift_priority_decision.dmn.xml", "order_shift_priority_decision"),
    ):
        tree = ElementTree.parse(Path(path))
        decision = tree.find("dmn:decision", DMN_NS)

        assert decision is not None
        assert decision.attrib["id"] == decision_id
        assert tree.find(".//dmn:decisionTable", DMN_NS) is not None


def test_capacity_overload_case_has_calendar_preview_approval_and_export_tasks() -> None:
    tree = ElementTree.parse(Path("processes/capacity/capacity_overload_case.cmmn.xml"))
    case = tree.find("cmmn:case", CMMN_NS)

    assert case is not None
    assert case.attrib["id"] == "capacity_overload_case"
    human_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//cmmn:humanTask", CMMN_NS)
    }
    assert "Review overload calendar" in human_task_names
    assert "Review smoothing preview" in human_task_names
    assert "Approve order moves" in human_task_names
    assert "Confirm TMS export" in human_task_names
