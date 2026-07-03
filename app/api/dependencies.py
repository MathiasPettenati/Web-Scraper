from __future__ import annotations

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors import ApiError
from app.core.config import get_settings
from app.core.rate_limit import InMemoryRateLimiter
from app.models import User
from app.services.users import get_or_create_demo_user


settings = get_settings()
search_rate_limiter = InMemoryRateLimiter(settings.search_rate_limit_per_minute)


async def enforce_search_rate_limit(request: Request) -> None:
    client = request.client.host if request.client else "unknown"
    if not search_rate_limiter.allow(client):
        raise ApiError(
            429,
            "RATE_LIMITED",
            "Too many searches were created. Please wait before trying again.",
            {"limit_per_minute": settings.search_rate_limit_per_minute},
        )


async def demo_user(session: AsyncSession) -> User:
    return await get_or_create_demo_user(session)

