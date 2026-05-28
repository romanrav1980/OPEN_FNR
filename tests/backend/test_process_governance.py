from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.process_governance import CHANGE_REQUESTS, process_change_deployable


client = TestClient(app)


def test_process_versions_and_changes_are_visible() -> None:
    versions = client.get("/process-governance/versions")
    changes = client.get("/process-governance/changes")

    assert versions.status_code == 200
    assert changes.status_code == 200
    assert versions.json()["total"] == 2
    assert changes.json()["items"][0]["change_id"] == "proc-change-20260528-001"
    assert changes.json()["items"][0]["release_notes"]


def test_release_manager_can_deploy_process_change_with_migration_safety() -> None:
    response = client.post(
        "/process-governance/changes/proc-change-20260528-001/deploy",
        json={
            "actor": "release.manager@example.org",
            "actor_role": "Release Manager",
            "comment": "Deploy DMN v2 after process suite passed.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "deployed"
    assert payload["migration_required"] is True
    assert payload["existing_instances_safe"] is True


def test_non_release_manager_cannot_deploy_process_change() -> None:
    response = client.post(
        "/process-governance/changes/proc-change-20260528-001/deploy",
        json={
            "actor": "bpm.owner@example.org",
            "actor_role": "BPM Owner",
            "comment": "not allowed",
        },
    )

    assert response.status_code == 403


def test_process_owner_can_rollback_process_change() -> None:
    response = client.post(
        "/process-governance/changes/proc-change-20260528-001/rollback",
        json={
            "actor": "process.owner@example.org",
            "actor_role": "Process Owner",
            "comment": "Rollback rehearsal.",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rolled_back"
    assert response.json()["existing_instances_safe"] is True


def test_process_change_deployable_helper_blocks_wrong_state_or_version() -> None:
    change = CHANGE_REQUESTS[0]
    draft = change.model_copy(update={"status": "draft"})
    wrong_version = change.model_copy(update={"to_version": 1})
    high_risk = change.model_copy(update={"risk": "high"})

    assert process_change_deployable(change) is True
    assert process_change_deployable(draft) is False
    assert process_change_deployable(wrong_version) is False
    assert process_change_deployable(high_risk) is False
