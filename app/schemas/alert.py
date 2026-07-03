from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SearchAlertCreate(BaseModel):
    saved_search_id: str | None = None
    alert_type: str = Field(pattern="^(price_below|discount_above|size_available|new_listing)$")
    threshold_value: Decimal | None = Field(default=None, ge=0)
    exact_size: str | None = Field(default=None, max_length=40)
    enabled: bool = True


class SearchAlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    saved_search_id: str | None
    alert_type: str
    threshold_value: Decimal | None
    exact_size: str | None
    enabled: bool
    last_triggered_at: datetime | None
    created_at: datetime

