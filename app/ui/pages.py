from __future__ import annotations

from decimal import Decimal

from nicegui import ui
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.session import async_session_maker
from app.core.brand_catalog import BRAND_NAMES
from app.models import Product, Retailer, SavedSearch, SearchJob, SearchResult, UserFavorite
from app.schemas.search import SearchCriteria, SortMethod
from app.services.search_service import cancel_search_job, create_search_job, dispatch_search_job
from app.services.users import get_or_create_demo_user
from app.ui.theme import apply_theme


CATEGORIES = [
    "Jackets",
    "Hoodies",
    "Shirts",
    "T-shirts",
    "Jeans",
    "Trousers",
    "Shorts",
    "Shoes",
    "Sneakers",
    "Dresses",
    "Sweaters",
    "Coats",
    "Accessories",
]

CONDITIONS = ["any", "new", "used", "refurbished"]
SORT_LABELS = {
    "Best match": SortMethod.best_match,
    "Lowest total price": SortMethod.lowest_total_price,
    "Highest discount": SortMethod.highest_discount,
    "Highest deal score": SortMethod.highest_deal_score,
    "Lowest shipping price": SortMethod.lowest_shipping_price,
    "Newest listing": SortMethod.newest_listing,
}


def register_pages() -> None:
    @ui.page("/")
    async def dashboard() -> None:
        apply_theme()
        dark = ui.dark_mode()
        retailers = await _retailer_options()
        async with async_session_maker() as session:
            recent = (
                await session.scalars(select(SearchJob).order_by(SearchJob.created_at.desc()).limit(5))
            ).all()
            saved = (
                await session.scalars(select(SavedSearch).order_by(SavedSearch.updated_at.desc()).limit(5))
            ).all()
            favorites = (
                await session.scalars(
                    select(UserFavorite).options(selectinload(UserFavorite.product)).order_by(UserFavorite.created_at.desc()).limit(4)
                )
            ).all()
            deals = (
                await session.scalars(select(Product).order_by(Product.deal_score.desc()).limit(4))
            ).all()
        with ui.element("main").classes("app-shell"):
            _topbar(dark)
            with ui.element("div").classes("content-grid"):
                with ui.element("section").classes("surface section-pad"):
                    ui.label("Garment Search").classes("section-title")
                    await _search_form(retailers)
                with ui.element("aside").classes("surface section-pad"):
                    ui.label("Recent Searches").classes("section-title")
                    if recent:
                        for job in recent:
                            ui.link(f"{job.status.title()} - {job.products_found} products", f"/search/{job.id}").classes("block muted")
                    else:
                        ui.label("No searches yet.").classes("muted")
                    ui.separator().classes("q-my-md")
                    ui.label("Saved Searches").classes("section-title")
                    if saved:
                        for preset in saved:
                            ui.link(preset.name, "/saved-searches").classes("block muted")
                    else:
                        ui.label("No saved presets.").classes("muted")
                    ui.separator().classes("q-my-md")
                    ui.label("Favorites").classes("section-title")
                    if favorites:
                        for favorite in favorites:
                            ui.link(favorite.product.title, f"/products/{favorite.product.id}").classes("block muted")
                    else:
                        ui.label("No favorites yet.").classes("muted")
                    ui.separator().classes("q-my-md")
                    ui.label("Recently Discovered Deals").classes("section-title")
                    if deals:
                        for product in deals:
                            ui.link(f"{product.title} - {_money(product.total_price)}", f"/products/{product.id}").classes("block muted")
                    else:
                        ui.label("No products discovered.").classes("muted")

    @ui.page("/search/{search_id}")
    async def results_page(search_id: str) -> None:
        apply_theme()
        dark = ui.dark_mode()
        with ui.element("main").classes("app-shell"):
            _topbar(dark)
            with ui.row().classes("items-center justify-between q-mt-lg"):
                with ui.column().classes("gap-1"):
                    ui.label("Search Results").classes("section-title")
                    status = ui.label("Loading search...").classes("muted")
                    progress = ui.linear_progress(value=0).classes("w-80")
                async def cancel_click() -> None:
                    await _cancel_from_ui(search_id)

                cancel_button = ui.button(icon="cancel", on_click=cancel_click).props("outline round").tooltip("Cancel search")
            with ui.element("div").classes("results-layout"):
                with ui.element("aside").classes("surface section-pad"):
                    ui.label("Filters").classes("section-title")
                    max_total = ui.number("Max total", min=0, step=1)
                    in_stock = ui.checkbox("In stock", value=False)
                    free_ship = ui.checkbox("Free shipping", value=False)
                    ui.label("Sort").classes("q-mt-md")
                    sort_select = ui.select(list(SORT_LABELS.keys()), value="Best match").classes("w-full")
                    ui.label("Display").classes("q-mt-md")
                    view_mode = ui.toggle(["Grid", "List"], value="Grid")
                    active_filters = ui.element("div").classes("pill-row q-mt-md")
                with ui.element("section"):
                    summary = ui.label("").classes("muted q-mb-sm")
                    error_box = ui.element("div").classes("q-mb-md")
                    results_container = ui.element("div").classes("results-grid")
                    empty = ui.element("div").classes("empty-state")
                    with empty:
                        ui.label("Results will appear as retailers finish.")
                        ui.element("div").classes("skeleton q-mt-md")

            async def refresh() -> None:
                async with async_session_maker() as session:
                    job = await session.get(SearchJob, search_id)
                    if not job:
                        status.set_text("Search not found.")
                        empty.set_visibility(True)
                        return
                    completed = job.completed_retailers
                    total = max(job.total_retailers, 1)
                    progress.value = min(completed / total, 1)
                    status.set_text(
                        f"{job.status.title()} - {completed}/{job.total_retailers} retailers - {job.products_found} products"
                    )
                    summary.set_text("Prices and availability may have changed since the last check.")
                    cancel_button.set_visibility(job.status in {"queued", "running"})
                    results = (
                        await session.scalars(
                            select(SearchResult)
                            .where(SearchResult.search_job_id == search_id)
                            .options(selectinload(SearchResult.product))
                            .order_by(SearchResult.ranking)
                        )
                    ).all()
                    filtered = _filter_ui_results(results, max_total.value, in_stock.value, free_ship.value)
                    filtered = _sort_ui_results(filtered, sort_select.value)
                    results_container.classes(replace="results-grid" if view_mode.value == "Grid" else "results-list")
                    results_container.clear()
                    active_filters.clear()
                    with active_filters:
                        if max_total.value is not None:
                            ui.label(f"Max {_money(Decimal(str(max_total.value)))}").classes("pill")
                        if in_stock.value:
                            ui.label("In stock").classes("pill")
                        if free_ship.value:
                            ui.label("Free shipping").classes("pill")
                    error_box.clear()
                    with error_box:
                        for error in job.retailer_errors:
                            ui.label(f"{error['retailer']}: {error['message']}").classes("text-negative")
                    empty.set_visibility(not filtered)
                    with results_container:
                        for result in filtered:
                            await _product_card(result.product, result.score_explanation)
                    if job.status in {"completed", "cancelled", "failed"}:
                        timer.active = False

            timer = ui.timer(1.4, refresh)
            max_total.on_value_change(lambda _: timer.activate())
            in_stock.on_value_change(lambda _: timer.activate())
            free_ship.on_value_change(lambda _: timer.activate())
            sort_select.on_value_change(lambda _: timer.activate())
            view_mode.on_value_change(lambda _: timer.activate())

    @ui.page("/products/{product_id}")
    async def product_details(product_id: str) -> None:
        apply_theme()
        dark = ui.dark_mode()
        async with async_session_maker() as session:
            product = await session.get(Product, product_id, options=[selectinload(Product.price_history)])
            products = (await session.scalars(select(Product))).all()
        with ui.element("main").classes("app-shell"):
            _topbar(dark)
            if not product:
                ui.label("Product not found.").classes("empty-state q-mt-lg")
                return
            with ui.element("section").classes("surface section-pad q-mt-lg"):
                with ui.grid(columns=2).classes("gap-6"):
                    ui.image(product.image_url or "").classes("product-image")
                    with ui.column().classes("gap-3"):
                        ui.label(product.title).classes("text-h4")
                        ui.label(f"{product.retailer} - {product.brand or 'Unknown brand'}").classes("muted")
                        ui.label(_money(product.total_price)).classes("price-main")
                        ui.label(f"Sale {_money(product.sale_price)} - Shipping {_money(product.shipping_price)}").classes("muted")
                        ui.label(f"Match {product.match_score:.0f} - Deal {product.deal_score:.0f}").classes("score")
                        with ui.row().classes("pill-row"):
                            for size in product.available_sizes:
                                ui.label(size).classes("pill")
                        ui.link("Find this item", product.product_url, new_tab=True).classes("q-mt-sm")
                ui.separator().classes("q-my-lg")
                with ui.grid(columns=2).classes("gap-6"):
                    with ui.column():
                        ui.label("Score Explanation").classes("section-title")
                        for item in product.score_explanation:
                            ui.label(f"{item['label']}: {item['value']:+.1f}")
                    with ui.column():
                        ui.label("Price History").classes("section-title")
                        for point in product.price_history:
                            ui.label(f"{point.observed_at:%Y-%m-%d %H:%M} - {_money(point.total_price)}").classes("muted")
                ui.separator().classes("q-my-lg")
                ui.label("Similar Listings").classes("section-title")
                with ui.element("div").classes("results-grid"):
                    for similar in _similar_products(product, products):
                        await _product_card(similar, similar.score_explanation)

    @ui.page("/saved-searches")
    async def saved_searches_page() -> None:
        apply_theme()
        dark = ui.dark_mode()
        retailers = await _retailer_options()
        async with async_session_maker() as session:
            saved = (await session.scalars(select(SavedSearch).order_by(SavedSearch.updated_at.desc()))).all()
        with ui.element("main").classes("app-shell"):
            _topbar(dark)
            with ui.element("div").classes("content-grid"):
                with ui.element("section").classes("surface section-pad"):
                    ui.label("Create Preset").classes("section-title")
                    await _search_form(retailers, save_mode=True)
                with ui.element("aside").classes("surface section-pad"):
                    ui.label("Saved Searches").classes("section-title")
                    if not saved:
                        ui.label("No saved presets.").classes("muted")
                    for preset in saved:
                        async def run_preset(p=preset) -> None:
                            await _run_saved_search(p)

                        async def delete_preset(p=preset) -> None:
                            await _delete_saved_search(p.id)

                        with ui.row().classes("items-center justify-between full-width"):
                            ui.label(preset.name)
                            with ui.row():
                                ui.button(icon="play_arrow", on_click=run_preset).props("flat round").tooltip("Run saved search")
                                ui.button(icon="edit", on_click=lambda p=preset: _edit_saved_search_dialog(p)).props("flat round").tooltip("Edit")
                                ui.button(icon="delete", on_click=delete_preset).props("flat round color=negative").tooltip("Delete")
                        ui.label("Alerts on" if preset.alerts_enabled else "Alerts off").classes("muted")
                        ui.separator().classes("q-my-sm")

    @ui.page("/retailers")
    async def retailer_status_page() -> None:
        apply_theme()
        dark = ui.dark_mode()
        async with async_session_maker() as session:
            retailers = (
                await session.scalars(select(Retailer).options(selectinload(Retailer.health_status)).order_by(Retailer.name))
            ).all()
        with ui.element("main").classes("app-shell"):
            _topbar(dark)
            ui.label("Retailer Status").classes("section-title q-mt-lg")
            with ui.element("div").classes("results-grid"):
                for retailer in retailers:
                    health = retailer.health_status
                    with ui.element("article").classes("surface section-pad"):
                        ui.label(retailer.name).classes("product-title")
                        ui.label("Enabled" if retailer.enabled else "Disabled").classes("muted")
                        ui.label(f"Health: {health.health if health else 'unknown'}").classes("score")
                        if health:
                            ui.label(f"Error rate: {health.error_rate:.0%}").classes("muted")
                            ui.label(f"Last success: {_dt(health.last_successful_search)}").classes("muted")
                            ui.label(health.message or "").classes("text-negative")


