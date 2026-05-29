from fastapi.testclient import TestClient

from open_fnr_api import audit
from open_fnr_api.main import app
from open_fnr_api import publication
from open_fnr_api.publication import PUBLICATION_PACKAGES, all_items_approved, find_duplicate_export


client = TestClient(app)


class CapturingOperationalDecisionRepository:
    mode = "in_memory"

    def __init__(self) -> None:
        self.decisions = []

    def upsert_decision(self, decision):
        self.decisions.append(decision)
        return decision


def test_publication_packages_expose_status_idempotency_and_responses() -> None:
    response = client.get("/publication/packages")
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 4
    failed = next(item for item in payload["items"] if item["status"] == "failed")
    assert failed["idempotency_key"] == "erp:orders:20260528:001"
    assert failed["linked_exception_id"] == "exc-export-20260528-001"


def test_send_publication_package_requires_export_service_account() -> None:
    response = client.post(
        "/publication/packages/pub-wms-orders-20260528-001/send",
        json={
            "actor": "integration.owner@example.org",
            "service_account": "wrong-account",
            "idempotency_key": "wms:orders:20260528:new",
        },
    )
    assert response.status_code == 403


def test_send_publication_package_rejects_unapproved_items() -> None:
    response = client.post(
        "/publication/packages/pub-wms-orders-20260528-002/send",
        json={
            "actor": "integration.owner@example.org",
            "service_account": "svc-open-fnr-export",
            "idempotency_key": "wms:orders:20260528:002-new",
        },
    )
    assert response.status_code == 409


def test_send_publication_package_is_idempotent() -> None:
    response = client.post(
        "/publication/packages/pub-wms-orders-20260528-001/send",
        json={
            "actor": "integration.owner@example.org",
            "service_account": "svc-open-fnr-export",
            "idempotency_key": "dwh:forecast:20260528:001",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["duplicate"] is True
    assert payload["package"]["package_id"] == "pub-dwh-forecast-20260528-001"


def test_retry_failed_publication_package_increments_retry_count() -> None:
    response = client.post(
        "/publication/packages/pub-erp-orders-20260528-001/retry",
        json={
            "actor": "integration.owner@example.org",
            "service_account": "svc-open-fnr-export",
            "idempotency_key": "erp:orders:20260528:001",
        },
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["package"]["status"] == "sent"
    assert payload["package"]["retry_count"] == 2


def test_publication_send_writes_operational_decision_boundary(monkeypatch) -> None:
    repository = CapturingOperationalDecisionRepository()
    monkeypatch.setattr(publication, "operational_decision_repository", repository)

    response = client.post(
        "/publication/packages/pub-wms-orders-20260528-001/send",
        json={
            "actor": "integration.owner@example.org",
            "service_account": "svc-open-fnr-export",
            "idempotency_key": "wms:orders:20260528:repo",
        },
    )

    assert response.status_code == 200
    assert repository.decisions[0].decision_type == "publication_export"
    assert repository.decisions[0].object_id == "pub-wms-orders-20260528-001"
    assert repository.decisions[0].idempotency_key == "wms:orders:20260528:repo"
    assert repository.decisions[0].payload["target"] == "wms"


def test_send_publication_package_can_post_to_configured_http_target(monkeypatch) -> None:
    calls = []
    original_url = publication.settings.wms_export_url
    original_timeout = publication.settings.publication_http_timeout_seconds

    class FakeResponse:
        status = 202

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b"accepted by wms"

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        return FakeResponse()

    monkeypatch.setattr("open_fnr_api.publication.urlopen", fake_urlopen)
    publication.settings.wms_export_url = "http://wms.integration.local/orders"
    publication.settings.publication_http_timeout_seconds = 17
    try:
        response = client.post(
            "/publication/packages/pub-wms-orders-20260528-001/send",
            json={
                "actor": "integration.owner@example.org",
                "service_account": "svc-open-fnr-export",
                "idempotency_key": "wms:orders:20260528:http",
            },
        )
    finally:
        publication.settings.wms_export_url = original_url
        publication.settings.publication_http_timeout_seconds = original_timeout

    assert response.status_code == 200
    payload = response.json()
    assert payload["package"]["response_code"] == "202"
    assert payload["package"]["response_message"] == "accepted by wms"
    assert len(calls) == 1
    assert calls[0][0].full_url == "http://wms.integration.local/orders"
    assert calls[0][0].headers["Idempotency-key"] == "wms:orders:20260528:http"
    assert calls[0][1] == 17


def test_retry_publication_package_requires_export_service_account() -> None:
    response = client.post(
        "/publication/packages/pub-erp-orders-20260528-001/retry",
        json={
            "actor": "integration.owner@example.org",
            "service_account": "wrong-account",
            "idempotency_key": "erp:orders:20260528:001",
        },
    )
    assert response.status_code == 403


def test_send_publication_package_does_not_auto_record_audit_when_disabled() -> None:
    before = client.get("/audit/events", params={"limit": 500}).json()
    original_value = audit.settings.audit_enabled
    audit.settings.audit_enabled = False
    try:
        response = client.post(
            "/publication/packages/pub-wms-orders-20260528-001/send",
            json={
                "actor": "integration.owner@example.org",
                "service_account": "svc-open-fnr-export",
                "idempotency_key": "wms:orders:20260528:new",
            },
        )
    finally:
        audit.settings.audit_enabled = original_value
    assert response.status_code == 200

    after = client.get("/audit/events", params={"limit": 500}).json()
    assert len(after) == len(before)


def test_publication_helpers() -> None:
    assert all_items_approved(PUBLICATION_PACKAGES[0]) is True
    assert all_items_approved(PUBLICATION_PACKAGES[3]) is False
    assert find_duplicate_export("dwh:forecast:20260528:001").package_id == "pub-dwh-forecast-20260528-001"
