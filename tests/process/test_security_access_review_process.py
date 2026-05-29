from pathlib import Path
from xml.etree import ElementTree


BPMN = Path("processes/security/access_review_process.bpmn20.xml")
NS = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}


def test_access_review_bpmn_contains_required_control_steps() -> None:
    tree = ElementTree.parse(BPMN)
    process = tree.find("bpmn:process", NS)

    assert process is not None
    assert process.attrib["id"] == "access_review_process"

    user_tasks = {task.attrib["id"] for task in process.findall("bpmn:userTask", NS)}
    service_tasks = {task.attrib["id"] for task in process.findall("bpmn:serviceTask", NS)}
    gateways = {gateway.attrib["id"] for gateway in process.findall("bpmn:exclusiveGateway", NS)}

    assert "review_excessive_access" in user_tasks
    assert "remediate_access_scope" in user_tasks
    assert "collect_access_evidence" in service_tasks
    assert "write_access_review_audit" in service_tasks
    assert "access_review_decision" in gateways
