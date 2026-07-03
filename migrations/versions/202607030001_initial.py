"""initial schema

Revision ID: 202607030001
Revises:
Create Date: 2026-07-03 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "202607030001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "retailers",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("base_url", sa.String(length=1000), nullable=False),
        sa.Column("adapter_path", sa.String(length=300), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("uses_browser", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_retailers_slug", "retailers", ["slug"], unique=True)
    op.create_unique_constraint("uq_retailers_name", "retailers", ["name"])

    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("retailer", sa.String(length=120), nullable=False),
        sa.Column("retailer_product_id", sa.String(length=160), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("brand", sa.String(length=160), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("available_sizes", sa.JSON(), nullable=False),
        sa.Column("colors", sa.JSON(), nullable=False),
        sa.Column("material", sa.String(length=180), nullable=True),
        sa.Column("condition", sa.String(length=40), nullable=True),
        sa.Column("original_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("sale_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("shipping_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("discount_percent", sa.Float(), nullable=True),
        sa.Column("product_url", sa.String(length=1000), nullable=False),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("in_stock", sa.Boolean(), nullable=False),
        sa.Column("date_discovered", sa.DateTime(timezone=True), nullable=False),
        sa.Column("date_last_checked", sa.DateTime(timezone=True), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("deal_score", sa.Float(), nullable=False),
        sa.Column("score_explanation", sa.JSON(), nullable=False),
        sa.UniqueConstraint("retailer", "retailer_product_id", name="uq_product_retailer_id"),
    )
    op.create_index("ix_products_retailer", "products", ["retailer"])
    op.create_index("ix_products_title", "products", ["title"])
    op.create_index("ix_products_brand", "products", ["brand"])
    op.create_index("ix_products_title_brand", "products", ["title", "brand"])

    op.create_table(
        "search_criteria",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("criteria", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "saved_searches",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("criteria", sa.JSON(), nullable=False),
        sa.Column("alerts_enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "search_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("criteria_id", sa.String(length=36), sa.ForeignKey("search_criteria.id"), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=True),
        sa.Column("total_retailers", sa.Integer(), nullable=False),
        sa.Column("completed_retailers", sa.Integer(), nullable=False),
        sa.Column("products_found", sa.Integer(), nullable=False),
        sa.Column("cancel_requested", sa.Boolean(), nullable=False),
        sa.Column("retailer_errors", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_search_jobs_status", "search_jobs", ["status"])

    op.create_table(
        "retailer_health_status",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("retailer_id", sa.String(length=36), sa.ForeignKey("retailers.id"), nullable=False),
        sa.Column("health", sa.String(length=40), nullable=False),
        sa.Column("error_rate", sa.Float(), nullable=False),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False),
        sa.Column("last_successful_search", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("temporarily_disabled_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("message", sa.String(length=500), nullable=True),
        sa.UniqueConstraint("retailer_id"),
    )

    op.create_table(
        "price_history",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("product_id", sa.String(length=36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("sale_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("shipping_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_price_history_product_id", "price_history", ["product_id"])

    op.create_table(
        "search_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("search_job_id", sa.String(length=36), sa.ForeignKey("search_jobs.id"), nullable=False),
        sa.Column("product_id", sa.String(length=36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("deal_score", sa.Float(), nullable=False),
        sa.Column("ranking", sa.Integer(), nullable=False),
        sa.Column("filtering_reasons", sa.JSON(), nullable=False),
        sa.Column("score_explanation", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_search_results_search_job_id", "search_results", ["search_job_id"])
    op.create_index("ix_search_results_product_id", "search_results", ["product_id"])

    op.create_table(
        "user_favorites",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", sa.String(length=36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "product_id", name="uq_favorite_user_product"),
    )
    op.create_index("ix_user_favorites_user_id", "user_favorites", ["user_id"])
    op.create_index("ix_user_favorites_product_id", "user_favorites", ["product_id"])

    op.create_table(
        "search_alerts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("saved_search_id", sa.String(length=36), sa.ForeignKey("saved_searches.id"), nullable=True),
        sa.Column("alert_type", sa.String(length=80), nullable=False),
        sa.Column("threshold_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("exact_size", sa.String(length=40), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_search_alerts_user_id", "search_alerts", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_search_alerts_user_id", table_name="search_alerts")
    op.drop_table("search_alerts")
    op.drop_index("ix_user_favorites_product_id", table_name="user_favorites")
    op.drop_index("ix_user_favorites_user_id", table_name="user_favorites")
    op.drop_table("user_favorites")
    op.drop_index("ix_search_results_product_id", table_name="search_results")
    op.drop_index("ix_search_results_search_job_id", table_name="search_results")
    op.drop_table("search_results")
    op.drop_index("ix_price_history_product_id", table_name="price_history")
    op.drop_table("price_history")
    op.drop_table("retailer_health_status")
    op.drop_index("ix_search_jobs_status", table_name="search_jobs")
    op.drop_table("search_jobs")
    op.drop_table("saved_searches")
    op.drop_table("search_criteria")
    op.drop_index("ix_products_title_brand", table_name="products")
    op.drop_index("ix_products_brand", table_name="products")
    op.drop_index("ix_products_title", table_name="products")
    op.drop_index("ix_products_retailer", table_name="products")
    op.drop_table("products")
    op.drop_constraint("uq_retailers_name", "retailers", type_="unique")
    op.drop_index("ix_retailers_slug", table_name="retailers")
    op.drop_table("retailers")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

