from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.search import SearchCriteria, SortMethod


def test_search_criteria_splits_comma_lists_and_uppercases_currency() -> None:
    criteria = SearchCriteria(
        search_phrase="waxed jacket",
        preferred_brands="Northline, Aster",
        alternative_sizes="M, L",
        required_keywords="cotton, olive",
        preferred_currency="usd",
        sort_method=SortMethod.highest_deal_score,
    )

    assert criteria.preferred_brands == ["Northline", "Aster"]
    assert criteria.alternative_sizes == ["M", "L"]
    assert criteria.required_keywords == ["cotton", "olive"]
    assert criteria.preferred_currency == "USD"


def test_search_criteria_rejects_invalid_price_range() -> None:
    with pytest.raises(ValidationError):
        SearchCriteria(search_phrase="hoodie", min_price=Decimal("100"), max_price=Decimal("20"))


def test_search_criteria_rejects_overlapping_retailers() -> None:
    with pytest.raises(ValidationError):
        SearchCriteria(
            search_phrase="sneaker",
            retailers_to_include=["demo-chic"],
            retailers_to_exclude=["demo-chic"],
        )

