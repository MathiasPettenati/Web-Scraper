from __future__ import annotations

import json
from decimal import Decimal

from bs4 import BeautifulSoup

from app.core.brand_catalog import catalog_products_for_retailer, product_detail_url, product_image_url
from app.retailers.base import RetailerAdapter, ScrapeContext, ScrapedProduct
from app.scoring import normalize_text


class DemoOutletAdapter(RetailerAdapter):
    retailer_name = "Demo Outlet"
    retailer_slug = "demo-outlet"
    base_url = "fixture://demo-outlet"

    async def search(self, query, context: ScrapeContext) -> list[ScrapedProduct]:
        html = context.load_fixture("demo_outlet.html")
        soup = BeautifulSoup(html, "html.parser")
        raw_products = json.loads(soup.select_one("#products-jsonld").string)
        products = [await self.parse_product(raw_product) for raw_product in raw_products["itemListElement"]]
        products.extend(catalog_products_for_retailer(self.retailer_name, self.retailer_slug))
        return [product for product in products if _matches_query(product, query.search_phrase)]

    async def parse_product(self, raw_product: object) -> ScrapedProduct:
        product = raw_product["item"]
        offer = product["offers"]
        title = product["name"]
        brand = product.get("brand", {}).get("name")
        category = product.get("category")
        colors = product.get("color", [])
        return ScrapedProduct(
            retailer=self.retailer_name,
            retailer_product_id=product.get("sku"),
            title=title,
            description=product.get("description"),
            brand=brand,
            category=category,
            available_sizes=product.get("size", []),
            colors=colors,
            material=product.get("material"),
            condition=product.get("itemCondition", "new").split("/")[-1].lower(),
            original_price=_maybe_decimal(product.get("highPrice")),
            sale_price=Decimal(str(offer["price"])),
            shipping_price=Decimal(str(offer.get("shippingDetails", {}).get("shippingRate", {}).get("value", 0))),
            currency=offer.get("priceCurrency", "USD"),
            product_url=product_detail_url(
                retailer_product_id=product.get("sku") or "demo-outlet-product",
                title=title,
                brand=brand,
                category=category,
                color=(colors or [None])[0],
            ),
            image_url=product_image_url(
                category,
                (colors or [None])[0],
                brand,
                title,
            ),
            in_stock=offer.get("availability", "").endswith("InStock"),
        )


def _maybe_decimal(value: object) -> Decimal | None:
    if value in {None, ""}:
        return None
    return Decimal(str(value))


def _matches_query(product: ScrapedProduct, phrase: str) -> bool:
    normalized_phrase = normalize_text(phrase)
    if normalized_phrase in {"", "all", "deal", "deals", "sale", "sales"}:
        return True
    haystack = normalize_text(
        " ".join(
            [
                product.title,
                product.description or "",
                product.brand or "",
                product.category or "",
                product.material or "",
            ]
        )
    )
    return all(token in haystack for token in normalized_phrase.split())
