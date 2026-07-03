from __future__ import annotations

from decimal import Decimal

from app.scoring.python_engine import (
    calculate_deal_score,
    keyword_match_score,
    normalize_text,
    size_match_score,
    title_similarity,
)
from app.services.pricing import calculate_discount_percent, calculate_total_price, money


def test_currency_safe_total_and_discount() -> None:
    assert money("10.005") == Decimal("10.01")
    assert calculate_total_price(Decimal("79.99"), Decimal("4.50")) == Decimal("84.49")
    assert calculate_discount_percent(Decimal("100.00"), Decimal("75.00")) == 25.0


def test_text_keyword_size_and_similarity_scoring() -> None:
    assert normalize_text("Waxed-Cotton Jacket!") == "waxed cotton jacket"
    assert keyword_match_score("Olive waxed cotton jacket", ["olive", "cotton"], []) == 1.0
    assert keyword_match_score("Olive waxed cotton jacket", ["olive"], ["damaged"]) == 1.0
    assert keyword_match_score("Damaged cotton jacket", ["cotton"], ["damaged"]) == 0.0
    assert size_match_score(["M", "L"], ["M"]) == 1.0
    assert size_match_score(["L"], ["M", "L"]) == 0.75
    assert title_similarity("Northline Rain Shell Jacket", "Northline packable rain shell") > 0.6


def test_deal_score_uses_independent_components() -> None:
    high = calculate_deal_score(40, 80, 120, 0, 1, 1, 1, 1, 1, True)
    low = calculate_deal_score(0, 120, 100, 15, 0, 0, 0, 0, 1, True)
    high_shipping = calculate_deal_score(40, 80, 120, 40, 1, 1, 1, 1, 1, True)
    assert high > low
    assert high > high_shipping
    assert 0 <= low <= 100
