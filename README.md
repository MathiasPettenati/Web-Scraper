# Garment Deal Finder

A production-style garment deal-finder website built with Python 3.12, FastAPI, NiceGUI, PostgreSQL, SQLAlchemy 2, Alembic, Redis, Celery, BeautifulSoup, HTTPX, Playwright, Cython, and Pytest.

## Quick Start With Docker

```bash
git clone <repository>
cd garment-deal-finder
cp .env.example .env
docker compose up --build
```

Open `http://localhost:8000`.

The Docker stack starts PostgreSQL, Redis, the FastAPI/NiceGUI web app, and a Celery worker. The API container runs Alembic migrations before startup.

## Non-Docker Development

```bash
cd garment-deal-finder
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
python scripts/compile_cython.py
python scripts/run_local.py
```

On Windows PowerShell:

```powershell
cd garment-deal-finder
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python scripts\compile_cython.py
python scripts\run_local.py
```

The local script defaults to SQLite and in-process background jobs. To use local PostgreSQL and Redis, copy `.env.example` to `.env`, update `DATABASE_URL` and `REDIS_URL`, run `alembic upgrade head`, start a worker with:

```bash
celery -A app.workers.celery_app.celery_app worker --loglevel=INFO
```

Then run:

```bash
uvicorn app.main:app --reload --port 8000
```

## Cython Build Notes

The scorer lives in `app/scoring`.

```bash
python scripts/compile_cython.py
```

The loader automatically uses `app.scoring.cython_engine` when it is compiled. If the extension is not available, it falls back to `app.scoring.python_engine`.

Platform notes:

- Windows: install the Microsoft C++ Build Tools for Python extension compilation.
- macOS: install Xcode Command Line Tools with `xcode-select --install`.
- Linux: install a compiler toolchain such as `build-essential` or equivalent.

## Tests

```bash
pytest
```

Tests use local HTML fixtures and do not call live retailer websites.

## API Endpoints

- `POST /api/searches`
- `GET /api/searches/{search_id}`
- `GET /api/searches/{search_id}/results`
- `POST /api/searches/{search_id}/cancel`
- `GET /api/products/{product_id}`
- `GET /api/products/{product_id}/price-history`
- `GET /api/retailers`
- `GET /api/retailers/status`
- `POST /api/saved-searches`
- `GET /api/saved-searches`
- `PUT /api/saved-searches/{saved_search_id}`
- `DELETE /api/saved-searches/{saved_search_id}`
- `POST /api/favorites/{product_id}`
- `DELETE /api/favorites/{product_id}`
- `GET /api/favorites`
- `GET /health/live`
- `GET /health/ready`

Errors use:

```json
{
  "error": {
    "code": "RETAILER_UNAVAILABLE",
    "message": "The retailer could not be searched.",
    "details": {}
  }
}
```

## Demo Retailers

Two enabled adapters are included:

- Demo Chic: parses normal fixture HTML product cards.
- Demo Outlet: parses fixture JSON-LD product data.

`Demo Broken` is disabled by default and is used by tests to prove one failed retailer does not break an entire search.

The demo adapters also include an approved local 60-brand catalog covering Zara, Nike, H&M, Uniqlo, Adidas, Shein, Lululemon, Levi's, Gap, Old Navy, Ralph Lauren, Calvin Klein, Tommy Hilfiger, The North Face, New Balance, Puma, Under Armour, Patagonia, Columbia, Vans, Louis Vuitton, Gucci, Dior, Converse, Skechers, Abercrombie & Fitch, American Eagle, Aritzia, Urban Outfitters, Free People, Anthropologie, Mango, ASOS, Zalando, COS, Massimo Dutti, Bershka, Pull&Bear, Next, Victoria's Secret, JD Sports, Nordstrom, Macy's, Bloomingdale's, TJ Maxx, Chanel, Hermes, Prada, Burberry, Hugo Boss, Coach, Michael Kors, Kate Spade, Reformation, Everlane, Madewell, AllSaints, Alo Yoga, Fabletics, and Dr. Martens. The local database generates 30 product listings per brand, for 1,800 catalog listings total. These are local demonstration listings, not live scrapes from brand websites. The "Find this item" links open direct local product pages for the normalized title and brand so users land on a product detail view instead of a shopping search. Product images are served by the app through local generated catalog-image URLs, so every listing displays a square sunset-toned product image matching its item type without relying on broken external placeholders.

## Security And Scraping Policy

The app does not accept arbitrary websites to scrape. Retailers are configured by administrators through adapter records. Adapters must prefer official APIs or structured product data, use normal HTTP before browser automation, identify themselves with a descriptive user agent, respect delays and request limits, and mark protected or unavailable pages as unavailable.

The project does not bypass CAPTCHAs, authentication, private account pages, rate limits, or anti-bot systems. It does not rotate proxies or purchase products automatically.

## Project Tree

```text
garment-deal-finder/
|-- app/
|   |-- api/
|   |-- core/
|   |-- database/
|   |-- models/
|   |-- schemas/
|   |-- services/
|   |-- retailers/
|   |-- scoring/
|   |-- workers/
|   |-- ui/
|   `-- main.py
|-- migrations/
|-- tests/
|   |-- fixtures/
|   |-- unit/
|   `-- integration/
|-- scripts/
|-- Dockerfile
|-- docker-compose.yml
|-- pyproject.toml
|-- alembic.ini
|-- .env.example
|-- .gitignore
|-- ARCHITECTURE.md
`-- README.md
```
