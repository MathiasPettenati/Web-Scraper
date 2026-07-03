from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.common import utc_now, uuid_str


class SearchCriteriaRecord(Base):
    __tablename__ = "search_criteria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    criteria: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class SearchJob(Base):
    __tablename__ = "search_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    criteria_id: Mapped[str | None] = mapped_column(ForeignKey("search_criteria.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="queued", index=True)
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    total_retailers: Mapped[int] = mapped_column(Integer, default=0)
    completed_retailers: Mapped[int] = mapped_column(Integer, default=0)
    products_found: Mapped[int] = mapped_column(Integer, default=0)
    cancel_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    retailer_errors: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    results = relationship("SearchResult", back_populates="search_job", cascade="all, delete-orphan")
    criteria_record = relationship("SearchCriteriaRecord")


class SearchResult(Base):
    __tablename__ = "search_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    search_job_id: Mapped[str] = mapped_column(ForeignKey("search_jobs.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    deal_score: Mapped[float] = mapped_column(Float, default=0.0)
    ranking: Mapped[int] = mapped_column(Integer, default=0)
    filtering_reasons: Mapped[list[str]] = mapped_column(JSON, default=list)
    score_explanation: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    search_job = relationship("SearchJob", back_populates="results")
    product = relationship("Product", back_populates="results")

