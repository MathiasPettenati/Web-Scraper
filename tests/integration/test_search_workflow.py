from __future__ import annotations

from sqlalchemy import select

from app.models import Product, Retailer, SearchJob, SearchResult
from app.schemas.search import SearchCriteria, SortMethod
from app.services.search_service import cancel_search_job, create_search_job, run_search_job
from app.services.users import get_or_create_demo_user


async def test_background_search_finds_scores_and_ranks_products(db_session) -> None:
    user = await get_or_create_demo_user(db_session)
    criteria = SearchCriteria(
        search_phrase="jacket",
        garment_category="Jackets",
        preferred_brands=["Northline"],
        size="M",
        max_price=250,
        sort_method=SortMethod.highest_deal_score,
    )
    job = await create_search_job(db_session, criteria, user.id)

    await run_search_job(job.id)

    refreshed = await db_session.get(SearchJob, job.id)
    await db_session.refresh(refreshed)
    results = (
        await db_session.scalars(
            select(SearchResult).where(SearchResult.search_job_id == job.id).order_by(SearchResult.ranking)
        )
    ).all()
    products = (await db_session.scalars(select(Product))).all()

    assert refreshed.status == "completed"
    assert refreshed.completed_retailers == 2
    assert refreshed.products_found >= 2
    assert results[0].ranking == 1
    assert results[0].deal_score > 0
    assert results[0].score_explanation
    assert all(product.total_price == product.sale_price + product.shipping_price for product in products)
    assert all("demo.local" not in product.product_url for product in products)


async def test_failed_retailer_does_not_break_search(db_session) -> None:
    broken = await db_session.scalar(select(Retailer).where(Retailer.slug == "demo-broken"))
    broken.enabled = True
    await db_session.commit()
    user = await get_or_create_demo_user(db_session)
    criteria = SearchCriteria(
        search_phrase="jacket",
        retailers_to_include=["demo-chic", "demo-broken"],
    )
    job = await create_search_job(db_session, criteria, user.id)

    await run_search_job(job.id)

    refreshed = await db_session.get(SearchJob, job.id)
    await db_session.refresh(refreshed)
    assert refreshed.status == "completed"
    assert refreshed.products_found > 0
    assert refreshed.retailer_errors[0]["code"] == "RETAILER_UNAVAILABLE"


async def test_search_cancellation(db_session) -> None:
    user = await get_or_create_demo_user(db_session)
    job = await create_search_job(db_session, SearchCriteria(search_phrase="jacket"), user.id)
    await cancel_search_job(db_session, job.id)

    await run_search_job(job.id)

    refreshed = await db_session.get(SearchJob, job.id)
    await db_session.refresh(refreshed)
    assert refreshed.status == "cancelled"


async def test_requested_brand_catalog_product_flows_through_search(db_session) -> None:
    user = await get_or_create_demo_user(db_session)
    criteria = SearchCriteria(search_phrase="Burberry", preferred_brands=["Burberry"], size="M")
    job = await create_search_job(db_session, criteria, user.id)

    await run_search_job(job.id)

    results = (
        await db_session.scalars(
            select(SearchResult).where(SearchResult.search_job_id == job.id).order_by(SearchResult.ranking)
        )
    ).all()
    assert results
    product = await db_session.get(Product, results[0].product_id)
    assert product.brand == "Burberry"
    assert product.deal_score > 0
    assert product.product_url.startswith("/api/catalog-products/")
    assert "google.com/search" not in product.product_url


async def test_default_deal_feed_returns_many_good_deals(db_session) -> None:
    user = await get_or_create_demo_user(db_session)
    criteria = SearchCriteria(search_phrase="deals", sort_method=SortMethod.highest_deal_score)
    job = await create_search_job(db_session, criteria, user.id)

    await run_search_job(job.id)

    refreshed = await db_session.get(SearchJob, job.id)
    await db_session.refresh(refreshed)
    results = (
        await db_session.scalars(
            select(SearchResult).where(SearchResult.search_job_id == job.id).order_by(SearchResult.ranking)
        )
    ).all()
    assert refreshed.status == "completed"
    assert refreshed.products_found >= 1600
    assert len(results) >= 1600
    assert results[0].deal_score >= results[-1].deal_score
    assert any(item["label"] == "Total price vs comparable median" for item in results[0].score_explanation)
