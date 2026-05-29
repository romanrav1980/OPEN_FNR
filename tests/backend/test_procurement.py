from fastapi.testclient import TestClient

from open_fnr_api import procurement
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
    assert payload["target"] == "ERP supplier purchase"
    assert payload["supplier_id"] == "SUP_FAST"
    assert payload["idempotency_key"] == "purchase-proposal-20260528-001:SUP_FAST:v1"
    assert payload["export_channel"] == "local_fallback"


def test_erp_supplier_export_send_uses_local_fallback_with_audit() -> None:
    response = client.post(
        "/procurement/proposals/purchase-proposal-20260528-001/erp-export/send",
        json={
            "actor": "procurement.planner@example.org",
            "actor_role": "Procurement Planner",
            "service_account": "svc-open-fnr-procurement-export",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["export"]["export_channel"] == "local_fallback"
    assert payload["response_code"] == "202"
    assert payload["audit_recorded"] is True


def test_erp_supplier_export_send_requires_service_account() -> None:
    response = client.post(
        "/procurement/proposals/purchase-proposal-20260528-001/erp-export/send",
        json={
            "actor": "procurement.planner@example.org",
            "actor_role": "Procurement Planner",
            "service_account": "wrong-account",
        },
    )
    assert response.status_code == 403


def test_erp_supplier_export_can_post_to_configured_http_target(monkeypatch) -> None:
    calls = []
    original_url = procurement.settings.erp_export_url
    original_timeout = procurement.settings.publication_http_timeout_seconds

    class FakeResponse:
        status = 202

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b"accepted by erp"

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        return FakeResponse()

    monkeypatch.setattr("open_fnr_api.procurement.urlopen", fake_urlopen)
    procurement.settings.erp_export_url = "http://erp.integration.local/purchases"
    procurement.settings.publication_http_timeout_seconds = 23
    try:
        response = client.post(
            "/procurement/proposals/purchase-proposal-20260528-001/erp-export/send",
            json={
                "actor": "procurement.planner@example.org",
                "actor_role": "Procurement Planner",
                "service_account": "svc-open-fnr-procurement-export",
            },
        )
    finally:
        procurement.settings.erp_export_url = original_url
        procurement.settings.publication_http_timeout_seconds = original_timeout

    assert response.status_code == 200
    payload = response.json()
    assert payload["export"]["export_channel"] == "http_api"
    assert payload["response_message"] == "accepted by erp"
    assert calls[0][0].full_url == "http://erp.integration.local/purchases"
    assert calls[0][0].headers["Idempotency-key"] == "purchase-proposal-20260528-001:SUP_FAST:v1"
    assert calls[0][1] == 23


def test_supplier_selection_warns_when_best_supplier_exceeds_target_share() -> None:
    overloaded = (
        CONTRACTS[0].model_copy(update={"current_share": 0.72}),
        CONTRACTS[1],
    )

    decision = select_supplier(overloaded)
    assert decision.supplier_id == "SUP_FAST"
    assert decision.target_share_warning is True
