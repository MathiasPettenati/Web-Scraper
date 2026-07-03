from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base
from app.database.session import async_session_maker, engine
from app.models import (
    Product,
    PriceHistory,
    Retailer,
    RetailerHealthStatus,
    SavedSearch,
    SearchAlert,
    SearchCriteriaRecord,
    SearchJob,
    SearchResult,
    User,
    UserFavorite,
)


async def init_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        await seed_database(session)


async def seed_database(session: AsyncSession) -> None:
    await _seed_user(session)
    await _seed_retailers(session)
    await session.commit()


async def _seed_user(session: AsyncSession) -> None:
    existing = await session.scalar(
        select(User).where(User.email == "demo@garment.local")
    )
    if existing:
        return
    session.add(
        User(
            email="demo@garment.local",
            display_name="Demo Shopper",
            is_admin=True,
        )
    )


async def _seed_retailers(session: AsyncSession) -> None:
    retailers = [
        {
            "name": "Demo Chic",
            "slug": "demo-chic",
            "base_url": "fixture://demo-chic",
            "adapter_path": "app.retailers.demo_chic.DemoChicAdapter",
            "enabled": True,
            "uses_browser": False,
        },
        {
            "name": "Demo Outlet",
            "slug": "demo-outlet",
            "base_url": "fixture://demo-outlet",
            "adapter_path": "app.retailers.demo_outlet.DemoOutletAdapter",
            "enabled": True,
            "uses_browser": False,
        },
        {
            "name": "Demo Broken",
            "slug": "demo-broken",
            "base_url": "fixture://demo-broken",
            "adapter_path": "app.retailers.demo_broken.DemoBrokenAdapter",
            "enabled": False,
            "uses_browser": False,
        },
    ]
    for payload in retailers:
        retailer = await session.scalar(select(Retailer).where(Retailer.slug == payload["slug"]))
        if retailer is None:
            retailer = Retailer(**payload)
            session.add(retailer)
            await session.flush()
            session.add(RetailerHealthStatus(retailer_id=retailer.id, health="healthy"))
        else:
            for key, value in payload.items():
                setattr(retailer, key, value)

