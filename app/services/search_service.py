from __future__ import annotations

import asyncio
from decimal import Decimal
from statistics import median

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models import PriceHistory, Product, Retailer, RetailerHealthStatus, SearchCriteriaRecord, SearchJob, SearchResult
from app.models.common import utc_now
from app.retailers import RetailerUnavailable, ScrapeContext, ScrapedProduct
from app.scoring import calculate_deal_score, keyword_match_score, normalize_text, size_match_score, title_similarity
from app.schemas.search import SearchCriteria, SortMethod
from app.services.pricing import calculate_discount_percent, calculate_total_price, money
from app.services.retailer_registry import enabled_adapters_for_search


logger = get_logger(__name__)
DEAL_FEED_TERMS = {"all", "deal", "deals", "sale", "sales"}


async def create_search_job(
    session: AsyncSession,
    criteria: SearchCriteria,
    user_id: str | None = None,
) -> SearchJob:
    record = SearchCriteriaRecord(user_id=user_id, criteria=criteria.model_dump(mode="json"))
    session.add(record)
    await session.flush()
    job = SearchJob(user_id=user_id, criteria_id=record.id, status="queued", message="Queued")
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


def dispatch_search_job(search_id: str) -> None:
    settings = get_settings()
    if settings.use_celery:
        from app.workers.tasks import run_search_job_task

        run_search_job_task.delay(search_id)
    else:
        asyncio.create_task(run_search_job(search_id))


async def cancel_search_job(session: AsyncSession, search_id: str) -> SearchJob | None:
    job = await session.get(SearchJob, search_id)
    if not job:
        return None
    job.cancel_requested = True
    if job.status in {"queued", "running"}:
        job.message = "Cancellation requested"
    await session.commit()
    await session.refresh(job)
    return job


async def run_search_job(search_id: str) -> None:
    from app.database.session import async_session_maker

    async with async_session_maker() as session:
        job = await session.get(SearchJob, search_id, options=[selectinload(SearchJob.criteria_record)])
        if not job or not job.criteria_record:
            return
        criteria = SearchCriteria.model_validate(job.criteria_record.criteria)
        adapters = await enabled_adapters_for_search(session, criteria)
        job.status = "running"
        job.started_at = utc_now()
        job.message = "Searching retailers"
        job.total_retailers = len(adapters)
        job.completed_retailers = 0
        job.products_found = 0
        await session.commit()

        context = ScrapeContext()
        retailer_errors: list[dict[str, object]] = []
        saved_products: list[Product] = []
        all_scraped_products: list[ScrapedProduct] = []
        try:
            for adapter in adapters:
                await session.refresh(job)
                if job.cancel_requested:
                    job.status = "cancelled"
                    job.message = "Search cancelled"
                    job.completed_at = utc_now()
                    await session.commit()
                    return
                try:
                    scraped_products = await adapter.search(criteria, context)
                    all_scraped_products.extend(scraped_products)
                    job.completed_retailers += 1
                    job.products_found = len(all_scraped_products)
                    await mark_retailer_success(session, adapter.retailer_slug)
                    await session.commit()
                except RetailerUnavailable as exc:
                    error = {
                        "retailer": exc.retailer,
                        "code": "RETAILER_UNAVAILABLE",
                        "message": exc.message,
                        "details": exc.details,
                    }
                    retailer_errors.append(error)
                    await mark_retailer_failure(session, adapter.retailer_slug, exc.message)
                    job.completed_retailers += 1
                    job.retailer_errors = retailer_errors
                    await session.commit()
                    logger.warning("retailer_unavailable", retailer=exc.retailer, details=exc.details)
                except Exception as exc:
                    error = {
                        "retailer": adapter.retailer_name,
                        "code": "RETAILER_ERROR",
                        "message": "Retailer search failed",
                        "details": {"exception": exc.__class__.__name__},
                    }
                    retailer_errors.append(error)
                    await mark_retailer_failure(session, adapter.retailer_slug, str(exc))
                    job.completed_retailers += 1
                    job.retailer_errors = retailer_errors
                    await session.commit()
                    logger.exception("retailer_failed", retailer=adapter.retailer_name)
            await session.refresh(job)
            if job.cancel_requested:
                job.status = "cancelled"
                job.message = "Search cancelled"
                job.completed_at = utc_now()
                await session.commit()
                return
            for scraped in all_scraped_products:
                reasons = filtering_reasons(scraped, criteria)
                if reasons:
                    continue
                median_price = _median_comparable_total_price(scraped, all_scraped_products)
                product, explanation = await upsert_product(session, scraped, criteria, median_price)
                if _is_duplicate(product, saved_products):
                    continue
                saved_products.append(product)
                result = SearchResult(
                    search_job_id=job.id,
                    product_id=product.id,
                    match_score=product.match_score,
                    deal_score=product.deal_score,
                    filtering_reasons=[],
                    score_explanation=explanation,
                )
                session.add(result)
            job.products_found = len(saved_products)
            await session.commit()
            await rank_results(session, job.id, criteria.sort_method)
            await session.refresh(job)
            if job.cancel_requested:
                job.status = "cancelled"
                job.message = "Search cancelled"
            else:
                job.status = "completed"
                job.message = "Search completed"
            job.retailer_errors = retailer_errors
            job.completed_at = utc_now()
            await session.commit()
        except Exception:
            logger.exception("search_job_failed", search_id=search_id)
            job.status = "failed"
            job.message = "Search failed unexpectedly"
            job.completed_at = utc_now()
            await session.commit()


