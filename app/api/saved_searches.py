from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors import ApiError
from app.database.session import get_session
from app.models import SavedSearch
from app.schemas.saved_search import SavedSearchCreate, SavedSearchRead, SavedSearchUpdate
from app.services.users import get_or_create_demo_user


router = APIRouter()


@router.post("", response_model=SavedSearchRead)
async def create_saved_search(payload: SavedSearchCreate, session: AsyncSession = Depends(get_session)) -> SavedSearch:
    user = await get_or_create_demo_user(session)
    saved = SavedSearch(
        user_id=user.id,
        name=payload.name,
        criteria=payload.criteria.model_dump(mode="json"),
        alerts_enabled=payload.alerts_enabled,
    )
    session.add(saved)
    await session.commit()
    await session.refresh(saved)
    return saved


@router.get("", response_model=list[SavedSearchRead])
async def list_saved_searches(session: AsyncSession = Depends(get_session)) -> list[SavedSearch]:
    user = await get_or_create_demo_user(session)
    return (
        await session.scalars(
            select(SavedSearch)
            .where(SavedSearch.user_id == user.id)
            .order_by(SavedSearch.updated_at.desc())
        )
    ).all()


@router.put("/{saved_search_id}", response_model=SavedSearchRead)
async def update_saved_search(
    saved_search_id: str,
    payload: SavedSearchUpdate,
    session: AsyncSession = Depends(get_session),
) -> SavedSearch:
    saved = await session.get(SavedSearch, saved_search_id)
    if not saved:
        raise ApiError(404, "SAVED_SEARCH_NOT_FOUND", "The saved search was not found.")
    if payload.name is not None:
        saved.name = payload.name
    if payload.criteria is not None:
        saved.criteria = payload.criteria.model_dump(mode="json")
    if payload.alerts_enabled is not None:
        saved.alerts_enabled = payload.alerts_enabled
    await session.commit()
    await session.refresh(saved)
    return saved


@router.delete("/{saved_search_id}")
async def delete_saved_search(saved_search_id: str, session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    saved = await session.get(SavedSearch, saved_search_id)
    if not saved:
        raise ApiError(404, "SAVED_SEARCH_NOT_FOUND", "The saved search was not found.")
    await session.delete(saved)
    await session.commit()
    return {"message": "deleted"}

