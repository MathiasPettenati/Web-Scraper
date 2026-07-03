from __future__ import annotations

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_garment.sqlite3"
os.environ["USE_CELERY"] = "false"
os.environ["AUTO_CREATE_TABLES"] = "false"
os.environ["NICEGUI_STORAGE_SECRET"] = "test-storage-secret"

import pytest
from httpx import ASGITransport, AsyncClient

from app.database.base import Base
from app.database.init_db import seed_database
from app.database.session import async_session_maker, engine
from app.main import app


@pytest.fixture(autouse=True)
async def reset_database():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        await seed_database(session)
    yield


@pytest.fixture
async def db_session():
    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def api_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

