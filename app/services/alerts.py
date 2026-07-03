from __future__ import annotations

from app.models import Product, SearchAlert, User
from app.services.notifications import NotificationProvider


async def evaluate_alert(alert: SearchAlert, product: Product, user: User, provider: NotificationProvider) -> bool:
    triggered = False
    if alert.alert_type == "price_below" and alert.threshold_value is not None:
        triggered = product.total_price <= alert.threshold_value
    elif alert.alert_type == "discount_above" and alert.threshold_value is not None:
        triggered = (product.discount_percent or 0) >= float(alert.threshold_value)
    elif alert.alert_type == "size_available" and alert.exact_size:
        triggered = alert.exact_size.lower() in {size.lower() for size in product.available_sizes}
    elif alert.alert_type == "new_listing":
        triggered = True
    if triggered and alert.enabled is not False:
        await provider.send(user.email, "Garment deal alert", f"{product.title} matched your alert.")
    return triggered