def _topbar(dark) -> None:
    with ui.element("header").classes("topbar"):
        with ui.element("div").classes("brand-lockup"):
            ui.element("div").classes("brand-mark")
            ui.label("Garment Deal Finder").classes("brand-title")
        with ui.element("nav").classes("nav-row"):
            ui.link("Dashboard", "/")
            ui.link("Saved", "/saved-searches")
            ui.link("Retailers", "/retailers")
            ui.button(icon="dark_mode", on_click=dark.toggle).props("flat round").tooltip("Toggle dark mode")


async def _search_form(retailers: dict[str, str], save_mode: bool = False) -> None:
    with ui.element("div").classes("form-grid"):
        search_phrase = ui.input("Search phrase", value="deals").classes("full")
        garment_category = ui.select(["Any"] + CATEGORIES, label="Category", value="Any").classes("wide")
        preferred_brands = ui.select(list(BRAND_NAMES), label="Preferred brands", multiple=True).classes("wide")
        excluded_brands = ui.select(list(BRAND_NAMES), label="Excluded brands", multiple=True).classes("wide")
        size = ui.input("Size", value="")
        alternative_sizes = ui.input("Alternative sizes", placeholder="L, 40")
        color = ui.input("Color", value="")
        material = ui.input("Material", value="")
        condition = ui.select(CONDITIONS, label="Condition", value="any")
        min_price = ui.number("Min price", min=0, step=1)
        max_price = ui.number("Max price", min=0, step=1)
        min_discount = ui.number("Min discount %", min=0, max=100, step=1)
        max_shipping = ui.number("Max shipping", min=0, step=1)
        delivery_region = ui.input("Delivery region", value="US")
        preferred_currency = ui.input("Currency", value="USD")
        include_retailers = ui.select(retailers, label="Include retailers", multiple=True).classes("wide")
        exclude_retailers = ui.select(retailers, label="Exclude retailers", multiple=True).classes("wide")
        required_keywords = ui.input("Required keywords", placeholder="waterproof, cotton").classes("wide")
        excluded_keywords = ui.input("Excluded keywords", placeholder="damaged").classes("wide")
        sort_method = ui.select(list(SORT_LABELS.keys()), label="Sort", value="Best match").classes("wide")
        with ui.element("div").classes("toggle-grid full"):
            in_stock_only = ui.checkbox("In stock only", value=True)
            sale_products_only = ui.checkbox("Sale only")
            free_shipping_only = ui.checkbox("Free shipping only")
        preset_name = ui.input("Preset name", value="My jacket search").classes("wide") if save_mode else None

    async def submit() -> None:
        try:
            criteria = SearchCriteria(
                search_phrase=search_phrase.value,
                garment_category=None if garment_category.value == "Any" else garment_category.value,
                preferred_brands=preferred_brands.value,
                excluded_brands=excluded_brands.value,
                size=size.value or None,
                alternative_sizes=alternative_sizes.value,
                color=color.value or None,
                material=material.value or None,
                condition=condition.value,
                min_price=_decimal_or_none(min_price.value),
                max_price=_decimal_or_none(max_price.value),
                min_discount_percentage=float(min_discount.value) if min_discount.value is not None else None,
                max_shipping_price=_decimal_or_none(max_shipping.value),
                delivery_region=delivery_region.value,
                preferred_currency=preferred_currency.value,
                retailers_to_include=include_retailers.value or [],
                retailers_to_exclude=exclude_retailers.value or [],
                required_keywords=required_keywords.value,
                excluded_keywords=excluded_keywords.value,
                in_stock_only=in_stock_only.value,
                sale_products_only=sale_products_only.value,
                free_shipping_only=free_shipping_only.value,
                sort_method=SORT_LABELS[sort_method.value],
            )
        except ValidationError as exc:
            ui.notify(str(exc), color="negative")
            return
        async with async_session_maker() as session:
            user = await get_or_create_demo_user(session)
            if save_mode:
                saved = SavedSearch(
                    user_id=user.id,
                    name=preset_name.value if preset_name else "Saved search",
                    criteria=criteria.model_dump(mode="json"),
                    alerts_enabled=True,
                )
                session.add(saved)
                await session.commit()
                ui.notify("Saved search created")
                ui.navigate.to("/saved-searches")
            else:
                job = await create_search_job(session, criteria, user.id)
                dispatch_search_job(job.id)
                ui.navigate.to(f"/search/{job.id}")

    ui.button("Save Preset" if save_mode else "Search Deals", on_click=submit).props("color=primary unelevated").classes("q-mt-md")


