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
