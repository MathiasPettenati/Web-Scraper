from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.errors import ApiError
from app.database.session import get_session
from app.models import Product, UserFavorite
from app.schemas.product import ProductRead
from app.services.users import get_or_create_demo_user


router = APIRouter()


@router.post("/{product_id}", response_model=ProductRead)
async def add_favorite(product_id: str, session: AsyncSession = Depends(get_session)) -> Product:
    user = await get_or_create_demo_user(session)
    product = await session.get(Product, product_id)
    if not product:
        raise ApiError(404, "PRODUCT_NOT_FOUND", "The product was not found.", {"product_id": product_id})
    existing = await session.scalar(
        select(UserFavorite).where(
            UserFavorite.user_id == user.id,
            UserFavorite.product_id == product_id,
        )
    )
    if existing is None:
        session.add(UserFavorite(user_id=user.id, product_id=product_id))
        await session.commit()
    return product


@router.delete("/{product_id}")
async def remove_favorite(product_id: str, session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    user = await get_or_create_demo_user(session)
    await session.execute(
        delete(UserFavorite).where(
            UserFavorite.user_id == user.id,
            UserFavorite.product_id == product_id,
        )
    )
    await session.commit()
    return {"message": "deleted"}


@router.get("", response_model=list[ProductRead])
async def list_favorites(session: AsyncSession = Depends(get_session)) -> list[Product]:
    user = await get_or_create_demo_user(session)
    favorites = (
        await session.scalars(
            select(UserFavorite)
            .where(UserFavorite.user_id == user.id)
            .options(selectinload(UserFavorite.product))
            .order_by(UserFavorite.created_at.desc())
        )
    ).all()
    return [favorite.product for favorite in favorites]

