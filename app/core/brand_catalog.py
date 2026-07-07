from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import quote_plus

from app.retailers.base import ScrapedProduct


@dataclass(frozen=True)
class ProductTemplate:
    title: str
    category: str
    material: str
    colors: tuple[str, ...]
    sizes: tuple[str, ...]
    base_price: int


@dataclass(frozen=True)
class BrandCatalogItem:
    index: int
    brand_index: int
    product_index: int
    brand: str
    title: str
    category: str
    material: str
    colors: tuple[str, ...]
    sizes: tuple[str, ...]
    base_price: int


REQUESTED_BRANDS: tuple[str, ...] = (
    "Zara",
    "Nike",
    "H&M",
    "Uniqlo",
    "Adidas",
    "Shein",
    "Lululemon",
    "Levi's",
    "Gap",
    "Old Navy",
    "Ralph Lauren",
    "Calvin Klein",
    "Tommy Hilfiger",
    "The North Face",
    "New Balance",
    "Puma",
    "Under Armour",
    "Patagonia",
    "Columbia",
    "Vans",
    "Louis Vuitton",
    "Gucci",
    "Dior",
    "Converse",
    "Skechers",
    "Abercrombie & Fitch",
    "American Eagle",
    "Aritzia",
    "Urban Outfitters",
    "Free People",
    "Anthropologie",
    "Mango",
    "ASOS",
    "Zalando",
    "COS",
    "Massimo Dutti",
    "Bershka",
    "Pull&Bear",
    "Next",
    "Victoria's Secret",
    "JD Sports",
    "Nordstrom",
    "Macy's",
    "Bloomingdale's",
    "TJ Maxx",
    "Chanel",
    "Hermes",
    "Prada",
    "Burberry",
    "Hugo Boss",
    "Coach",
    "Michael Kors",
    "Kate Spade",
    "Reformation",
    "Everlane",
    "Madewell",
    "AllSaints",
    "Alo Yoga",
    "Fabletics",
    "Dr. Martens",
)


PRODUCT_TEMPLATES: tuple[ProductTemplate, ...] = (
    ProductTemplate("Essential Crew T-Shirt", "T-shirts", "Cotton jersey", ("White", "Black"), ("XS", "S", "M", "L", "XL"), 32),
    ProductTemplate("Graphic Logo T-Shirt", "T-shirts", "Heavy cotton jersey", ("Washed Black", "Ivory"), ("XS", "S", "M", "L", "XL"), 38),
    ProductTemplate("Performance Training T-Shirt", "T-shirts", "Moisture-wicking knit", ("Blue", "Black"), ("S", "M", "L", "XL"), 42),
    ProductTemplate("Oxford Button-Down Shirt", "Shirts", "Oxford cotton", ("White", "Sky"), ("S", "M", "L", "XL"), 74),
    ProductTemplate("Linen Resort Shirt", "Shirts", "Linen", ("Sand", "White"), ("S", "M", "L", "XL"), 82),
    ProductTemplate("Denim Overshirt", "Shirts", "Cotton denim", ("Indigo", "Blue"), ("S", "M", "L", "XL"), 96),
    ProductTemplate("Vintage Soft Hoodie", "Hoodies", "Cotton fleece", ("Heather Grey", "Navy"), ("XS", "S", "M", "L", "XL"), 84),
    ProductTemplate("Zip Fleece Hoodie", "Hoodies", "Brushed fleece", ("Charcoal", "Cream"), ("S", "M", "L", "XL"), 92),
    ProductTemplate("Crewneck Knit Sweater", "Sweaters", "Cotton wool knit", ("Navy", "Camel"), ("XS", "S", "M", "L", "XL"), 118),
    ProductTemplate("Cashmere Crew Sweater", "Sweaters", "Cashmere blend", ("Grey", "Oat"), ("S", "M", "L", "XL"), 168),
    ProductTemplate("Straight Leg Jeans", "Jeans", "Cotton denim", ("Indigo", "Black"), ("28", "29", "30", "31", "32", "34", "36"), 98),
    ProductTemplate("Slim Stretch Jeans", "Jeans", "Stretch denim", ("Blue", "Black"), ("28", "29", "30", "31", "32", "34", "36"), 104),
    ProductTemplate("Relaxed Cargo Trousers", "Trousers", "Cotton ripstop", ("Olive", "Black"), ("S", "M", "L", "XL"), 110),
    ProductTemplate("Tailored Slim Trousers", "Trousers", "Stretch suiting", ("Navy", "Charcoal"), ("30", "32", "34", "36"), 128),
    ProductTemplate("Everyday Chino Shorts", "Shorts", "Cotton twill", ("Khaki", "Stone"), ("30", "32", "34", "36"), 64),
    ProductTemplate("Running Training Shorts", "Shorts", "Performance woven", ("Black", "Volt"), ("S", "M", "L", "XL"), 58),
    ProductTemplate("Lightweight Puffer Jacket", "Jackets", "Recycled nylon", ("Black", "Forest"), ("XS", "S", "M", "L", "XL"), 184),
    ProductTemplate("Denim Trucker Jacket", "Jackets", "Cotton denim", ("Blue", "Black"), ("S", "M", "L", "XL"), 132),
    ProductTemplate("Waterproof Rain Jacket", "Jackets", "Nylon shell", ("Blue", "Black"), ("S", "M", "L", "XL"), 156),
    ProductTemplate("Double Breasted Wool Coat", "Coats", "Wool blend", ("Camel", "Black"), ("XS", "S", "M", "L", "XL"), 260),
    ProductTemplate("Cotton Trench Coat", "Coats", "Cotton gabardine", ("Honey", "Navy"), ("XS", "S", "M", "L", "XL"), 280),
    ProductTemplate("Printed Midi Dress", "Dresses", "Viscose crepe", ("Rust", "Ivory"), ("XS", "S", "M", "L"), 146),
    ProductTemplate("Ribbed Knit Dress", "Dresses", "Ribbed knit", ("Black", "Sage"), ("XS", "S", "M", "L"), 118),
    ProductTemplate("Satin Slip Dress", "Dresses", "Satin", ("Black", "Champagne"), ("XS", "S", "M", "L"), 154),
    ProductTemplate("Low-Top Court Sneaker", "Sneakers", "Leather", ("White", "Grey"), ("7", "8", "9", "10", "11", "12"), 112),
    ProductTemplate("Retro Runner Sneaker", "Sneakers", "Suede and mesh", ("Grey", "White"), ("7", "8", "9", "10", "11", "12"), 126),
    ProductTemplate("Cushioned Walking Shoe", "Shoes", "Engineered mesh", ("Black", "Grey"), ("7", "8", "9", "10", "11", "12"), 104),
    ProductTemplate("Leather Logo Belt", "Accessories", "Leather", ("Black", "Brown"), ("80", "85", "90", "95", "100"), 88),
    ProductTemplate("Structured Tote Bag", "Accessories", "Cotton canvas", ("Natural", "Black"), ("One size",), 128),
    ProductTemplate("Printed Scarf", "Accessories", "Silk twill", ("Orange", "Navy"), ("One size",), 96),
)


