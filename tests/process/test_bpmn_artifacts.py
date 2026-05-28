from pathlib import Path
from xml.etree import ElementTree


BPMN_NS = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
PROCESS_PATH = Path("processes/dev-healthcheck/dev_healthcheck_process.bpmn20.xml")
DATA_LOAD_PROCESS_PATH = Path("processes/data-ingestion/data_load_monitoring_process.bpmn20.xml")
DQ_PROCESS_PATH = Path("processes/data-quality/dq_check_process.bpmn20.xml")
FEATURE_PROCESS_PATH = Path("processes/feature-mart/feature_build_process.bpmn20.xml")
FORECAST_PROCESS_PATH = Path("processes/forecast/regular_forecast_run_process.bpmn20.xml")
FORECAST_REVIEW_PROCESS_PATH = Path("processes/forecast/forecast_review_process.bpmn20.xml")
MODEL_REVIEW_PROCESS_PATH = Path("processes/ml/model_candidate_review_process.bpmn20.xml")
PROMO_VALIDATION_PROCESS_PATH = Path("processes/promo/promo_draft_validation_process.bpmn20.xml")
PROMO_FORECAST_PROCESS_PATH = Path("processes/promo/promo_forecast_process.bpmn20.xml")
PROMO_PLANNING_PROCESS_PATH = Path("processes/promo/promo_planning_process.bpmn20.xml")
REPLENISHMENT_APPROVAL_PROCESS_PATH = Path("processes/process-engine/replenishment_approval_process.bpmn20.xml")
REPLENISHMENT_CALCULATION_PROCESS_PATH = Path("processes/replenishment/replenishment_calculation_process.bpmn20.xml")
ORDER_PROPOSAL_PROCESS_PATH = Path("processes/replenishment/order_proposal_generation_process.bpmn20.xml")
EXCEPTION_ESCALATION_PROCESS_PATH = Path("processes/exceptions/exception_escalation_process.bpmn20.xml")
MANUAL_ADJUSTMENT_PROCESS_PATH = Path("processes/adjustments/manual_adjustment_process.bpmn20.xml")
PUBLICATION_PROCESS_PATH = Path("processes/publication/publication_process.bpmn20.xml")
KPI_REVIEW_PROCESS_PATH = Path("processes/kpi/weekly_kpi_review_process.bpmn20.xml")
FRESH_ORDER_REVIEW_PROCESS_PATH = Path("processes/fresh/fresh_order_review_process.bpmn20.xml")
SKU_PHASE_IN_PROCESS_PATH = Path("processes/lifecycle/sku_phase_in_process.bpmn20.xml")
SKU_PHASE_OUT_PROCESS_PATH = Path("processes/lifecycle/sku_phase_out_process.bpmn20.xml")
DC_REPLENISHMENT_PROCESS_PATH = Path("processes/multi-echelon/dc_replenishment_process.bpmn20.xml")
PERFORMANCE_TEST_RUN_PROCESS_PATH = Path("processes/performance/performance_test_run_process.bpmn20.xml")
ACCESS_REQUEST_PROCESS_PATH = Path("processes/security/access_request_process.bpmn20.xml")
STAGE_DAILY_CYCLE_PROCESS_PATH = Path("processes/stage/stage_daily_cycle_process.bpmn20.xml")
PILOT_OPERATIONAL_PROCESS_PATH = Path("processes/pilot/pilot_operational_process.bpmn20.xml")
INDUSTRIAL_DATA_LOAD_PROCESS_PATH = Path("processes/data-scale/industrial_data_load_process.bpmn20.xml")
MODEL_RELEASE_PROCESS_PATH = Path("processes/ml-governance/model_release_process.bpmn20.xml")
INDUSTRIAL_REPLENISHMENT_PROCESS_PATH = Path("processes/replenishment-scale/industrial_replenishment_process.bpmn20.xml")
PROCESS_CHANGE_MANAGEMENT_PROCESS_PATH = Path("processes/process-governance/process_change_management_process.bpmn20.xml")
INCIDENT_MANAGEMENT_PROCESS_PATH = Path("processes/observability/incident_management_process.bpmn20.xml")
RELEASE_GO_NO_GO_PROCESS_PATH = Path("processes/release-gate/release_go_no_go_process.bpmn20.xml")
PURCHASE_PROPOSAL_PROCESS_PATH = Path("processes/procurement/purchase_proposal_process.bpmn20.xml")
SHELF_SPACE_REVIEW_PROCESS_PATH = Path("processes/shelf-space/shelf_space_review_process.bpmn20.xml")
CAPACITY_SMOOTHING_PROCESS_PATH = Path("processes/capacity/capacity_smoothing_process.bpmn20.xml")
DIAGNOSTIC_INSIGHT_REVIEW_PROCESS_PATH = Path("processes/diagnostics/diagnostic_insight_review_process.bpmn20.xml")


