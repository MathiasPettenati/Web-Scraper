from __future__ import annotations

from decimal import Decimal

import pytest

from app.models import Product, SearchAlert, User
from app.services.alerts import evaluate_alert
from app.services.notifications import TestNotificationProvider


@pytest.mark.asyncio
async def test_test_notification_provider_records_triggered_alert() -> None:
    user = User(email="shopper@example.com", display_name="Shopper")
    product = Product(
        retailer="Demo Chic",
        retailer_product_id="x",
        title="Northline Jacket",
        sale_price=Decimal("80"),
        shipping_price=Decimal("0"),
        total_price=Decimal("80"),
        currency="USD",
        product_url="https://demo.local/item",
        in_stock=True,
        available_sizes=["M"],
        colors=["Olive"],
    )
    alert = SearchAlert(user_id="u", alert_type="price_below", threshold_value=Decimal("90"))
    provider = TestNotificationProvider()

    triggered = await evaluate_alert(alert, product, user, provider)

    assert triggered is True
    assert provider.sent_messages[0]["recipient"] == "shopper@example.com"

