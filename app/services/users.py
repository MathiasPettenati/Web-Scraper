from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import User


async def get_or_create_demo_user(session: AsyncSession) -> User:
    settings = get_settings()
    user = await session.scalar(select(User).where(User.email == settings.demo_user_email))
    if user:
        return user
    user = User(email=settings.demo_user_email, display_name="Demo Shopper", is_admin=True)
    session.add(user)
    await session.flush()
    return user

