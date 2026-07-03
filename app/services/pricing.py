from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


MONEY = Decimal("0.01")


def money(value: Decimal | int | float | str | None) -> Decimal:
    if value is None:
        return Decimal("0.00")
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def calculate_total_price(sale_price: Decimal, shipping_price: Decimal | None) -> Decimal:
    return money(sale_price) + money(shipping_price)


def calculate_discount_percent(original_price: Decimal | None, sale_price: Decimal) -> float | None:
    if original_price is None or original_price <= 0:
        return None
    discount = (money(original_price) - money(sale_price)) / money(original_price) * Decimal("100")
    return round(max(float(discount), 0.0), 2)

