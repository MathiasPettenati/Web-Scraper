from __future__ import annotations

from fastapi import APIRouter, Query

from app.samples.products import get_products
from app.schemas.deals import DealFilterRequest, NearbyLocationRequest
from app.services.deals import filter_products, get_country_options, get_filters, paginate

router = APIRouter()


@router.get("/deals")
def list_deals(request: DealFilterRequest = None):
    if request is None:
        request = DealFilterRequest()
    products = get_products()
    filtered = filter_products(
        products,
        query=request.query,
        country=request.country,
        category=request.category,
        brand=request.brand,
        size=request.size,
        color=request.color,
        price_min=request.price_min,
        price_max=request.price_max,
        discount_min=request.discount_min,
        store=request.store,
        condition=request.condition,
        availability=request.availability,
        shipping_max=request.shipping_max,
        sort=request.sort,
    )
    paged_items, page, pages = paginate(filtered, request.page, request.limit)
    return {
        "items": paged_items,
        "page": page,
        "limit": request.limit,
        "total": len(filtered),
        "pages": pages,
    }


@router.get("/deals/filters")
def deal_filters() -> dict[str, list[str]]:
    return get_filters()


@router.get("/deals/featured")
def featured_deals() -> list[dict]:
    products = get_products()
    ranked = filter_products(products, sort="best_deal")[:4]
    return ranked


@router.get("/products/{product_id}")
def product_detail(product_id: str) -> dict:
    products = get_products()
    product = next((candidate for candidate in products if candidate["id"] == product_id), None)
    if not product:
        return {"error": "Product not found"}
    product = dict(product)
    product["deal_score"] = 0
    return product


@router.get("/countries")
def country_catalog() -> list[dict[str, str]]:
    return get_country_options()


@router.post("/geo/nearby")
def nearby_stores(request: NearbyLocationRequest) -> dict[str, object]:
    return {
        "message": "Location permission was granted and nearby retailers were prepared.",
        "country": request.country or "United States",
        "nearby_stores": [
            {"name": "Downtown Pickup Hub", "distance_km": 3.2, "city": "Seattle"},
            {"name": "Local Retail Annex", "distance_km": 5.8, "city": "Bellevue"},
        ],
    }
