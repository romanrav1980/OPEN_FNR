from pathlib import Path
from xml.etree import ElementTree


BPMN_NS = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
PROCESS_PATH = Path("processes/dev-healthcheck/dev_healthcheck_process.bpmn20.xml")


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
