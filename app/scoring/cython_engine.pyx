import re
import unicodedata
from difflib import SequenceMatcher


WORD_RE = re.compile(r"[a-z0-9]+")


def normalize_text(str value):
    cdef str normalized = unicodedata.normalize("NFKD", value or "")
    cdef str ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(WORD_RE.findall(ascii_text.lower()))


def keyword_match_score(str title, list required, list excluded):
    cdef str haystack = normalize_text(title)
    cdef object keyword
    cdef int matches = 0
    if not haystack:
        return 0.0
    for keyword in excluded:
        if normalize_text(str(keyword)) in haystack:
            return 0.0
    if not required:
        return 1.0
    for keyword in required:
        if normalize_text(str(keyword)) in haystack:
            matches += 1
    return matches / len(required)


def size_match_score(list product_sizes, list requested_sizes):
    if not requested_sizes:
        return 1.0
    cdef set normalized_product = {normalize_text(str(size)) for size in product_sizes}
    cdef list normalized_requested = [normalize_text(str(size)) for size in requested_sizes]
    cdef object size
    if not normalized_product:
        return 0.0
    if normalized_requested[0] in normalized_product:
        return 1.0
    for size in normalized_requested[1:]:
        if size in normalized_product:
            return 0.75
    for size in normalized_requested:
        if _compatible_size(size, normalized_product):
            return 0.35
    return 0.0


def calculate_deal_score(
    object discount_percent,
    double sale_price,
    object median_price,
    double shipping_price,
    double brand_score,
    double size_score,
    double color_score,
    double keyword_score,
    double condition_score,
    bint in_stock,
):
    cdef double total_price = max(sale_price, 0.01)
    cdef double discount_component = min(max(discount_percent or 0.0, 0.0) * 0.45, 26.0)
    cdef double market_component = 0.0
    cdef double median = float(median_price or 0.0)
    cdef double preference_component
    cdef double shipping_penalty
    cdef double confidence_component
    cdef double stock_component
    cdef double score
    if median > 0:
        market_component = max(min((median - total_price) / median * 30.0, 24.0), -18.0)
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


def title_similarity(str first, str second):
    cdef str first_normalized = normalize_text(first)
    cdef str second_normalized = normalize_text(second)
    if not first_normalized or not second_normalized:
        return 0.0
    return SequenceMatcher(None, first_normalized, second_normalized).ratio()


def _compatible_size(str size, set product_sizes):
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
