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
