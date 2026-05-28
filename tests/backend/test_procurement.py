from fastapi.testclient import TestClient

from open_fnr_api.main import app
from open_fnr_api.procurement import CONTRACTS, select_supplier, supplier_score


client = TestClient(app)


def test_supplier_contracts_and_scores_are_explainable() -> None:
    response = client.get("/procurement/contracts")
    assert response.status_code == 200

    contracts = response.json()["items"]
    assert len(contracts) == 2
    assert supplier_score(CONTRACTS[0]) > supplier_score(CONTRACTS[1])


def test_purchase_proposal_selects_best_supplier_without_share_warning() -> None:
    response = client.get("/procurement/proposals")
    assert response.status_code == 200

    proposal = response.json()["items"][0]
    assert proposal["selected_supplier_id"] == "SUP_FAST"
    assert proposal["status"] == "supplier_selected"
    assert proposal["decision"]["target_share_warning"] is False
    assert "fill-rate" in proposal["decision"]["reason"]


def test_procurement_role_can_approve_purchase_proposal_with_audit() -> None:
    response = client.post(
        "/procurement/proposals/purchase-proposal-20260528-001/approve",
        json={
            "actor": "procurement.planner@example.org",
            "actor_role": "Procurement Planner",
            "reason": "Supplier choice accepted before cutoff.",
        },
    )

    assert response.status_code == 200
    assert response.json()["proposal"]["status"] == "approved"
    assert "SUP_FAST" in response.json()["audit_message"]


def test_purchase_approval_rejects_wrong_role() -> None:
    response = client.post(
        "/procurement/proposals/purchase-proposal-20260528-001/approve",
        json={"actor": "viewer@example.org", "actor_role": "Viewer", "reason": "not allowed"},
    )

    assert response.status_code == 403


def test_erp_supplier_export_is_idempotent() -> None:
    response = client.get("/procurement/proposals/purchase-proposal-20260528-001/erp-export")
    assert response.status_code == 200

    payload = response.json()
    assert payload["target"] == "ERP supplier purchase mock"
    assert payload["supplier_id"] == "SUP_FAST"
    assert payload["idempotency_key"] == "purchase-proposal-20260528-001:SUP_FAST:v1"


def test_supplier_selection_warns_when_best_supplier_exceeds_target_share() -> None:
    overloaded = (
        CONTRACTS[0].model_copy(update={"current_share": 0.72}),
        CONTRACTS[1],
    )

    decision = select_supplier(overloaded)
    assert decision.supplier_id == "SUP_FAST"
    assert decision.target_share_warning is True
