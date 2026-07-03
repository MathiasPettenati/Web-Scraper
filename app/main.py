from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from nicegui import ui

from app.api.errors import register_error_handlers
from app.api.routes import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.database.init_db import init_database
from app.ui.pages import register_pages


configure_logging()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_create_tables:
        await init_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)
register_error_handlers(app)
app.include_router(api_router)
register_pages()
ui.run_with(
    app,
    mount_path="/",
    storage_secret=settings.nicegui_storage_secret,
    title=settings.app_name,
)