async def upsert_product(
    session: AsyncSession,
    scraped: ScrapedProduct,
    criteria: SearchCriteria,
    median_price: Decimal | None,
) -> tuple[Product, list[dict[str, object]]]:
    sale_price = money(scraped.sale_price)
    shipping_price = money(scraped.shipping_price)
    total_price = calculate_total_price(sale_price, shipping_price)
    discount_percent = calculate_discount_percent(scraped.original_price, sale_price)
    match_score, explanation = score_product(scraped, criteria, discount_percent, total_price, median_price)
    statement = select(Product).where(Product.retailer == scraped.retailer)
    if scraped.retailer_product_id:
        statement = statement.where(Product.retailer_product_id == scraped.retailer_product_id)
    else:
        statement = statement.where(Product.product_url == scraped.product_url)
    product = await session.scalar(statement)
    if product is None:
        product = Product(retailer=scraped.retailer, retailer_product_id=scraped.retailer_product_id, title=scraped.title)
        session.add(product)
    product.title = scraped.title
    product.description = scraped.description
    product.brand = scraped.brand
    product.category = scraped.category
    product.available_sizes = scraped.available_sizes
    product.colors = scraped.colors
    product.material = scraped.material
    product.condition = scraped.condition
    product.original_price = money(scraped.original_price) if scraped.original_price is not None else None
    product.sale_price = sale_price
    product.shipping_price = shipping_price
    product.total_price = total_price
    product.currency = scraped.currency
    product.discount_percent = discount_percent
    product.product_url = scraped.product_url
    product.image_url = scraped.image_url
    product.in_stock = scraped.in_stock
    product.date_last_checked = utc_now()
    product.match_score = match_score
    product.deal_score = sum(float(item["value"]) for item in explanation)
    product.deal_score = max(min(round(product.deal_score, 2), 100.0), 0.0)
    product.score_explanation = explanation
    await session.flush()
    session.add(
        PriceHistory(
            product_id=product.id,
            sale_price=sale_price,
            shipping_price=shipping_price,
            total_price=total_price,
            currency=scraped.currency,
        )
    )
    return product, explanation


def score_product(
    product: ScrapedProduct,
    criteria: SearchCriteria,
    discount_percent: float | None,
    total_price: Decimal,
    median_price: Decimal | None,
) -> tuple[float, list[dict[str, object]]]:
    requested_sizes = criteria.requested_sizes()
    brand_score = _brand_score(product.brand, criteria.preferred_brands)
    product_size_score = size_match_score(product.available_sizes, requested_sizes)
    color_score = _contains_score(product.colors, criteria.color)
    query_tokens = normalize_text(criteria.search_phrase).split()
    required_keywords = criteria.required_keywords or ([] if set(query_tokens) <= DEAL_FEED_TERMS else query_tokens)
    keyword_score = keyword_match_score(
        " ".join([product.title, product.description or ""]),
        required_keywords,
        criteria.excluded_keywords,
    )
    condition_score = 1.0 if criteria.condition == "any" or product.condition == criteria.condition.value else 0.0
    match_score = round(
        (
            keyword_score * 34
            + brand_score * 18
            + product_size_score * 18
            + color_score * 10
            + condition_score * 8
            + (1 if product.in_stock else 0) * 12
        ),
        2,
    )
    shipping = float(product.shipping_price or Decimal("0"))
    engine_score = calculate_deal_score(
        discount_percent,
        float(total_price),
        float(median_price) if median_price is not None else None,
        shipping,
        brand_score,
        product_size_score,
        color_score,
        keyword_score,
        condition_score,
        product.in_stock,
    )
    explanation = _score_explanation(
        product,
        criteria,
        discount_percent,
        total_price,
        median_price,
        brand_score,
        product_size_score,
        color_score,
        keyword_score,
        condition_score,
        engine_score,
    )
    return match_score, explanation


