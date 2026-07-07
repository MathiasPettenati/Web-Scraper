from __future__ import annotations

from html import escape

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.samples.products import get_products
from app.schemas.deals import DealFilterRequest, NearbyLocationRequest
from app.services.deals import filter_products, get_country_options, get_filters, paginate

router = APIRouter()


@router.get("/deals")
def list_deals(request: DealFilterRequest = None):
    if request is None:
        request = DealFilterRequest()
    products = get_products()
    filtered = filter_products(
        products,
        query=request.query,
        country=request.country,
        category=request.category,
        brand=request.brand,
        size=request.size,
        color=request.color,
        price_min=request.price_min,
        price_max=request.price_max,
        discount_min=request.discount_min,
        store=request.store,
        condition=request.condition,
        availability=request.availability,
        shipping_max=request.shipping_max,
        sort=request.sort,
    )
    paged_items, page, pages = paginate(filtered, request.page, request.limit)
    return {
        "items": paged_items,
        "page": page,
        "limit": request.limit,
        "total": len(filtered),
        "pages": pages,
    }


@router.get("/deals/filters")
def deal_filters() -> dict[str, list[str]]:
    return get_filters()


@router.get("/deals/featured")
def featured_deals() -> list[dict]:
    products = get_products()
    ranked = filter_products(products, sort="best_deal")[:4]
    return ranked


@router.get("/deals/products/{product_id}/page", response_class=HTMLResponse)
def deal_product_page(product_id: str) -> HTMLResponse:
    products = get_products()
    product = next((candidate for candidate in products if candidate["id"] == product_id), None)
    if not product:
        return HTMLResponse("<h1>Product not found</h1>", status_code=404)

    title = escape(product["title"])
    brand = escape(product["brand"])
    store = escape(product["store"])
    image_url = escape(product["image_url"])
    category = escape(product["category"])
    price = escape(f"{product['currency']} {product['price']}")
    original_price = escape(f"{product['currency']} {product['original_price']}")
    description = escape(product["description"])
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <style>
      * {{ box-sizing: border-box; border-radius: 0 !important; }}
      body {{
        margin: 0;
        min-height: 100vh;
        background: linear-gradient(135deg, #310024 0%, #a0006d 45%, #ff6a00 100%);
        color: #fff7ed;
        font-family: Inter, Arial, sans-serif;
      }}
      main {{
        display: grid;
        gap: 24px;
        grid-template-columns: minmax(280px, 520px) minmax(280px, 1fr);
        max-width: 1040px;
        margin: 0 auto;
        padding: 40px 20px;
      }}
      img {{
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: contain;
        background: linear-gradient(135deg, #fff2d6, #ffb36b);
        border: 1px solid #ff2da8;
      }}
      section {{
        border: 1px solid #ff7a18;
        background: rgba(49, 0, 36, 0.82);
        padding: 24px;
      }}
      p {{ color: #ffd6a5; line-height: 1.6; }}
      .meta {{ color: #ff9f1c; text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.76rem; }}
      .price {{ color: #ff7a18; font-size: 2rem; font-weight: 800; }}
      .old {{ color: #ffb8da; text-decoration: line-through; }}
      @media (max-width: 760px) {{ main {{ grid-template-columns: 1fr; }} }}
    </style>
  </head>
  <body>
    <main>
      <img src="{image_url}" alt="{title}">
      <section>
        <div class="meta">{brand} - {store}</div>
        <h1>{title}</h1>
        <p>{category}</p>
        <p>{description}</p>
        <p class="price">{price}</p>
        <p class="old">{original_price}</p>
      </section>
    </main>
  </body>
</html>"""
    return HTMLResponse(html)


@router.get("/products/{product_id}")
def product_detail(product_id: str) -> dict:
    products = get_products()
    product = next((candidate for candidate in products if candidate["id"] == product_id), None)
    if not product:
        return {"error": "Product not found"}
    product = dict(product)
    product["deal_score"] = 0
    return product


@router.get("/countries")
def country_catalog() -> list[dict[str, str]]:
    return get_country_options()


@router.post("/geo/nearby")
def nearby_stores(request: NearbyLocationRequest) -> dict[str, object]:
    return {
        "message": "Location permission was granted and nearby retailers were prepared.",
        "country": request.country or "United States",
        "nearby_stores": [
            {"name": "Downtown Pickup Hub", "distance_km": 3.2, "city": "Seattle"},
            {"name": "Local Retail Annex", "distance_km": 5.8, "city": "Bellevue"},
        ],
    }
