from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.process_deployment import (
    build_multipart_deployment_body,
    build_process_deployment_package,
    deploy_process_package_to_flowable,
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


def test_process_deployment_multipart_body_contains_artifacts() -> None:
    package = build_process_deployment_package()
    body = build_multipart_deployment_body(package, deployment_name="OPEN_FNR_TEST")

    assert b'name="deploymentName"' in body
    assert b"OPEN_FNR_TEST" in body
    assert body.count(b'Content-Disposition: form-data; name="file";') == package.artifact_count


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

    assert result.status == "deployed"
    assert result.execution_mode == "execute"
    assert result.deployment_id == "flowable-deploy-test-001"
    assert result.deployed_artifacts == package.artifact_count
    assert captured["timeout"] > 0
