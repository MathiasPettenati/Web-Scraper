from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.product import ProductRead


class Condition(str, Enum):
    new = "new"
    used = "used"
    refurbished = "refurbished"
    any = "any"


class SortMethod(str, Enum):
    best_match = "best_match"
    lowest_total_price = "lowest_total_price"
    highest_discount = "highest_discount"
    highest_deal_score = "highest_deal_score"
    lowest_shipping_price = "lowest_shipping_price"
    newest_listing = "newest_listing"


class SearchCriteria(BaseModel):
    search_phrase: str = Field(min_length=1, max_length=200)
    garment_category: str | None = Field(default=None, max_length=80)
    preferred_brands: list[str] = Field(default_factory=list, max_length=20)
    excluded_brands: list[str] = Field(default_factory=list, max_length=20)
    size: str | None = Field(default=None, max_length=30)
    alternative_sizes: list[str] = Field(default_factory=list, max_length=12)
    color: str | None = Field(default=None, max_length=80)
    material: str | None = Field(default=None, max_length=80)
    condition: Condition = Condition.any
    min_price: Decimal | None = Field(default=None, ge=0)
    max_price: Decimal | None = Field(default=None, ge=0)
    min_discount_percentage: float | None = Field(default=None, ge=0, le=100)
    max_shipping_price: Decimal | None = Field(default=None, ge=0)
    delivery_region: str = Field(default="US", min_length=2, max_length=80)
    preferred_currency: str = Field(default="USD", min_length=3, max_length=3)
    retailers_to_include: list[str] = Field(default_factory=list, max_length=20)
    retailers_to_exclude: list[str] = Field(default_factory=list, max_length=20)
    required_keywords: list[str] = Field(default_factory=list, max_length=20)
    excluded_keywords: list[str] = Field(default_factory=list, max_length=20)
    in_stock_only: bool = True
    sale_products_only: bool = False
    free_shipping_only: bool = False
    sort_method: SortMethod = SortMethod.best_match

    @field_validator(
        "preferred_brands",
        "excluded_brands",
        "alternative_sizes",
        "retailers_to_include",
        "retailers_to_exclude",
        "required_keywords",
        "excluded_keywords",
        mode="before",
    )
    @classmethod
    def split_list_values(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        if isinstance(value, list):
            return [str(part).strip() for part in value if str(part).strip()]
        return value

    @field_validator("preferred_currency")
    @classmethod
    def uppercase_currency(cls, value: str) -> str:
        return value.upper()

    @model_validator(mode="after")
    def validate_price_range(self) -> "SearchCriteria":
        if self.min_price is not None and self.max_price is not None and self.min_price > self.max_price:
            raise ValueError("min_price cannot exceed max_price")
        overlap = set(self.retailers_to_include) & set(self.retailers_to_exclude)
        if overlap:
            raise ValueError("A retailer cannot be both included and excluded")
        return self

    def requested_sizes(self) -> list[str]:
        sizes: list[str] = []
        if self.size:
            sizes.append(self.size)
        sizes.extend(self.alternative_sizes)
        return sizes


class SearchJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    message: str | None
    total_retailers: int
    completed_retailers: int
    products_found: int
    cancel_requested: bool
    retailer_errors: list[dict[str, object]]
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class SearchResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    search_job_id: str
    product_id: str
    match_score: float
    deal_score: float
    ranking: int
    filtering_reasons: list[str]
    score_explanation: list[dict[str, object]]


class SearchResultWithProduct(BaseModel):
    result: SearchResultRead
    product: ProductRead

