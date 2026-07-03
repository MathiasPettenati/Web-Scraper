from __future__ import annotations

from app.retailers.base import RetailerAdapter, RetailerUnavailable


class DemoBrokenAdapter(RetailerAdapter):
    retailer_name = "Demo Broken"
    retailer_slug = "demo-broken"
    base_url = "fixture://demo-broken"
    enabled_by_default = False

    async def search(self, query, context):
        raise RetailerUnavailable(
            self.retailer_name,
            "Demo adapter is intentionally unavailable",
            {"reason": "fixture failure"},
        )

    async def parse_product(self, raw_product):
        raise RetailerUnavailable(self.retailer_name, "No product can be parsed")

