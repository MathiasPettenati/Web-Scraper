from __future__ import annotations

import asyncio


async def test_search_api_results_and_favorites(api_client) -> None:
    payload = {
        "search_phrase": "jacket",
        "garment_category": "Jackets",
        "preferred_brands": ["Northline"],
        "size": "M",
        "max_price": "250",
    }
    response = await api_client.post("/api/searches", json=payload)
    assert response.status_code == 200, response.text
    search_id = response.json()["id"]

    results = []
    status_payload = {}
    for _ in range(20):
        status_response = await api_client.get(f"/api/searches/{search_id}")
        assert status_response.status_code == 200
        status_payload = status_response.json()
        results_response = await api_client.get(f"/api/searches/{search_id}/results")
        assert results_response.status_code == 200
        results = results_response.json()
        if status_payload["status"] == "completed" and results:
            break
        await asyncio.sleep(0.1)

    assert status_payload["status"] == "completed"
    assert results
    product_id = results[0]["product"]["id"]

    favorite_response = await api_client.post(f"/api/favorites/{product_id}")
    assert favorite_response.status_code == 200

    favorites_response = await api_client.get("/api/favorites")
    assert favorites_response.status_code == 200
    assert favorites_response.json()[0]["id"] == product_id


async def test_saved_search_api(api_client) -> None:
    payload = {
        "name": "Jacket preset",
        "criteria": {"search_phrase": "jacket", "max_price": "200"},
        "alerts_enabled": True,
    }
    response = await api_client.post("/api/saved-searches", json=payload)
    assert response.status_code == 200, response.text
    saved_id = response.json()["id"]

    list_response = await api_client.get("/api/saved-searches")
    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "Jacket preset"

    update_response = await api_client.put(
        f"/api/saved-searches/{saved_id}",
        json={"name": "Updated preset", "alerts_enabled": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated preset"

    delete_response = await api_client.delete(f"/api/saved-searches/{saved_id}")
    assert delete_response.status_code == 200


async def test_health_and_error_envelope(api_client) -> None:
    live = await api_client.get("/health/live")
    assert live.status_code == 200

    missing = await api_client.get("/api/products/missing")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "PRODUCT_NOT_FOUND"


async def test_catalog_image_api_returns_product_svg(api_client) -> None:
    response = await api_client.get(
        "/api/catalog-images/product.svg",
        params={
            "category": "Sneakers",
            "color": "White",
            "brand": "Nike",
            "title": "Nike Low-Top Court Sneaker",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert "<svg" in response.text
    assert "Nike" in response.text
    assert "Sneakers" in response.text
