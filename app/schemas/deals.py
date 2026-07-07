from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DealFilterRequest(BaseModel):
    query: str | None = None
    country: str | None = None
    category: str | None = None
    brand: str | None = None
    size: str | None = None
    color: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    discount_min: float | None = None
    store: str | None = None
    condition: str | None = None
    availability: str | None = None
    shipping_max: float | None = None
    sort: str = "best_deal"
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=6, ge=1, le=48)


class NearbyLocationRequest(BaseModel):
    lat: float
    lng: float
    country: str | None = None


class ProductDetail(BaseModel):
    id: str
    title: str
    brand: str
    category: str
    color: str
    condition: str
    store: str
    country: str
    currency: str
    price: float
    original_price: float
    discount_percent: int
    sizes: list[str]
    shipping_cost: float
    shipping_time: str
    rating: float
    popularity: int
    in_stock: bool
    verified: bool
    availability: str
    source_url: str
    last_verified: str
    image_url: str
    description: str
    tags: list[str]
    location_hint: str
    deal_score: float
    metadata: dict[str, Any] = Field(default_factory=dict)
