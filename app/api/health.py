from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.database.session import async_session_maker


router = APIRouter()


@router.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def ready() -> dict[str, str]:
    async with async_session_maker() as session:
        await session.execute(text("select 1"))
    return {"status": "ready"}

