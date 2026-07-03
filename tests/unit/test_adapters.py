from __future__ import annotations

import pytest

from app.retailers import ScrapeContext
from app.retailers.demo_chic import DemoChicAdapter
from app.retailers.demo_outlet import DemoOutletAdapter
from app.schemas.search import SearchCriteria


@pytest.mark.asyncio
async def test_demo_chic_parses_fixture_cards() -> None:
    products = await DemoChicAdapter().search(SearchCriteria(search_phrase="jacket"), ScrapeContext())
    assert products
    assert products[0].retailer == "Demo Chic"
    assert products[0].sale_price > 0
    assert "M" in products[0].available_sizes


@pytest.mark.asyncio
async def test_demo_outlet_parses_json_ld_fixture() -> None:
    products = await DemoOutletAdapter().search(SearchCriteria(search_phrase="jacket"), ScrapeContext())
    assert products
    assert products[0].retailer_product_id == "do-2001"
    assert products[0].brand == "Northline"
    assert products[0].in_stock is True