BRAND_PRICE_TIERS: dict[str, Decimal] = {
    "Shein": Decimal("0.55"),
    "H&M": Decimal("0.70"),
    "Old Navy": Decimal("0.72"),
    "Bershka": Decimal("0.78"),
    "Pull&Bear": Decimal("0.80"),
    "ASOS": Decimal("0.82"),
    "TJ Maxx": Decimal("0.82"),
    "Zara": Decimal("0.92"),
    "Mango": Decimal("0.98"),
    "Gap": Decimal("0.98"),
    "American Eagle": Decimal("1.00"),
    "Uniqlo": Decimal("1.02"),
    "Urban Outfitters": Decimal("1.08"),
    "Converse": Decimal("1.12"),
    "Vans": Decimal("1.12"),
    "Skechers": Decimal("1.14"),
    "JD Sports": Decimal("1.16"),
    "Columbia": Decimal("1.20"),
    "Nike": Decimal("1.25"),
    "Adidas": Decimal("1.25"),
    "Puma": Decimal("1.22"),
    "Under Armour": Decimal("1.24"),
    "New Balance": Decimal("1.28"),
    "Next": Decimal("1.30"),
    "Abercrombie & Fitch": Decimal("1.34"),
    "Calvin Klein": Decimal("1.36"),
    "Tommy Hilfiger": Decimal("1.38"),
    "Macy's": Decimal("1.40"),
    "Nordstrom": Decimal("1.45"),
    "Ralph Lauren": Decimal("1.55"),
    "The North Face": Decimal("1.58"),
    "Victoria's Secret": Decimal("1.58"),
    "Massimo Dutti": Decimal("1.62"),
    "COS": Decimal("1.65"),
    "Free People": Decimal("1.68"),
    "Anthropologie": Decimal("1.72"),
    "Aritzia": Decimal("1.78"),
    "Bloomingdale's": Decimal("1.90"),
    "Patagonia": Decimal("1.95"),
    "Zalando": Decimal("1.15"),
    "Hugo Boss": Decimal("2.10"),
    "Burberry": Decimal("4.80"),
    "Prada": Decimal("5.60"),
    "Dior": Decimal("6.40"),
    "Gucci": Decimal("6.20"),
    "Louis Vuitton": Decimal("6.60"),
    "Chanel": Decimal("7.20"),
    "Hermes": Decimal("7.40"),
    "Coach": Decimal("2.35"),
    "Michael Kors": Decimal("2.45"),
    "Kate Spade": Decimal("2.30"),
    "Reformation": Decimal("1.85"),
    "Everlane": Decimal("1.22"),
    "Madewell": Decimal("1.28"),
    "AllSaints": Decimal("1.82"),
    "Alo Yoga": Decimal("1.72"),
    "Fabletics": Decimal("1.05"),
    "Dr. Martens": Decimal("1.48"),
}