async def _product_card(product: Product, explanation: list[dict[str, object]]) -> None:
    with ui.element("article").classes("product-card"):
        ui.image(product.image_url or "").classes("product-image")
        with ui.element("div").classes("product-body"):
            ui.label(product.title).classes("product-title")
            ui.label(f"{product.retailer} - {product.brand or 'Unknown brand'}").classes("muted")
            with ui.element("div").classes("price-row"):
                ui.label(_money(product.total_price)).classes("price-main")
                if product.original_price:
                    ui.label(_money(product.original_price)).classes("price-old")
                ui.label(f"Ship {_money(product.shipping_price)}").classes("muted")
            with ui.element("div").classes("score-row"):
                ui.label(f"Match {product.match_score:.0f}").classes("score")
                ui.label(f"Deal {product.deal_score:.0f}").classes("score")
                if product.discount_percent is not None:
                    ui.label(f"{product.discount_percent:.0f}% off").classes("pill")
            with ui.element("div").classes("pill-row"):
                for size in product.available_sizes[:6]:
                    ui.label(size).classes("pill")
                if product.in_stock:
                    ui.label("In stock").classes("pill")
            ui.label(f"Last checked {_dt(product.date_last_checked)}").classes("muted")
            with ui.row().classes("items-center justify-between"):
                async def favorite_click(p=product) -> None:
                    await _favorite(p.id)

                ui.button(icon="favorite_border", on_click=favorite_click).props("flat round").tooltip("Favorite")
                ui.button("Why this score?", on_click=lambda e=explanation: _score_dialog(e)).props("outline dense")
                ui.link("Find this item", product.product_url, new_tab=True)


