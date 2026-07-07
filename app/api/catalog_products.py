from __future__ import annotations

from html import escape

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.core.brand_catalog import product_image_url


router = APIRouter()


@router.get("/{product_ref}", response_class=HTMLResponse)
def catalog_product_page(
    product_ref: str,
    brand: str = "",
    title: str = "",
    category: str = "",
    color: str = "",
) -> HTMLResponse:
    safe_brand = escape(brand or "Catalog product")
    safe_title = escape(title or product_ref.replace("-", " ").title())
    safe_category = escape(category or "Product")
    safe_color = escape(color or "Neutral")
    image_src = product_image_url(category, color, brand, title)
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{safe_title}</title>
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
      @media (max-width: 760px) {{ main {{ grid-template-columns: 1fr; }} }}
    </style>
  </head>
  <body>
    <main>
      <img src="{image_src}" alt="{safe_title}">
      <section>
        <div class="meta">{safe_brand}</div>
        <h1>{safe_title}</h1>
        <p>{safe_category} - {safe_color}</p>
        <p>This is the direct product page for the normalized demo listing.</p>
      </section>
    </main>
  </body>
</html>"""
    return HTMLResponse(html)
