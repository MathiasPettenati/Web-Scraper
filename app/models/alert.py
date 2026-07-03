from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.common import utc_now, uuid_str


class SearchAlert(Base):
    __tablename__ = "search_alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    saved_search_id: Mapped[str | None] = mapped_column(ForeignKey("saved_searches.id"), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(80))
    threshold_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    exact_size: Mapped[str | None] = mapped_column(String(40), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user = relationship("User", back_populates="alerts")
    saved_search = relationship("SavedSearch", back_populates="alerts")

