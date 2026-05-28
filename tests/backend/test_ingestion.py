from fastapi.testclient import TestClient

from open_fnr_api.main import app


client = TestClient(app)


def test_contracts_endpoint_lists_core_domains() -> None:
    response = client.get("/data/contracts")
    assert response.status_code == 200

    domains = {item["domain"] for item in response.json()["contracts"]}
    assert {"sales", "stock", "prices", "product_mdm", "store_mdm", "calendar"} <= domains


def test_ingestion_status_can_filter_by_domain() -> None:
    response = client.get("/data/ingestion/status", params={"domain": "sales"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["domain"] == "sales"


def test_ingestion_status_returns_404_for_unknown_batch() -> None:
    response = client.get("/data/ingestion/status/missing-batch")
    assert response.status_code == 404
