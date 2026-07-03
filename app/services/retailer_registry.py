from __future__ import annotations

from importlib import import_module

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Retailer
from app.retailers.base import RetailerAdapter
from app.schemas.search import SearchCriteria


def load_adapter(adapter_path: str) -> RetailerAdapter:
    module_path, class_name = adapter_path.rsplit(".", 1)
    module = import_module(module_path)
    adapter_class = getattr(module, class_name)
    return adapter_class()


async def enabled_adapters_for_search(
    session: AsyncSession,
    criteria: SearchCriteria,
) -> list[RetailerAdapter]:
    statement = select(Retailer).where(Retailer.enabled.is_(True))
    if criteria.retailers_to_include:
        statement = statement.where(Retailer.slug.in_(criteria.retailers_to_include))
    if criteria.retailers_to_exclude:
        statement = statement.where(Retailer.slug.not_in(criteria.retailers_to_exclude))
    retailers = (await session.scalars(statement.order_by(Retailer.name))).all()
    return [load_adapter(retailer.adapter_path) for retailer in retailers]

