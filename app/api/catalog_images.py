from __future__ import annotations

from html import escape

from fastapi import APIRouter
from fastapi.responses import Response


router = APIRouter()


COLOR_HEX: dict[str, str] = {
    "black": "#64113f",
    "blue": "#b83280",
    "brown": "#a2412d",
    "camel": "#ff9f1c",
    "champagne": "#ffd08a",
    "charcoal": "#7a174f",
    "cream": "#ffd6a5",
    "emerald": "#ff4fa3",
    "forest": "#c64161",
    "gray": "#ff7a45",
    "grey": "#ff7a45",
    "heather grey": "#ff9a76",
    "honey": "#ff8c1a",
    "indigo": "#8f1d64",
    "ivory": "#ffe1b8",
    "khaki": "#ffb347",
    "natural": "#ffc675",
    "navy": "#5d1049",
    "oat": "#ffd7a8",
    "olive": "#d85a3c",
    "orange": "#ff7a00",
    "rust": "#e94f37",
    "sage": "#f06f7f",
    "sand": "#ffb45f",
    "sky": "#ff8ab3",
    "stone": "#ffa66a",
    "tan": "#ff9f3f",
    "volt": "#ffcf33",
    "washed black": "#7b174f",
    "white": "#fff0d6",
}


@router.get("/product.svg")
def product_svg(category: str = "Jackets", color: str = "Navy", brand: str = "", title: str = "") -> Response:
    svg = render_product_svg(category=category, color=color, brand=brand, title=title)
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=86400"},
    )


def render_product_svg(category: str, color: str, brand: str, title: str) -> str:
    fill = _color_hex(color)
    accent = _accent_color(fill)
    category_label = escape(category or "Product")
    brand_label = escape((brand or "Deal Finder").strip()[:34])
    title_label = escape(_short_title(title or category or "Catalog product"))
    shape = _shape_for_category(category, fill, accent, title)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 900" role="img" aria-label="{brand_label} {title_label} {category_label}">
  <defs>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#4a0832" flood-opacity="0.24"/>
    </filter>
    <linearGradient id="sky" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#ff2da8"/>
      <stop offset="0.52" stop-color="#ff7a18"/>
      <stop offset="1" stop-color="#ffd36a"/>
    </linearGradient>
    <linearGradient id="warm-surface" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#fff2d6"/>
      <stop offset="1" stop-color="#ffd1b8"/>
    </linearGradient>
  </defs>
  <rect width="900" height="900" fill="url(#sky)"/>
  <rect x="92" y="92" width="716" height="716" fill="url(#warm-surface)" stroke="#ff2da8" stroke-width="3"/>
  <g filter="url(#shadow)">
    <rect x="185" y="168" width="530" height="530" fill="#fff3df"/>
    <g transform="translate(0 94)">
    {shape}
    </g>
  </g>
