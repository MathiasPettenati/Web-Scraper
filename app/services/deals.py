from __future__ import annotations

from math import ceil
from typing import Any

from app.samples.products import get_countries, get_products


def normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def compute_deal_score(product: dict[str, Any]) -> float:
    discount_bonus = product.get("discount_percent", 0) * 0.8
    rating_bonus = product.get("rating", 0) * 3.0
    shipping_penalty = product.get("shipping_cost", 0) * 0.6
    price_penalty = product.get("price", 0) * 0.01
    return round(discount_bonus + rating_bonus + product.get("popularity", 0) / 20 - shipping_penalty - price_penalty, 2)


def filter_products(
    products: list[dict[str, Any]],
    *,
    query: str | None = None,
    country: str | None = None,
    category: str | None = None,
    brand: str | None = None,
    size: str | None = None,
    color: str | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    discount_min: float | None = None,
    store: str | None = None,
    condition: str | None = None,
    availability: str | None = None,
    shipping_max: float | None = None,
    sort: str = "best_deal",
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    query_term = normalize(query)
    for product in products:
        if query_term and query_term not in normalize(product.get("title")) and query_term not in normalize(product.get("description")) and query_term not in normalize(product.get("brand")):
            continue
        if country and normalize(country) not in normalize(product.get("country")):
            continue
        if category and normalize(category) != normalize(product.get("category")):
            continue
        if brand and normalize(brand) != normalize(product.get("brand")):
            continue
        if size and not any(normalize(size) == normalize(item) for item in product.get("sizes", [])):
            continue
        if color and normalize(color) != normalize(product.get("color")):
            continue
        if price_min is not None and product.get("price", 0) < price_min:
            continue
        if price_max is not None and product.get("price", 0) > price_max:
            continue
        if discount_min is not None and product.get("discount_percent", 0) < discount_min:
            continue
        if store and normalize(store) != normalize(product.get("store")):
            continue
        if condition and normalize(condition) != normalize(product.get("condition")):
            continue
        if availability and normalize(availability) != normalize(product.get("availability")):
            continue
        if shipping_max is not None and product.get("shipping_cost", 0) > shipping_max:
            continue
        product = dict(product)
        product["deal_score"] = compute_deal_score(product)
        filtered.append(product)

    if sort == "lowest_price":
        filtered.sort(key=lambda item: item.get("price", 0))
    elif sort == "highest_discount":
        filtered.sort(key=lambda item: -(item.get("discount_percent", 0)))
    elif sort == "newest":
        filtered.sort(key=lambda item: item.get("last_verified", ""), reverse=True)
    elif sort == "popularity":
        filtered.sort(key=lambda item: -(item.get("popularity", 0)))
    elif sort == "rating":
        filtered.sort(key=lambda item: -(item.get("rating", 0)))
    elif sort == "fastest_delivery":
        filtered.sort(key=lambda item: item.get("shipping_time", ""))
    else:
        filtered.sort(key=lambda item: -(item.get("deal_score", 0)))
    return filtered


def paginate(items: list[dict[str, Any]], page: int, limit: int) -> tuple[list[dict[str, Any]], int, int]:
    start = (page - 1) * limit
    end = start + limit
    return items[start:end], page, ceil(len(items) / limit) if limit else 1


def get_filters() -> dict[str, list[str]]:
    products = get_products()
    return {
        "brands": sorted({product.get("brand", "") for product in products if product.get("brand")}),
        "countries": sorted({product.get("country", "") for product in products if product.get("country")}),
        "stores": sorted({product.get("store", "") for product in products if product.get("store")}),
        "categories": sorted({product.get("category", "") for product in products if product.get("category")}),
        "colors": sorted({product.get("color", "") for product in products if product.get("color")}),
        "sizes": sorted({size for product in products for size in product.get("sizes", [])}),
    }


def get_country_options() -> list[dict[str, str]]:
    return get_countries()
