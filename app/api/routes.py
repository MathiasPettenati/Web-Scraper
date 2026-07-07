from __future__ import annotations

from fastapi import APIRouter

from app.api import catalog_images, deals, favorites, health, products, retailers, saved_searches, searches


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(searches.router, prefix="/api/searches", tags=["searches"])
api_router.include_router(catalog_images.router, prefix="/api/catalog-images", tags=["catalog-images"])
api_router.include_router(products.router, prefix="/api/products", tags=["products"])
api_router.include_router(retailers.router, prefix="/api/retailers", tags=["retailers"])
api_router.include_router(saved_searches.router, prefix="/api/saved-searches", tags=["saved-searches"])
api_router.include_router(favorites.router, prefix="/api/favorites", tags=["favorites"])
api_router.include_router(deals.router, prefix="/api", tags=["deals"])
