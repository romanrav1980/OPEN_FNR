from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.release_gate import CHECKLIST, RISKS, ChecklistStatus, ReleaseChecklistItem, ReleaseDecision, release_readiness_decision


client = TestClient(app)


def test_release_candidate_contains_readiness_checklist_and_risk() -> None:
    response = client.get("/release-gate/candidate")
    assert response.status_code == 200

    payload = response.json()
    assert payload["candidate_id"] == "open-fnr-industrial-rc1"
    assert payload["version"] == "0.30.0-rc1"
    assert payload["critical_defects"] == 0
    assert payload["decision"] == "conditional_go"
    assert len(payload["checklist"]) == 5
    assert payload["risks"][0]["status"] == "accepted_risk"


def test_authorized_release_role_can_approve_conditional_go() -> None:
    response = client.post(
        "/release-gate/candidate/approve",
        json={
            "actor": "product.owner@example.org",
            "actor_role": "Product Owner",
            "decision": "conditional_go",
            "comment": "Known medium risk accepted for industrial pilot.",
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "conditional_go"
    assert response.json()["decided_at"] is not None


def test_release_approval_rejects_unauthorized_role() -> None:
    response = client.post(
        "/release-gate/candidate/approve",
        json={
            "actor": "viewer@example.org",
            "actor_role": "Viewer",
            "decision": "go",
            "comment": "not allowed",
        },
    )

    assert response.status_code == 403


def test_release_readiness_decision_go_conditional_and_no_go() -> None:
    failed = (
        ReleaseChecklistItem(item_id="bad", area="regression", status=ChecklistStatus.FAILED, evidence="failed", owner_role="QA"),
    )

    assert release_readiness_decision(CHECKLIST, (), critical_defects=0) == ReleaseDecision.GO
    assert release_readiness_decision(CHECKLIST, RISKS, critical_defects=0) == ReleaseDecision.CONDITIONAL_GO
    assert release_readiness_decision(CHECKLIST, RISKS, critical_defects=1) == ReleaseDecision.NO_GO
    assert release_readiness_decision(failed, (), critical_defects=0) == ReleaseDecision.NO_GO


def test_rollback_plan_contains_export_freeze_restore_migration_and_backup_steps() -> None:
    response = client.get("/release-gate/rollback-plan")
    assert response.status_code == 200

    payload = response.json()
    step_names = {item["name"] for item in payload["steps"]}

    assert payload["ready"] is True
    assert payload["trigger"] == "sev1_or_sev2_after_release_or_failed_migration_gate"
    assert "Freeze controlled exports" in step_names
    assert "Restore previous application version" in step_names
    assert "Apply migration rollback or forward fix decision" in step_names
    assert "Run backup restore smoke evidence check" in step_names


def test_dr_drill_records_restore_evidence_and_degraded_mode() -> None:
    response = client.get("/release-gate/dr-drill")
    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "passed"
    assert payload["degraded_mode"] == "shadow_review_only"
    assert "backup manifest checksum verified" in payload["restore_evidence"]
    assert "publication exports remain stopped until reconciliation passes" in payload["restore_evidence"]


def test_degraded_modes_block_exports_and_keep_review_capabilities() -> None:
    response = client.get("/release-gate/degraded-modes")
    assert response.status_code == 200

    mode = response.json()["items"][0]

    assert mode["mode_id"] == "shadow_review_only"
    assert "forecast review" in mode["allowed_capabilities"]
    assert "ERP export" in mode["blocked_capabilities"]
    assert mode["activation_owner_role"] == "Incident Manager"
