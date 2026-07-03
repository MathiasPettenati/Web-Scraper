from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors import ApiError
from app.database.session import get_session
from app.models import PriceHistory, Product
from app.schemas.product import PriceHistoryRead, ProductRead


router = APIRouter()


@router.get("/{product_id}", response_model=ProductRead)
async def read_product(product_id: str, session: AsyncSession = Depends(get_session)) -> Product:
    product = await session.get(Product, product_id)
    if not product:
        raise ApiError(404, "PRODUCT_NOT_FOUND", "The product was not found.", {"product_id": product_id})
    return product


@router.get("/{product_id}/price-history", response_model=list[PriceHistoryRead])
async def read_price_history(product_id: str, session: AsyncSession = Depends(get_session)) -> list[PriceHistory]:
    product = await session.get(Product, product_id)
    if not product:
        raise ApiError(404, "PRODUCT_NOT_FOUND", "The product was not found.", {"product_id": product_id})
    return (
        await session.scalars(
            select(PriceHistory)
            .where(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.observed_at)
        )
    ).all()

