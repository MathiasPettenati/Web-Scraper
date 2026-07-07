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
    assert all(item["source_url"].startswith("/api/deals/products/") for item in payload["items"])
    assert all(item["image_url"].startswith("/api/catalog-images/product.svg?") for item in payload["items"])
    assert all("images.unsplash.com" not in item["image_url"] for item in payload["items"])

    filters_response = client.get("/api/deals/filters")
    assert filters_response.status_code == 200
    filters_payload = filters_response.json()
    assert "brands" in filters_payload
    assert "countries" in filters_payload
    assert len(filters_payload["brands"]) >= 20
    assert "Mango" in filters_payload["brands"]
    assert "New Balance" in filters_payload["brands"]


def test_deal_product_link_opens_direct_product_page() -> None:
    response = client.get("/api/deals/products/sku-011/page")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Dri-FIT One Training Top" in response.text
    assert "/api/catalog-images/product.svg?" in response.text
