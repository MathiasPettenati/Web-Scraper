from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RetailerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    base_url: str
    enabled: bool
    uses_browser: bool


class RetailerStatusRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    retailer_id: str
    health: str
    error_rate: float
    consecutive_failures: int
    last_successful_search: datetime | None
    last_error_at: datetime | None
    temporarily_disabled_until: datetime | None
    message: str | None