def _score_explanation(
    product: ScrapedProduct,
    criteria: SearchCriteria,
    discount_percent: float | None,
    total_price: Decimal,
    median_price: Decimal | None,
    brand_score: float,
    product_size_score: float,
    color_score: float,
    keyword_score: float,
    condition_score: float,
    engine_score: float,
) -> list[dict[str, object]]:
    shipping = float(product.shipping_price or Decimal("0"))
    total = max(float(total_price), 0.01)
    discount_component = min(max(discount_percent or 0.0, 0.0) * 0.45, 26.0)
    market_component = 0.0
    if median_price and median_price > 0:
        market_component = max(min((float(median_price) - total) / float(median_price) * 30.0, 24.0), -18.0)
    shipping_penalty = min((max(shipping, 0.0) / total) * 35.0, 14.0)
    confidence_component = 5.0 if product.original_price is not None and median_price else -6.0
    items = [
        {"label": "Good-deal baseline", "value": 18.0},
        {"label": f"{discount_percent or 0:.0f}% listed discount", "value": round(discount_component, 2)},
        {"label": "Total price vs comparable median", "value": round(market_component, 2)},
        {"label": "Brand preference match", "value": round(brand_score * 8.0, 2)},
        {"label": "Size availability match", "value": round(product_size_score * 10.0, 2)},
        {"label": "Color preference match", "value": round(color_score * 4.0, 2)},
        {"label": "Keyword match", "value": round(keyword_score * 8.0, 2)},
        {"label": "Condition preference", "value": round(condition_score * 3.0, 2)},
        {"label": "Stock status", "value": 8.0 if product.in_stock else -35.0},
        {"label": "Shipping burden penalty", "value": -round(shipping_penalty, 2)},
        {"label": "Pricing confidence", "value": confidence_component},
    ]
    if product.original_price is None:
        items.append({"label": "Original price unavailable", "value": -4.0})
    if product.brand is None:
        items.append({"label": "Brand unavailable", "value": -2.0})
    raw = sum(float(item["value"]) for item in items)
    adjustment = round(engine_score - raw, 2)
    if adjustment:
        items.append({"label": "Score bounds adjustment", "value": adjustment})
    return items


def filtering_reasons(product: ScrapedProduct, criteria: SearchCriteria) -> list[str]:
    reasons: list[str] = []
    title_blob = normalize_text(" ".join([product.title, product.description or ""]))
    brand = normalize_text(product.brand or "")
    if criteria.excluded_brands and brand in {normalize_text(item) for item in criteria.excluded_brands}:
        reasons.append("excluded_brand")
    if criteria.garment_category and normalize_text(criteria.garment_category) not in normalize_text(product.category or ""):
        reasons.append("category_mismatch")
    if criteria.in_stock_only and not product.in_stock:
        reasons.append("out_of_stock")
    if criteria.sale_products_only and not (product.original_price and product.original_price > product.sale_price):
        reasons.append("not_on_sale")
    if criteria.free_shipping_only and money(product.shipping_price) > 0:
        reasons.append("shipping_not_free")
    total_price = calculate_total_price(product.sale_price, product.shipping_price)
    if criteria.min_price is not None and total_price < criteria.min_price:
        reasons.append("below_min_price")
    if criteria.max_price is not None and total_price > criteria.max_price:
        reasons.append("above_max_price")
    if criteria.max_shipping_price is not None and money(product.shipping_price) > criteria.max_shipping_price:
        reasons.append("shipping_above_limit")
    discount = calculate_discount_percent(product.original_price, product.sale_price)
    if criteria.min_discount_percentage is not None and (discount or 0) < criteria.min_discount_percentage:
        reasons.append("discount_below_minimum")
    if criteria.condition != "any" and product.condition != criteria.condition.value:
        reasons.append("condition_mismatch")
    if criteria.material and normalize_text(criteria.material) not in normalize_text(product.material or ""):
        reasons.append("material_mismatch")
    if criteria.color and not _contains_score(product.colors, criteria.color):
        reasons.append("color_mismatch")
    if size_match_score(product.available_sizes, criteria.requested_sizes()) == 0:
        reasons.append("size_mismatch")
    if keyword_match_score(title_blob, criteria.required_keywords, criteria.excluded_keywords) == 0 and criteria.required_keywords:
        reasons.append("keyword_mismatch")
    if any(normalize_text(keyword) in title_blob for keyword in criteria.excluded_keywords):
        reasons.append("excluded_keyword")
    return reasons


