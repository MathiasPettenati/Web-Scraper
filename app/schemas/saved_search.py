from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.search import SearchCriteria


class SavedSearchCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    criteria: SearchCriteria
    alerts_enabled: bool = False


class SavedSearchUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    criteria: SearchCriteria | None = None
    alerts_enabled: bool | None = None


class SavedSearchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str | None
    name: str
    criteria: dict[str, object]
    alerts_enabled: bool
    created_at: datetime
    updated_at: datetime

