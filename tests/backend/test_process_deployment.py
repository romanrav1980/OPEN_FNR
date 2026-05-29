from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.process_deployment import build_process_deployment_package


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
