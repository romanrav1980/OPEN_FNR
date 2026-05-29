from fastapi.testclient import TestClient
from zipfile import ZipFile
from io import BytesIO

from open_fnr_api.main import app
from open_fnr_api.process_deployment import (
    build_bpmn_quality_report,
    build_flowable_bar_archive,
    build_multipart_deployment_body,
    build_process_deployability_report,
    build_process_deployment_package,
    build_process_runtime_strategy_report,
    deploy_process_package_to_flowable,
    normalize_bpmn_for_flowable_deployment,
)


client = TestClient(app)


def test_process_deployment_package_discovers_bpmn_dmn_and_cmmn_artifacts() -> None:
    package = build_process_deployment_package()

    assert package.artifact_count > 0
    assert package.bpmn_count > 0
    assert package.dmn_count > 0
    assert package.cmmn_count > 0
    assert all(len(artifact.checksum_sha256) == 64 for artifact in package.artifacts)


def test_process_deployment_package_endpoint_exposes_flowable_deployment_url() -> None:
    response = client.get("/process-deployment/packages/current")
    assert response.status_code == 200

    payload = response.json()
    assert payload["package_id"] == "flowable-processes-v1"
    assert payload["deploy_channel"] == "flowable_rest"
    assert payload["deployment_url"].endswith("/flowable-rest/service/repository/deployments")
    assert payload["artifact_count"] == payload["bpmn_count"] + payload["dmn_count"] + payload["cmmn_count"]


def test_process_deployment_validate_endpoint_is_idempotent() -> None:
    first = client.post("/process-deployment/packages/current/validate")
    second = client.post("/process-deployment/packages/current/validate")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["artifact_count"] == second.json()["artifact_count"]
    assert first.json()["artifacts"][0]["checksum_sha256"] == second.json()["artifacts"][0]["checksum_sha256"]


def test_process_deployment_dry_run_does_not_call_flowable() -> None:
    response = client.post(
        "/process-deployment/packages/current/deploy",
        json={"execute": False, "deployment_name": "OPEN_FNR_TEST"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "validated"
    assert payload["execution_mode"] == "dry_run"
    assert payload["deployed_artifacts"] == 0
    assert "runtime-deployable BPMN" in payload["message"]


def test_process_deployment_deployability_endpoint_exposes_runtime_safe_subset() -> None:
    response = client.get("/process-deployment/packages/current/deployability")

    assert response.status_code == 200
    payload = response.json()
    assert payload["bpmn_total"] > payload["bpmn_requires_model_fix"]
    assert payload["dmn_governance_artifacts"] > 0
    assert payload["cmmn_governance_artifacts"] > 0


def test_process_deployment_runtime_strategy_separates_runtime_and_governance_artifacts() -> None:
    report = build_process_runtime_strategy_report()

    strategies = {item.artifact_type: item for item in report.items}

    assert strategies["bpmn"].strategy == "runtime_deploy"
    assert strategies["bpmn"].status == "ready"
    assert strategies["dmn"].strategy == "governed_artifact"
    assert strategies["dmn"].status == "governed_not_runtime_deployed"
    assert strategies["cmmn"].strategy == "governed_artifact"


def test_process_deployment_runtime_strategy_endpoint() -> None:
    response = client.get("/process-deployment/packages/current/runtime-strategy")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 3
    assert {item["artifact_type"] for item in payload["items"]} == {"bpmn", "dmn", "cmmn"}


def test_process_deployment_bpmn_quality_gate_has_no_blockers() -> None:
    report = build_bpmn_quality_report()

    assert report.bpmn_total == 38
    assert report.quality_gate == "passed"
    assert report.blocker_count == 0
    assert not [issue for issue in report.issues if issue.issue_type == "question_gateway_without_alternative"]
    assert report.cognitive_challenge_count > 0


def test_process_deployment_bpmn_quality_endpoint_exposes_cognitive_challenges() -> None:
    response = client.get("/process-deployment/packages/current/bpmn-quality")

    assert response.status_code == 200
    payload = response.json()
    assert payload["quality_gate"] == "passed"
    assert payload["blocker_count"] == 0
    assert payload["cognitive_challenge_count"] > 0


def test_process_deployment_multipart_body_contains_artifacts() -> None:
    package = build_process_deployment_package()
    body = build_multipart_deployment_body(package, deployment_name="OPEN_FNR_TEST")

    assert b'name="deploymentName"' in body
    assert b"OPEN_FNR_TEST" in body
    assert b'filename="open-fnr-processes.bar"' in body
    assert body.count(b'Content-Disposition: form-data; name="file";') == 1


def test_process_deployment_bar_archive_contains_manifest_and_all_artifacts() -> None:
    package = build_process_deployment_package()
    report = build_process_deployability_report()
    archive_bytes = build_flowable_bar_archive(package)

    with ZipFile(BytesIO(archive_bytes)) as archive:
        names = archive.namelist()

    assert "open-fnr-deployment-manifest.json" in names
    assert len(names) == report.bpmn_runtime_deployable + 1


def test_process_deployment_deployability_report_finds_model_fix_items() -> None:
    report = build_process_deployability_report()

    assert report.bpmn_total > 0
    assert report.bpmn_runtime_deployable > 0
    assert report.dmn_governance_artifacts > 0
    assert report.cmmn_governance_artifacts > 0
    assert report.bpmn_requires_model_fix == 0
    assert report.bpmn_runtime_deployable == report.bpmn_total
    assert report.issues == ()


def test_process_deployment_normalizes_service_tasks_for_flowable() -> None:
    source = b"""<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
  <process id="p" isExecutable="true">
    <serviceTask id="s" name="Resolve" />
    <businessRuleTask id="d" name="Decide" />
  </process>
</definitions>
"""

    normalized = normalize_bpmn_for_flowable_deployment(source)

    assert b"openFnrNoopDelegate" in normalized
    assert b"businessRuleTask" not in normalized


def test_process_deployment_execute_records_flowable_deployment_id() -> None:
    class FakeResponse:
        status = 201

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"id":"flowable-deploy-test-001"}'

    captured: dict[str, object] = {}

    def fake_opener(request: object, timeout: int) -> FakeResponse:
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse()

    package = build_process_deployment_package()
    result = deploy_process_package_to_flowable(package, deployment_name="OPEN_FNR_TEST", opener=fake_opener)
    report = build_process_deployability_report()

    assert result.status == "deployed"
    assert result.execution_mode == "execute"
    assert result.deployment_id == "flowable-deploy-test-001"
    assert result.deployed_artifacts == report.bpmn_runtime_deployable
    assert captured["timeout"] > 0
