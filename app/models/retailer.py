from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.common import uuid_str


class Retailer(Base):
    __tablename__ = "retailers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    base_url: Mapped[str] = mapped_column(String(1000))
    adapter_path: Mapped[str] = mapped_column(String(300))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    uses_browser: Mapped[bool] = mapped_column(Boolean, default=False)

    health_status = relationship(
        "RetailerHealthStatus",
        back_populates="retailer",
        uselist=False,
        cascade="all, delete-orphan",
    )


class RetailerHealthStatus(Base):
    __tablename__ = "retailer_health_status"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    retailer_id: Mapped[str] = mapped_column(ForeignKey("retailers.id"), unique=True)
    health: Mapped[str] = mapped_column(String(40), default="healthy")
    error_rate: Mapped[float] = mapped_column(Float, default=0.0)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0)
    last_successful_search: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    temporarily_disabled_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    retailer = relationship("Retailer", back_populates="health_status")