</svg>"""


def _shape_for_category(category: str, fill: str, accent: str, title: str) -> str:
    normalized = (category or "").casefold()
    title_text = (title or "").casefold()
    if normalized in {"t-shirts", "shirts", "hoodies", "sweaters"}:
        return _top_shape(fill, accent, hood=normalized == "hoodies", collar=normalized == "shirts")
    if normalized in {"jackets", "coats"}:
        return _outerwear_shape(fill, accent, long=normalized == "coats")
    if normalized in {"jeans", "trousers"}:
        return _pants_shape(fill, accent, shorts=False)
    if normalized == "shorts":
        return _pants_shape(fill, accent, shorts=True)
    if normalized == "dresses":
        return _dress_shape(fill, accent)
    if normalized in {"sneakers", "shoes"}:
        return _shoe_shape(fill, accent)
    if "belt" in title_text:
        return _belt_shape(fill, accent)
    if "bag" in title_text or "tote" in title_text:
        return _bag_shape(fill, accent)
    return _scarf_shape(fill, accent)


def _top_shape(fill: str, accent: str, hood: bool = False, collar: bool = False) -> str:
    hood_svg = ""
    collar_svg = ""
    if hood:
        hood_svg = f'<path d="M382 135c14-48 122-48 136 0l-31 48h-74z" fill="{accent}" opacity="0.34"/>'
    if collar:
        collar_svg = '<path d="M410 178l40 44 40-44" fill="#ffffff" opacity="0.92"/>'
    return f"""
    <path d="M316 198l-88 64 56 92 54-34v162h224V320l54 34 56-92-88-64-78-34H394z" fill="{fill}"/>
    {hood_svg}
    {collar_svg}
    <path d="M338 482h224" stroke="{accent}" stroke-width="10" opacity="0.45"/>
    <path d="M378 196c33 34 111 34 144 0" stroke="#ffffff" stroke-width="14" stroke-linecap="round" opacity="0.7"/>
    """


def _outerwear_shape(fill: str, accent: str, long: bool = False) -> str:
    bottom = 500 if long else 474
    return f"""
    <path d="M322 178l82-32h92l82 32 74 286-88 24-42-142v{bottom - 346}H378V346l-42 142-88-24z" fill="{fill}"/>
    <path d="M404 146l46 92 46-92" fill="#ffffff" opacity="0.86"/>
    <path d="M450 226v{bottom - 2}" stroke="{accent}" stroke-width="8" opacity="0.65"/>
    <path d="M376 258l-42 62M524 258l42 62" stroke="#ffffff" stroke-width="10" stroke-linecap="round" opacity="0.42"/>
    """


def _pants_shape(fill: str, accent: str, shorts: bool = False) -> str:
    end = 404 if shorts else 502
    return f"""
    <path d="M340 150h220l-24 {end - 150}h-76l-10-172-10 172h-76z" fill="{fill}"/>
    <path d="M340 150h220v54H340z" fill="{accent}" opacity="0.42"/>
    <path d="M450 204v{end}" stroke="#ffffff" stroke-width="9" opacity="0.48"/>
    <path d="M370 {end}h62M468 {end}h62" stroke="{accent}" stroke-width="10" stroke-linecap="round" opacity="0.5"/>
    """


def _dress_shape(fill: str, accent: str) -> str:
    return f"""
    <path d="M402 142h96l52 112 88 238H262l88-238z" fill="{fill}"/>
    <path d="M402 142c18 36 78 36 96 0l26 72H376z" fill="#ffffff" opacity="0.78"/>
    <path d="M334 344h232" stroke="{accent}" stroke-width="14" opacity="0.5"/>
    <path d="M302 492c80-36 216-36 296 0" stroke="#ffffff" stroke-width="12" opacity="0.48"/>
    """


def _shoe_shape(fill: str, accent: str) -> str:
    return f"""
    <path d="M262 360c92 6 126-62 196-110 42 74 100 116 210 122 26 2 43 24 34 50-8 22-28 34-60 34H276c-48 0-70-20-64-54 4-25 20-40 50-42z" fill="{fill}"/>
    <path d="M226 424h476c-8 32-32 48-72 48H284c-38 0-58-16-58-48z" fill="{accent}" opacity="0.55"/>
    <path d="M392 302l92 46M358 330l86 42M504 348l66 28" stroke="#ffffff" stroke-width="13" stroke-linecap="round" opacity="0.72"/>
    """


def _belt_shape(fill: str, accent: str) -> str:
    return f"""
    <rect x="226" y="302" width="448" height="78" rx="22" fill="{fill}"/>
    <rect x="260" y="278" width="112" height="126" rx="16" fill="none" stroke="{accent}" stroke-width="20"/>
    <circle cx="606" cy="341" r="10" fill="#ffffff" opacity="0.82"/>
    <circle cx="558" cy="341" r="10" fill="#ffffff" opacity="0.82"/>
    """


def _bag_shape(fill: str, accent: str) -> str:
    return f"""
    <path d="M318 248h264l44 244H274z" fill="{fill}"/>
    <path d="M370 250c0-76 160-76 160 0" fill="none" stroke="{accent}" stroke-width="24" stroke-linecap="round"/>
    <path d="M318 310h264" stroke="#ffffff" stroke-width="12" opacity="0.46"/>
    """


def _scarf_shape(fill: str, accent: str) -> str:
    return f"""
    <path d="M390 142h120v358l-60-34-60 34z" fill="{fill}"/>
    <path d="M390 226h120M390 310h120M390 394h120" stroke="{accent}" stroke-width="20" opacity="0.48"/>
    <path d="M390 142c60 38 60 78 0 120M510 142c-60 38-60 78 0 120" stroke="#ffffff" stroke-width="11" opacity="0.62"/>
    """


def _color_hex(color: str) -> str:
    normalized = (color or "").strip().casefold()
    return COLOR_HEX.get(normalized, "#ff7a18")


def _accent_color(fill: str) -> str:
    return "#ff2da8" if fill.lower() not in {"#ff2da8", "#ff4fa3", "#fff0d6"} else "#ff7a18"


def _short_title(title: str) -> str:
    words = [word for word in title.split() if word]
    if len(words) <= 5:
        return " ".join(words)
    return " ".join(words[-5:])