def _score_dialog(explanation: list[dict[str, object]]) -> None:
    with ui.dialog() as dialog, ui.card().classes("surface"):
        ui.label("Score Breakdown").classes("section-title")
        for item in explanation:
            ui.label(f"{item['label']}: {float(item['value']):+.1f}")
        ui.label("Deal scores are estimates from listing data, not guarantees.").classes("muted")
        ui.button("Close", on_click=dialog.close)
    dialog.open()


async def _favorite(product_id: str) -> None:
    async with async_session_maker() as session:
        user = await get_or_create_demo_user(session)
        exists = await session.scalar(
            select(UserFavorite).where(UserFavorite.user_id == user.id, UserFavorite.product_id == product_id)
        )
        if not exists:
            session.add(UserFavorite(user_id=user.id, product_id=product_id))
            await session.commit()
    ui.notify("Favorited")


async def _cancel_from_ui(search_id: str) -> None:
    async with async_session_maker() as session:
        await cancel_search_job(session, search_id)
    ui.notify("Cancellation requested")


async def _retailer_options() -> dict[str, str]:
    async with async_session_maker() as session:
        retailers = (await session.scalars(select(Retailer).order_by(Retailer.name))).all()
    return {retailer.slug: retailer.name for retailer in retailers if retailer.enabled}


