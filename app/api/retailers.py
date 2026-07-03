from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.models import Retailer, RetailerHealthStatus
from app.schemas.retailer import RetailerRead, RetailerStatusRead


router = APIRouter()


@router.get("", response_model=list[RetailerRead])
async def list_retailers(session: AsyncSession = Depends(get_session)) -> list[Retailer]:
    return (await session.scalars(select(Retailer).order_by(Retailer.name))).all()


@router.get("/status", response_model=list[RetailerStatusRead])
async def retailer_status(session: AsyncSession = Depends(get_session)) -> list[RetailerHealthStatus]:
    return (
        await session.scalars(
            select(RetailerHealthStatus)
            .join(Retailer)
            .order_by(Retailer.name)
        )
    ).all()

