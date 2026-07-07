from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_deals_endpoint_returns_products_and_filters() -> None:
    response = client.get("/api/deals", params={"page": 1, "limit": 6})
    assert response.status_code == 200
    payload = response.json()

    assert payload["items"]
    assert payload["page"] == 1
    assert payload["limit"] == 6
    assert any(item["store"] for item in payload["items"])

    filters_response = client.get("/api/deals/filters")
    assert filters_response.status_code == 200
    filters_payload = filters_response.json()
    assert "brands" in filters_payload
    assert "countries" in filters_payload