def _build_catalog() -> tuple[BrandCatalogItem, ...]:
    items: list[BrandCatalogItem] = []
    for brand_index, brand in enumerate(REQUESTED_BRANDS, start=1):
        for product_index, template in enumerate(PRODUCT_TEMPLATES, start=1):
            global_index = (brand_index - 1) * len(PRODUCT_TEMPLATES) + product_index
            items.append(
                BrandCatalogItem(
                    index=global_index,
                    brand_index=brand_index,
                    product_index=product_index,
                    brand=brand,
                    title=f"{brand} {template.title}",
                    category=template.category,
                    material=template.material,
                    colors=template.colors,
                    sizes=template.sizes,
                    base_price=template.base_price,
                )
            )
    return tuple(items)


BRAND_CATALOG: tuple[BrandCatalogItem, ...] = _build_catalog()
BRAND_NAMES: tuple[str, ...] = REQUESTED_BRANDS
PRODUCTS_PER_BRAND = len(PRODUCT_TEMPLATES)


def catalog_products_for_retailer(retailer_name: str, retailer_slug: str) -> list[ScrapedProduct]:
    parity = 1 if retailer_slug == "demo-chic" else 0
    return [
        _catalog_product(item, retailer_name, retailer_slug)
        for item in BRAND_CATALOG
        if item.index % 2 == parity
    ]


def _catalog_product(item: BrandCatalogItem, retailer_name: str, retailer_slug: str) -> ScrapedProduct:
    original_price = _catalog_original_price(item)
    discount = _catalog_discount(item)
    sale_price = _money(original_price * (Decimal("1") - discount))
    shipping_price = _catalog_shipping(item)
    retailer_product_id = f"{retailer_slug}-{item.index:04d}"
    return ScrapedProduct(
        retailer=retailer_name,
        retailer_product_id=retailer_product_id,
        title=item.title,
        description=(
            f"Sale deal listing for {item.brand} {item.category.lower()}; "
            "approved local normalized catalog data only, not a live retailer scrape."
        ),
        brand=item.brand,
        category=item.category,
        available_sizes=list(item.sizes),
        colors=list(item.colors),
        material=item.material,
        condition="new",
        original_price=original_price,
        sale_price=sale_price,
        shipping_price=shipping_price,
        currency="USD",
        product_url=product_detail_url(
            retailer_product_id=retailer_product_id,
            title=item.title,
            brand=item.brand,
            category=item.category,
            color=item.colors[0],
        ),
        image_url=product_image_url(item.category, item.colors[0], item.brand, item.title),
        in_stock=item.index % 17 != 0,
    )


def product_detail_url(
    *,
    retailer_product_id: str,
    title: str,
    brand: str | None = None,
    category: str | None = None,
    color: str | None = None,
) -> str:
    slug = _slug(title)
    query = {
        "brand": brand or "",
        "title": title,
        "category": category or "",
        "color": color or "",
    }
    query_string = "&".join(f"{key}={quote_plus(value)}" for key, value in query.items() if value)
    suffix = f"?{query_string}" if query_string else ""
    return f"/api/catalog-products/{retailer_product_id}-{slug}{suffix}"


def shopping_search_url(title: str, brand: str | None = None) -> str:
    product_id = _slug(" ".join(part for part in [brand or "", title] if part))[:80] or "catalog-product"
    return product_detail_url(retailer_product_id=product_id, title=title, brand=brand)


def product_image_url(category: str | None, color: str | None, brand: str | None, title: str | None) -> str:
    query = {
        "category": category or "Jackets",
        "color": color or "Navy",
        "brand": brand or "",
        "title": title or "",
    }
    return "/api/catalog-images/product.svg?" + "&".join(
        f"{key}={quote_plus(value)}" for key, value in query.items()
    )


def _catalog_original_price(item: BrandCatalogItem) -> Decimal:
    tier = BRAND_PRICE_TIERS.get(item.brand, Decimal("1.00"))
    seasonal_variance = Decimal("1.00") + Decimal(item.product_index % 5) * Decimal("0.045")
    brand_variance = Decimal(item.brand_index % 4) * Decimal("3.00")
    return _money(Decimal(item.base_price) * tier * seasonal_variance + brand_variance)


def _catalog_discount(item: BrandCatalogItem) -> Decimal:
    base_discount = Decimal("0.18") + Decimal((item.index + item.product_index) % 9) * Decimal("0.025")
    if BRAND_PRICE_TIERS.get(item.brand, Decimal("1.00")) >= Decimal("4.00"):
        base_discount -= Decimal("0.04")
    return min(max(base_discount, Decimal("0.12")), Decimal("0.42"))


def _catalog_shipping(item: BrandCatalogItem) -> Decimal:
    tier = BRAND_PRICE_TIERS.get(item.brand, Decimal("1.00"))
    if item.index % 5 == 0 or tier >= Decimal("4.00"):
        return Decimal("0.00")
    return _money(Decimal("4.00") + Decimal(item.product_index % 6) + Decimal(item.brand_index % 3))


def _money(value: int | Decimal) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _slug(value: str) -> str:
    normalized = []
    previous_dash = False
    for character in value.casefold():
        if character.isalnum():
            normalized.append(character)
            previous_dash = False
        elif not previous_dash:
            normalized.append("-")
            previous_dash = True
    return "".join(normalized).strip("-")
