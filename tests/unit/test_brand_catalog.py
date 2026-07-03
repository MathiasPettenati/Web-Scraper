from __future__ import annotations

import pytest

from collections import Counter

from app.core.brand_catalog import BRAND_CATALOG, BRAND_NAMES, PRODUCTS_PER_BRAND, catalog_products_for_retailer
from app.retailers import ScrapeContext
from app.retailers.demo_chic import DemoChicAdapter
from app.retailers.demo_outlet import DemoOutletAdapter
from app.schemas.search import SearchCriteria


def test_brand_catalog_contains_requested_50_brands() -> None:
    assert len(BRAND_CATALOG) == 50 * PRODUCTS_PER_BRAND
    assert len(set(BRAND_NAMES)) == 50
    assert Counter(item.brand for item in BRAND_CATALOG) == Counter({brand: PRODUCTS_PER_BRAND for brand in BRAND_NAMES})
    for brand in [
        "Zara",
        "Nike",
        "Abercrombie & Fitch",
        "Victoria's Secret",
        "Macy's",
        "Chanel",
        "Hermes",
        "Hugo Boss",
    ]:
        assert brand in BRAND_NAMES


def test_catalog_is_split_across_two_demo_retailers() -> None:
    chic_products = catalog_products_for_retailer("Demo Chic", "demo-chic")
    outlet_products = catalog_products_for_retailer("Demo Outlet", "demo-outlet")

    assert len(chic_products) == 750
    assert len(outlet_products) == 750
    assert {product.brand for product in chic_products + outlet_products} == set(BRAND_NAMES)
    assert all(product.product_url.startswith("https://www.google.com/search?tbm=shop&q=") for product in chic_products)
    assert all(product.product_url.startswith("https://www.google.com/search?tbm=shop&q=") for product in outlet_products)
    assert all(product.image_url and product.image_url.startswith("/api/catalog-images/product.svg?") for product in chic_products)
    assert all(product.image_url and product.image_url.startswith("/api/catalog-images/product.svg?") for product in outlet_products)


@pytest.mark.asyncio
async def test_demo_adapters_search_catalog_brands() -> None:
    context = ScrapeContext()
    chic_results = await DemoChicAdapter().search(SearchCriteria(search_phrase="Hermes"), context)
    outlet_results = await DemoOutletAdapter().search(SearchCriteria(search_phrase="Chanel"), context)

    assert len(chic_results) == PRODUCTS_PER_BRAND // 2
    assert len(outlet_results) == PRODUCTS_PER_BRAND // 2
    assert {product.brand for product in chic_results} == {"Hermes"}
    assert {product.brand for product in outlet_results} == {"Chanel"}


@pytest.mark.asyncio
async def test_demo_adapters_return_working_find_links_for_fixture_products() -> None:
    context = ScrapeContext()
    products = await DemoChicAdapter().search(SearchCriteria(search_phrase="Northline"), context)

    assert products
    assert all("demo.local" not in product.product_url for product in products)
    assert all(product.product_url.startswith("https://www.google.com/search?tbm=shop&q=") for product in products)
    assert all(product.image_url and product.image_url.startswith("/api/catalog-images/product.svg?") for product in products)