async def rank_results(session: AsyncSession, job_id: str, sort_method: SortMethod) -> None:
    results = (
        await session.scalars(
            select(SearchResult)
            .where(SearchResult.search_job_id == job_id)
            .options(selectinload(SearchResult.product))
        )
    ).all()
    ranked = sorted(results, key=lambda result: _sort_key(result, sort_method))
    for index, result in enumerate(ranked, start=1):
        result.ranking = index
    await session.commit()


async def mark_retailer_success(session: AsyncSession, slug: str) -> None:
    retailer = await session.scalar(select(Retailer).where(Retailer.slug == slug).options(selectinload(Retailer.health_status)))
    if not retailer:
        return
    health = retailer.health_status or RetailerHealthStatus(retailer_id=retailer.id)
    health.health = "healthy"
    health.error_rate = max(health.error_rate * 0.5, 0.0)
    health.consecutive_failures = 0
    health.last_successful_search = utc_now()
    health.message = None
    session.add(health)


async def mark_retailer_failure(session: AsyncSession, slug: str, message: str) -> None:
    settings = get_settings()
    retailer = await session.scalar(select(Retailer).where(Retailer.slug == slug).options(selectinload(Retailer.health_status)))
    if not retailer:
        return
    health = retailer.health_status or RetailerHealthStatus(retailer_id=retailer.id)
    health.consecutive_failures += 1
    health.error_rate = min(1.0, max(health.error_rate, 0.2) + 0.2)
    health.last_error_at = utc_now()
    health.message = message
    health.health = "disabled" if health.consecutive_failures >= settings.max_retailer_failures else "degraded"
    if health.health == "disabled":
        retailer.enabled = False
    session.add(health)


def _median_comparable_total_price(product: ScrapedProduct, products: list[ScrapedProduct]) -> Decimal | None:
    if not products:
        return None
    comparable = [
        candidate
        for candidate in products
        if candidate.currency == product.currency
        and normalize_text(candidate.category or "") == normalize_text(product.category or "")
        and candidate.in_stock
    ]
    if len(comparable) < 3:
        comparable = [
            candidate
            for candidate in products
            if candidate.currency == product.currency and candidate.in_stock
        ]
    prices = [
        calculate_total_price(candidate.sale_price, candidate.shipping_price)
        for candidate in comparable
        if candidate.sale_price > 0
    ]
    if not prices:
        return None
    return money(median(prices))


def _brand_score(brand: str | None, preferred_brands: list[str]) -> float:
    if not preferred_brands:
        return 1.0
    normalized_brand = normalize_text(brand or "")
    return 1.0 if normalized_brand in {normalize_text(item) for item in preferred_brands} else 0.0


def _contains_score(values: list[str], preferred: str | None) -> float:
    if not preferred:
        return 1.0
    preferred_normalized = normalize_text(preferred)
    return 1.0 if any(preferred_normalized in normalize_text(value) for value in values) else 0.0


def _sort_key(result: SearchResult, sort_method: SortMethod):
    product = result.product
    if sort_method == SortMethod.lowest_total_price:
        return (product.total_price, -result.deal_score)
    if sort_method == SortMethod.highest_discount:
        return (-(product.discount_percent or 0), product.total_price)
    if sort_method == SortMethod.highest_deal_score:
        return (-result.deal_score, -result.match_score)
    if sort_method == SortMethod.lowest_shipping_price:
        return (product.shipping_price or Decimal("0"), product.total_price)
    if sort_method == SortMethod.newest_listing:
        return (-product.date_discovered.timestamp(), -result.deal_score)
    return (-result.match_score, -result.deal_score, product.total_price)


def _is_duplicate(product: Product, existing_products: list[Product]) -> bool:
    for existing in existing_products:
        if product.product_url == existing.product_url:
            return True
        if product.brand and existing.brand and normalize_text(product.brand) != normalize_text(existing.brand):
            continue
        if title_similarity(product.title, existing.title) > 0.94 and abs(product.total_price - existing.total_price) <= Decimal("2.00"):
            return True
    return False