async def _run_saved_search(preset: SavedSearch) -> None:
    criteria = SearchCriteria.model_validate(preset.criteria)
    async with async_session_maker() as session:
        user = await get_or_create_demo_user(session)
        job = await create_search_job(session, criteria, user.id)
        dispatch_search_job(job.id)
    ui.navigate.to(f"/search/{job.id}")


def _edit_saved_search_dialog(preset: SavedSearch) -> None:
    with ui.dialog() as dialog, ui.card().classes("surface"):
        name = ui.input("Name", value=preset.name)
        alerts = ui.checkbox("Alerts enabled", value=preset.alerts_enabled)

        async def save() -> None:
            async with async_session_maker() as session:
                saved = await session.get(SavedSearch, preset.id)
                if saved:
                    saved.name = name.value
                    saved.alerts_enabled = alerts.value
                    await session.commit()
            dialog.close()
            ui.navigate.reload()

        ui.button("Save", on_click=save)
    dialog.open()


async def _delete_saved_search(saved_search_id: str) -> None:
    async with async_session_maker() as session:
        saved = await session.get(SavedSearch, saved_search_id)
        if saved:
            await session.delete(saved)
            await session.commit()
    ui.navigate.reload()


def _filter_ui_results(results: list[SearchResult], max_total: object, in_stock: bool, free_ship: bool) -> list[SearchResult]:
    filtered: list[SearchResult] = []
    for result in results:
        product = result.product
        if max_total is not None and product.total_price > Decimal(str(max_total)):
            continue
        if in_stock and not product.in_stock:
            continue
        if free_ship and (product.shipping_price or Decimal("0")) > 0:
            continue
        filtered.append(result)
    return filtered


def _sort_ui_results(results: list[SearchResult], label: str) -> list[SearchResult]:
    method = SORT_LABELS.get(label, SortMethod.best_match)
    if method == SortMethod.lowest_total_price:
        return sorted(results, key=lambda result: result.product.total_price)
    if method == SortMethod.highest_discount:
        return sorted(results, key=lambda result: -(result.product.discount_percent or 0))
    if method == SortMethod.highest_deal_score:
        return sorted(results, key=lambda result: -result.deal_score)
    if method == SortMethod.lowest_shipping_price:
        return sorted(results, key=lambda result: result.product.shipping_price or Decimal("0"))
    if method == SortMethod.newest_listing:
        return sorted(results, key=lambda result: result.product.date_discovered, reverse=True)
    return sorted(results, key=lambda result: result.ranking)


def _similar_products(product: Product, products: list[Product]) -> list[Product]:
    from app.scoring import title_similarity

    candidates = [candidate for candidate in products if candidate.id != product.id]
    return sorted(candidates, key=lambda candidate: title_similarity(product.title, candidate.title), reverse=True)[:4]


def _decimal_or_none(value: object) -> Decimal | None:
    if value in {None, ""}:
        return None
    return Decimal(str(value))


def _money(value: object) -> str:
    if value is None:
        value = Decimal("0.00")
    return f"${Decimal(str(value)):.2f}"


def _dt(value) -> str:
    return value.strftime("%Y-%m-%d %H:%M") if value else "Never"
