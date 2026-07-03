from __future__ import annotations

from decimal import Decimal

from bs4 import BeautifulSoup

from app.core.brand_catalog import catalog_products_for_retailer, product_image_url, shopping_search_url
from app.retailers.base import RetailerAdapter, ScrapeContext, ScrapedProduct
from app.scoring import normalize_text


class DemoChicAdapter(RetailerAdapter):
    retailer_name = "Demo Chic"
    retailer_slug = "demo-chic"
    base_url = "fixture://demo-chic"

    async def search(self, query, context: ScrapeContext) -> list[ScrapedProduct]:
        html = context.load_fixture("demo_chic.html")
        soup = BeautifulSoup(html, "html.parser")
        products = [await self.parse_product(card) for card in soup.select("[data-product-card]")]
        products.extend(catalog_products_for_retailer(self.retailer_name, self.retailer_slug))
        return [product for product in products if _matches_query(product, query.search_phrase)]

    async def parse_product(self, raw_product: object) -> ScrapedProduct:
        card = raw_product
        sizes = _csv(card.get("data-sizes", ""))
        colors = _csv(card.get("data-colors", ""))
        return ScrapedProduct(
            retailer=self.retailer_name,
            retailer_product_id=card.get("data-id"),
            title=_text(card, ".title"),
            description=_text(card, ".description") or None,
            brand=card.get("data-brand"),
            category=card.get("data-category"),
            available_sizes=sizes,
            colors=colors,
            material=card.get("data-material"),
            condition=card.get("data-condition", "new"),
            original_price=_decimal(card.get("data-original-price")),
            sale_price=_decimal(card.get("data-sale-price")) or Decimal("0.00"),
            shipping_price=_decimal(card.get("data-shipping-price")),
            currency=card.get("data-currency", "USD"),
            product_url=shopping_search_url(_text(card, ".title"), card.get("data-brand")),
            image_url=product_image_url(card.get("data-category"), colors[0] if colors else None, card.get("data-brand"), _text(card, ".title")),
            in_stock=card.get("data-stock", "in").lower() == "in",
        )


def _text(card, selector: str) -> str:
    element = card.select_one(selector)
    return element.get_text(" ", strip=True) if element else ""


def _csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _decimal(value: str | None) -> Decimal | None:
    if value in {None, ""}:
        return None
    return Decimal(value.replace("$", "").strip())


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
