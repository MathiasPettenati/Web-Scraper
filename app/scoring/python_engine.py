from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher


WORD_RE = re.compile(r"[a-z0-9]+")


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(WORD_RE.findall(ascii_text.lower()))


def keyword_match_score(title: str, required: list[str], excluded: list[str]) -> float:
    haystack = normalize_text(title)
    if not haystack:
        return 0.0
    for keyword in excluded:
        if normalize_text(keyword) in haystack:
            return 0.0
    if not required:
        return 1.0
    matches = sum(1 for keyword in required if normalize_text(keyword) in haystack)
    return matches / len(required)


def size_match_score(product_sizes: list[str], requested_sizes: list[str]) -> float:
    if not requested_sizes:
        return 1.0
    normalized_product = {normalize_text(size) for size in product_sizes}
    normalized_requested = [normalize_text(size) for size in requested_sizes]
    if not normalized_product:
        return 0.0
    if normalized_requested[0] in normalized_product:
        return 1.0
    if any(size in normalized_product for size in normalized_requested[1:]):
        return 0.75
    if any(_compatible_size(size, normalized_product) for size in normalized_requested):
        return 0.35
    return 0.0


def calculate_deal_score(
    discount_percent: float | None,
    sale_price: float,
    median_price: float | None,
    shipping_price: float,
    brand_score: float,
    size_score: float,
    color_score: float,
    keyword_score: float,
    condition_score: float,
    in_stock: bool,
) -> float:
    total_price = max(sale_price, 0.01)
    discount_component = min(max(discount_percent or 0.0, 0.0) * 0.45, 26.0)
    market_component = 0.0
    if median_price and median_price > 0:
        market_component = max(min((median_price - total_price) / median_price * 30.0, 24.0), -18.0)
    preference_component = (
        brand_score * 8.0
        + size_score * 10.0
        + color_score * 4.0
        + keyword_score * 8.0
        + condition_score * 3.0
    )
    shipping_penalty = min((max(shipping_price, 0.0) / total_price) * 35.0, 14.0)
    confidence_component = 5.0 if discount_percent is not None and median_price else -6.0
    stock_component = 8.0 if in_stock else -35.0
    score = (
        18.0
        + discount_component
        + market_component
        + preference_component
        + confidence_component
        + stock_component
        - shipping_penalty
    )
    return round(max(min(score, 100.0), 0.0), 2)


def title_similarity(first: str, second: str) -> float:
    first_normalized = normalize_text(first)
    second_normalized = normalize_text(second)
    if not first_normalized or not second_normalized:
        return 0.0
    return SequenceMatcher(None, first_normalized, second_normalized).ratio()


def _compatible_size(size: str, product_sizes: set[str]) -> bool:
    aliases = {
        "extra small": {"xs", "0", "2"},
        "xs": {"extra small", "0", "2"},
        "small": {"s", "4", "6"},
        "s": {"small", "4", "6"},
        "medium": {"m", "8", "10"},
        "m": {"medium", "8", "10"},
        "large": {"l", "12", "14"},
        "l": {"large", "12", "14"},
        "extra large": {"xl", "16", "18"},
        "xl": {"extra large", "16", "18"},
    }
    return bool(aliases.get(size, set()) & product_sizes)
