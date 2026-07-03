from __future__ import annotations

import asyncio

from app.services.search_service import run_search_job
from app.workers.celery_app import celery_app


@celery_app.task(name="search.run_search_job")
def run_search_job_task(search_id: str) -> str:
    asyncio.run(run_search_job(search_id))
    return search_id

