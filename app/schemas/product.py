from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    retailer: str
    retailer_product_id: str | None
    title: str
    description: str | None
    brand: str | None
    category: str | None
    available_sizes: list[str]
    colors: list[str]
    material: str | None
    condition: str | None
    original_price: Decimal | None
    sale_price: Decimal
    shipping_price: Decimal | None
    total_price: Decimal
    currency: str
    discount_percent: float | None
    product_url: str
    image_url: str | None
    in_stock: bool
    date_discovered: datetime
    date_last_checked: datetime
    match_score: float
    deal_score: float
    score_explanation: list[dict[str, object]]


class PriceHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    sale_price: Decimal
    shipping_price: Decimal | None
    total_price: Decimal
    currency: str
    observed_at: datetime

