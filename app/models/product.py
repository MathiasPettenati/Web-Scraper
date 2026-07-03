from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.common import utc_now, uuid_str


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("retailer", "retailer_product_id", name="uq_product_retailer_id"),
        Index("ix_products_title_brand", "title", "brand"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    retailer: Mapped[str] = mapped_column(String(120), index=True)
    retailer_product_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    available_sizes: Mapped[list[str]] = mapped_column(JSON, default=list)
    colors: Mapped[list[str]] = mapped_column(JSON, default=list)
    material: Mapped[str | None] = mapped_column(String(180), nullable=True)
    condition: Mapped[str | None] = mapped_column(String(40), nullable=True)
    original_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    sale_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    shipping_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    discount_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    product_url: Mapped[str] = mapped_column(String(1000))
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    date_discovered: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    date_last_checked: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    deal_score: Mapped[float] = mapped_column(Float, default=0.0)
    score_explanation: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)

    results = relationship("SearchResult", back_populates="product")
    price_history = relationship(
        "PriceHistory",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="PriceHistory.observed_at",
    )
    favorites = relationship("UserFavorite", back_populates="product")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    sale_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    shipping_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    product = relationship("Product", back_populates="price_history")