def test_dev_healthcheck_bpmn_is_parseable() -> None:
    tree = ElementTree.parse(PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "dev_healthcheck_process"
    assert process.attrib["isExecutable"] == "true"


def test_dev_healthcheck_bpmn_has_minimal_lifecycle() -> None:
    tree = ElementTree.parse(PROCESS_PATH)
    root = tree.getroot()

    assert root.find(".//bpmn:startEvent", BPMN_NS) is not None
    assert root.find(".//bpmn:userTask", BPMN_NS) is not None
    assert root.find(".//bpmn:endEvent", BPMN_NS) is not None


def test_data_load_monitoring_bpmn_has_incident_path() -> None:
    tree = ElementTree.parse(DATA_LOAD_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "data_load_monitoring_process"
    assert tree.find(".//bpmn:exclusiveGateway", BPMN_NS) is not None
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    assert "Accept loaded batch" in user_task_names
    assert "Create data load incident" in user_task_names


def test_dq_check_bpmn_has_recheck_path() -> None:
    tree = ElementTree.parse(DQ_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "dq_check_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    assert "Run DQ rules" in service_task_names
    assert "Re-run DQ rules" in service_task_names


def test_feature_build_bpmn_publishes_validated_version() -> None:
    tree = ElementTree.parse(FEATURE_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "feature_build_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    assert "Build active matrix" in service_task_names
    assert "Publish feature version" in service_task_names


def test_regular_forecast_bpmn_scores_and_publishes() -> None:
    tree = ElementTree.parse(FORECAST_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "regular_forecast_run_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    assert "Score regular baseline" in service_task_names
    assert "Publish forecast version" in service_task_names


def test_forecast_review_bpmn_has_anomaly_review_task() -> None:
    tree = ElementTree.parse(FORECAST_REVIEW_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "forecast_review_process"
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    assert "Review forecast anomaly" in user_task_names
    assert "Accept forecast slice" in user_task_names


def test_model_candidate_review_bpmn_has_approval_and_promotion() -> None:
    tree = ElementTree.parse(MODEL_REVIEW_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "model_candidate_review_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    assert "Run model backtesting" in service_task_names
    assert "Promote model candidate" in service_task_names
    assert "Approve model candidate" in user_task_names


def test_promo_validation_bpmn_checks_completeness_and_overlap() -> None:
    tree = ElementTree.parse(PROMO_VALIDATION_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "promo_draft_validation_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    assert "Validate promo completeness" in service_task_names
    assert "Detect promo overlap" in service_task_names
    assert "Resolve promo data issue" in user_task_names


def test_promo_forecast_bpmn_calculates_uplift_and_total() -> None:
    tree = ElementTree.parse(PROMO_FORECAST_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "promo_forecast_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    assert "Load regular baseline for promo period" in service_task_names
    assert "Calculate promo uplift" in service_task_names
    assert "Calculate total forecast" in service_task_names


def test_replenishment_approval_bpmn_has_manual_and_publish_steps() -> None:
    tree = ElementTree.parse(REPLENISHMENT_APPROVAL_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "replenishment_approval_process"
    assert tree.find(".//bpmn:exclusiveGateway", BPMN_NS) is not None
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    assert "Load order proposal" in service_task_names
    assert "Publish approved order proposal" in service_task_names
    assert "Approve replenishment exception" in user_task_names


def test_promo_planning_bpmn_has_approval_rework_and_reject_paths() -> None:
    tree = ElementTree.parse(PROMO_PLANNING_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "promo_planning_process"
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    assert "Classify promo risk" in business_rule_names
    assert "Select approval route" in business_rule_names
    assert "Category Manager approval" in user_task_names
    assert "Supply Chain approval" in user_task_names
    assert "Request promo rework" in user_task_names
    assert "Reject promo" in service_task_names
    assert "Mark promo publication ready" in service_task_names


def test_replenishment_calculation_bpmn_projects_stock_and_handles_warning() -> None:
    tree = ElementTree.parse(REPLENISHMENT_CALCULATION_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "replenishment_calculation_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    assert "Load current stock snapshot" in service_task_names
    assert "Load open orders and in-transit" in service_task_names
    assert "Load demand projection" in service_task_names
    assert "Calculate projected stock" in service_task_names
    assert "Publish inventory projection" in service_task_names
    assert "Evaluate projection quality" in business_rule_names
    assert "Review stock projection issue" in user_task_names


def test_order_proposal_bpmn_generates_explainable_proposals() -> None:
    tree = ElementTree.parse(ORDER_PROPOSAL_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "order_proposal_generation_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    assert "Calculate gross requirement" in service_task_names
    assert "Calculate net requirement" in service_task_names
    assert "Apply MOQ and rounding" in service_task_names
    assert "Evaluate order constraints" in business_rule_names
    assert "Evaluate auto approval" in business_rule_names
    assert "Review order proposal" in user_task_names
    assert "Open supplier constraint case" in user_task_names


def test_exception_escalation_bpmn_routes_and_closes_exceptions() -> None:
    tree = ElementTree.parse(EXCEPTION_ESCALATION_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "exception_escalation_process"
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    assert "Decide exception severity" in business_rule_names
    assert "Route exception owner" in business_rule_names
    assert "Review exception" in user_task_names
    assert "Escalate exception" in user_task_names
    assert "Resolve exception" in service_task_names
    assert "Ignore exception" in service_task_names


def test_manual_adjustment_bpmn_previews_approves_and_applies_overlay() -> None:
    tree = ElementTree.parse(MANUAL_ADJUSTMENT_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "manual_adjustment_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    assert "Validate adjustment scope" in service_task_names
    assert "Preview adjustment impact" in service_task_names
    assert "Apply adjustment overlay" in service_task_names
    assert "Decide approval required" in business_rule_names
    assert "Approve adjustment" in user_task_names


def test_publication_bpmn_handles_accept_reject_fail_paths() -> None:
    tree = ElementTree.parse(PUBLICATION_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "publication_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    assert "Prepare publication package" in service_task_names
    assert "Send export to target" in service_task_names
    assert "Handle target response" in service_task_names
    assert "Store accepted status" in service_task_names
    assert "Reject publication package" in service_task_names
    assert "Check publication eligibility" in business_rule_names
    assert "Open export failure case" in user_task_names


def test_weekly_kpi_review_bpmn_creates_action_on_threshold_breach() -> None:
    tree = ElementTree.parse(KPI_REVIEW_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "weekly_kpi_review_process"
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    assert "Evaluate KPI alert" in business_rule_names
    assert "Review KPI degradation" in user_task_names
    assert "Create KPI action" in service_task_names


def test_fresh_order_review_bpmn_handles_spoilage_risk() -> None:
    tree = ElementTree.parse(FRESH_ORDER_REVIEW_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "fresh_order_review_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    assert "Load FEFO batches" in service_task_names
    assert "Estimate expected waste" in service_task_names
    assert "Adjust fresh order" in service_task_names
    assert "Approve fresh order" in service_task_names
    assert "Decide spoilage risk" in business_rule_names
    assert "Review fresh spoilage risk" in user_task_names


def test_sku_phase_in_bpmn_selects_reference_and_activates_sku() -> None:
    tree = ElementTree.parse(SKU_PHASE_IN_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "sku_phase_in_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    end_event_names = {
        event.attrib["name"]
        for event in tree.findall(".//bpmn:endEvent", BPMN_NS)
    }
    assert "Select reference product" in user_task_names
    assert "Approve phase-in" in user_task_names
    assert "Calculate cold-start forecast" in service_task_names
    assert "Update active matrix" in service_task_names
    assert "Activate SKU" in service_task_names
    assert "SKU active" in end_event_names


def test_sku_phase_out_bpmn_links_replacement_blocks_orders_and_terminates() -> None:
    tree = ElementTree.parse(SKU_PHASE_OUT_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "sku_phase_out_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    assert "Link replacement SKU" in user_task_names
    assert "Approve phase-out" in user_task_names
    assert "Evaluate clearance risk" in business_rule_names
    assert "Block orders after termination" in service_task_names
    assert "Terminate SKU" in service_task_names


def test_dc_replenishment_bpmn_covers_shortage_allocation_and_approval_paths() -> None:
    tree = ElementTree.parse(DC_REPLENISHMENT_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "dc_replenishment_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    gateway_names = {
        gateway.attrib["name"]
        for gateway in tree.findall(".//bpmn:exclusiveGateway", BPMN_NS)
    }
    end_event_names = {
        event.attrib["name"]
        for event in tree.findall(".//bpmn:endEvent", BPMN_NS)
    }
    sequence_targets = {
        flow.attrib["targetRef"]
        for flow in tree.findall(".//bpmn:sequenceFlow", BPMN_NS)
    }
    assert "Aggregate store demand" in service_task_names
    assert "Load DC stock and inbound" in service_task_names
    assert "Calculate DC shortage" in service_task_names
    assert "Publish allocation preview" in service_task_names
    assert "Approve DC replenishment" in service_task_names
    assert "Prioritize DC allocation" in business_rule_names
    assert "Review DC shortage allocation" in user_task_names
    assert "DC shortage detected?" in gateway_names
    assert "DC allocation approved" in end_event_names
    assert "review_dc_shortage_allocation" in sequence_targets
    assert "approve_dc_replenishment" in sequence_targets


def test_performance_test_run_bpmn_covers_gate_failure_waiver_and_report_paths() -> None:
    tree = ElementTree.parse(PERFORMANCE_TEST_RUN_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "performance_test_run_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    gateway_names = {
        gateway.attrib["name"]
        for gateway in tree.findall(".//bpmn:exclusiveGateway", BPMN_NS)
    }
    end_event_names = {
        event.attrib["name"]
        for event in tree.findall(".//bpmn:endEvent", BPMN_NS)
    }
    assert "Generate synthetic load" in service_task_names
    assert "Run batch benchmark" in service_task_names
    assert "Run API latency benchmark" in service_task_names
    assert "Run UI performance benchmark" in service_task_names
    assert "Publish performance report" in service_task_names
    assert "Evaluate performance gate" in business_rule_names
    assert "Review performance regression" in user_task_names
    assert "Approve or reject waiver" in user_task_names
    assert "Performance gate passed?" in gateway_names
    assert "Performance gate recorded" in end_event_names


def test_access_request_bpmn_covers_approve_reject_provision_and_audit_paths() -> None:
    tree = ElementTree.parse(ACCESS_REQUEST_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "access_request_process"
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    gateway_names = {
        gateway.attrib["name"]
        for gateway in tree.findall(".//bpmn:exclusiveGateway", BPMN_NS)
    }
    end_event_names = {
        event.attrib["name"]
        for event in tree.findall(".//bpmn:endEvent", BPMN_NS)
    }
    assert "Classify role assignment" in business_rule_names
    assert "Review access request" in user_task_names
    assert "Provision role and scope" in user_task_names
    assert "Record access rejection" in service_task_names
    assert "Write access audit" in service_task_names
    assert "Access approved?" in gateway_names
    assert {"Access rejected", "Access provisioned"}.issubset(end_event_names)


def test_stage_daily_cycle_bpmn_covers_end_to_end_rehearsal_path() -> None:
    tree = ElementTree.parse(STAGE_DAILY_CYCLE_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "stage_daily_cycle_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    assert "Run DQ checks" in service_task_names
    assert "Run regular forecast" in service_task_names
    assert "Run promo forecast" in service_task_names
    assert "Generate order proposals" in service_task_names
    assert "Publish stage exports" in service_task_names
    assert "Review stage exceptions" in user_task_names
    assert "Evaluate stage go/no-go" in business_rule_names


def test_pilot_operational_bpmn_covers_feedback_triage_and_acceptance_paths() -> None:
    tree = ElementTree.parse(PILOT_OPERATIONAL_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "pilot_operational_process"
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    gateway_names = {
        gateway.attrib["name"]
        for gateway in tree.findall(".//bpmn:exclusiveGateway", BPMN_NS)
    }
    assert "Review pilot forecast" in user_task_names
    assert "Approve pilot order" in user_task_names
    assert "Collect pilot feedback" in user_task_names
    assert "Triage pilot issue" in user_task_names
    assert "Sign pilot acceptance" in user_task_names
    assert "Evaluate pilot thresholds" in business_rule_names
    assert "Write pilot audit" in service_task_names
    assert "Pilot acceptance ready?" in gateway_names


def test_industrial_data_load_bpmn_covers_partition_lineage_dq_and_reprocess_paths() -> None:
    tree = ElementTree.parse(INDUSTRIAL_DATA_LOAD_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "industrial_data_load_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    gateway_names = {
        gateway.attrib["name"]
        for gateway in tree.findall(".//bpmn:exclusiveGateway", BPMN_NS)
    }
    assert "Load raw partitions" in service_task_names
    assert "Validate partition counts" in service_task_names
    assert "Write lineage edges" in service_task_names
    assert "Reprocess failed partitions" in service_task_names
    assert "Publish industrial mart" in service_task_names
    assert "Evaluate industrial DQ gate" in business_rule_names
    assert "Review large-scale data incident" in user_task_names
    assert "Industrial DQ passed?" in gateway_names


def test_model_release_bpmn_covers_retraining_shadow_approval_and_rollback_paths() -> None:
    tree = ElementTree.parse(MODEL_RELEASE_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "model_release_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    end_event_names = {
        event.attrib["name"]
        for event in tree.findall(".//bpmn:endEvent", BPMN_NS)
    }
    assert "Run backtesting" in service_task_names
    assert "Detect model drift" in service_task_names
    assert "Run shadow comparison" in service_task_names
    assert "Rollback model" in service_task_names
    assert "Publish model release" in service_task_names
    assert "Evaluate model release gate" in business_rule_names
    assert "Review model drift" in user_task_names
    assert "Approve model release" in user_task_names
    assert {"Model released", "Model rolled back"}.issubset(end_event_names)


def test_industrial_replenishment_bpmn_covers_bulk_approval_and_async_export_paths() -> None:
    tree = ElementTree.parse(INDUSTRIAL_REPLENISHMENT_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "industrial_replenishment_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    gateway_names = {
        gateway.attrib["name"]
        for gateway in tree.findall(".//bpmn:exclusiveGateway", BPMN_NS)
    }
    assert "Calculate projected stock partitions" in service_task_names
    assert "Generate partitioned order proposals" in service_task_names
    assert "Evaluate constraints at scale" in service_task_names
    assert "Queue async export" in service_task_names
    assert "Apply proposal retention" in service_task_names
    assert "Evaluate bulk auto approval" in business_rule_names
    assert "Review replenishment scale exception" in user_task_names
    assert "Approve bulk proposals" in user_task_names
    assert "Bulk approval allowed?" in gateway_names


def test_process_change_management_bpmn_covers_validation_approval_deploy_migration_and_rejection_paths() -> None:
    tree = ElementTree.parse(PROCESS_CHANGE_MANAGEMENT_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "process_change_management_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    end_event_names = {
        event.attrib["name"]
        for event in tree.findall(".//bpmn:endEvent", BPMN_NS)
    }
    assert "Validate process artifacts" in service_task_names
    assert "Run process test suite" in service_task_names
    assert "Deploy process version" in service_task_names
    assert "Migrate existing instances" in service_task_names
    assert "Publish process release notes" in service_task_names
    assert "Record process change rejection" in service_task_names
    assert "Evaluate process change risk" in business_rule_names
    assert "Review process change" in user_task_names
    assert {"Process change rejected", "Process change deployed"}.issubset(end_event_names)


def test_incident_management_bpmn_covers_alert_ack_runbook_escalation_and_closure_paths() -> None:
    tree = ElementTree.parse(INCIDENT_MANAGEMENT_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "incident_management_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    gateway_names = {
        gateway.attrib["name"]
        for gateway in tree.findall(".//bpmn:exclusiveGateway", BPMN_NS)
    }
    assert "Create incident" in service_task_names
    assert "Write incident timeline" in service_task_names
    assert "Classify incident severity" in business_rule_names
    assert "Acknowledge incident" in user_task_names
    assert "Open runbook" in user_task_names
    assert "Escalate incident" in user_task_names
    assert "Resolve incident" in user_task_names
    assert "Incident resolved?" in gateway_names


def test_release_go_no_go_bpmn_covers_regression_dr_handover_risk_approval_and_decision_paths() -> None:
    tree = ElementTree.parse(RELEASE_GO_NO_GO_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "release_go_no_go_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    end_event_names = {
        event.attrib["name"]
        for event in tree.findall(".//bpmn:endEvent", BPMN_NS)
    }
    assert "Run full regression" in service_task_names
    assert "Run DR smoke" in service_task_names
    assert "Publish release decision" in service_task_names
    assert "Record no-go decision" in service_task_names
    assert "Evaluate release readiness" in business_rule_names
    assert "Confirm support handover" in user_task_names
    assert "Accept release risks" in user_task_names
    assert "Collect go/no-go approvals" in user_task_names
    assert {"Release go", "Release no-go"}.issubset(end_event_names)


def test_purchase_proposal_bpmn_covers_supplier_selection_share_exception_and_export_paths() -> None:
    tree = ElementTree.parse(PURCHASE_PROPOSAL_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "purchase_proposal_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    gateway_names = {
        gateway.attrib["name"]
        for gateway in tree.findall(".//bpmn:exclusiveGateway", BPMN_NS)
    }
    assert "Load supplier contracts" in service_task_names
    assert "Export supplier order" in service_task_names
    assert "Select supplier" in business_rule_names
    assert "Check supplier share exception" in business_rule_names
    assert "Review supplier constraint" in user_task_names
    assert "Approve purchase proposal" in user_task_names
    assert "Supplier exception?" in gateway_names


def test_shelf_space_review_bpmn_covers_capacity_direct_to_shelf_review_and_audit_paths() -> None:
    tree = ElementTree.parse(SHELF_SPACE_REVIEW_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "shelf_space_review_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    gateway_names = {
        gateway.attrib["name"]
        for gateway in tree.findall(".//bpmn:exclusiveGateway", BPMN_NS)
    }
    assert "Load planogram capacity" in service_task_names
    assert "Write shelf audit" in service_task_names
    assert "Evaluate display capacity" in business_rule_names
    assert "Evaluate direct-to-shelf" in business_rule_names
    assert "Review shelf capacity warning" in user_task_names
    assert "Approve shelf values" in user_task_names
    assert "Shelf capacity warning?" in gateway_names


def test_capacity_smoothing_bpmn_covers_overload_preview_approval_and_publish_paths() -> None:
    tree = ElementTree.parse(CAPACITY_SMOOTHING_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "capacity_smoothing_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    gateway_names = {
        gateway.attrib["name"]
        for gateway in tree.findall(".//bpmn:exclusiveGateway", BPMN_NS)
    }
    assert "Load capacity calendar" in service_task_names
    assert "Create smoothing preview" in service_task_names
    assert "Publish capacity plan" in service_task_names
    assert "Detect capacity overload" in business_rule_names
    assert "Prioritize order shifts" in business_rule_names
    assert "Review capacity overload" in user_task_names
    assert "Approve order moves" in user_task_names
    assert "Capacity overload?" in gateway_names


def test_diagnostic_insight_review_bpmn_covers_evidence_classification_exception_and_audit_paths() -> None:
    tree = ElementTree.parse(DIAGNOSTIC_INSIGHT_REVIEW_PROCESS_PATH)
    process = tree.find("bpmn:process", BPMN_NS)

    assert process is not None
    assert process.attrib["id"] == "diagnostic_insight_review_process"
    service_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:serviceTask", BPMN_NS)
    }
    business_rule_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:businessRuleTask", BPMN_NS)
    }
    user_task_names = {
        task.attrib["name"]
        for task in tree.findall(".//bpmn:userTask", BPMN_NS)
    }
    gateway_names = {
        gateway.attrib["name"]
        for gateway in tree.findall(".//bpmn:exclusiveGateway", BPMN_NS)
    }
    assert "Collect evidence" in service_task_names
    assert "Link objects and audit decision" in service_task_names
    assert "Classify root cause" in business_rule_names
    assert "Review root cause card" in user_task_names
    assert "Create exception from insight" in user_task_names
    assert "Action required?" in gateway_names
