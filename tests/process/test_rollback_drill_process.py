from pathlib import Path
from xml.etree import ElementTree


BPMN = Path("processes/release-gate/rollback_drill_process.bpmn20.xml")
NS = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}


def test_rollback_drill_bpmn_covers_release_recovery_controls() -> None:
    tree = ElementTree.parse(BPMN)
    process = tree.find("bpmn:process", NS)

    assert process is not None
    assert process.attrib["id"] == "rollback_drill_process"

    service_tasks = {task.attrib["id"] for task in process.findall("bpmn:serviceTask", NS)}
    user_tasks = {task.attrib["id"] for task in process.findall("bpmn:userTask", NS)}
    rule_tasks = {task.attrib["id"] for task in process.findall("bpmn:businessRuleTask", NS)}
    gateways = {gateway.attrib["id"] for gateway in process.findall("bpmn:exclusiveGateway", NS)}

    assert "freeze_controlled_exports" in service_tasks
    assert "restore_previous_application_version" in service_tasks
    assert "validate_backup_restore_smoke" in service_tasks
    assert "run_reconciliation_gate" in service_tasks
    assert "write_dr_evidence" in service_tasks
    assert "apply_migration_recovery" in user_tasks
    assert "activate_degraded_mode_if_needed" in user_tasks
    assert "classify_rollback_path" in rule_tasks
    assert "resume_exports_gateway" in gateways
