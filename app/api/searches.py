from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import enforce_search_rate_limit
from app.api.errors import ApiError
from app.core.config import get_settings
from app.database.session import get_session
from app.models import SearchJob, SearchResult
from app.schemas.search import SearchCriteria, SearchJobRead, SearchResultWithProduct
from app.services.search_service import cancel_search_job, create_search_job, dispatch_search_job, run_search_job
from app.services.users import get_or_create_demo_user


router = APIRouter()


@router.post("", response_model=SearchJobRead, dependencies=[Depends(enforce_search_rate_limit)])
async def create_search(
    criteria: SearchCriteria,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> SearchJob:
    user = await get_or_create_demo_user(session)
    job = await create_search_job(session, criteria, user.id)
    if get_settings().use_celery:
        dispatch_search_job(job.id)
    else:
        background_tasks.add_task(run_search_job, job.id)
    return job


@router.get("/{search_id}", response_model=SearchJobRead)
async def read_search(search_id: str, session: AsyncSession = Depends(get_session)) -> SearchJob:
    job = await session.get(SearchJob, search_id)
    if not job:
        raise ApiError(404, "SEARCH_NOT_FOUND", "The search job was not found.", {"search_id": search_id})
    return job


@router.get("/{search_id}/results", response_model=list[SearchResultWithProduct])
async def read_search_results(
    search_id: str,
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, object]]:
    job = await session.get(SearchJob, search_id)
    if not job:
        raise ApiError(404, "SEARCH_NOT_FOUND", "The search job was not found.", {"search_id": search_id})
    results = (
        await session.scalars(
            select(SearchResult)
            .where(SearchResult.search_job_id == search_id)
            .options(selectinload(SearchResult.product))
            .order_by(SearchResult.ranking)
        )
    ).all()
    return [{"result": result, "product": result.product} for result in results]


@router.post("/{search_id}/cancel", response_model=SearchJobRead)
async def cancel_search(search_id: str, session: AsyncSession = Depends(get_session)) -> SearchJob:
    job = await cancel_search_job(session, search_id)
    if not job:
        raise ApiError(404, "SEARCH_NOT_FOUND", "The search job was not found.", {"search_id": search_id})
    return job

