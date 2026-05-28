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
