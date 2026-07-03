# Architecture

Garment Deal Finder is a single Python application with a FastAPI REST API and a NiceGUI browser UI mounted on the same ASGI app.

## Runtime Components

- FastAPI exposes search, product, retailer, saved-search, favorite, health, and readiness endpoints.
- NiceGUI renders the dashboard, results, product details, saved searches, and retailer health pages.
- SQLAlchemy 2 models store users, saved searches, jobs, criteria, products, results, retailer health, price history, favorites, and alerts.
- PostgreSQL is the production database target. SQLite is supported for local tests and quick non-Docker demos.
- Celery and Redis run background searches in Docker and production-like deployments.
- A local async dispatcher runs searches in-process when `USE_CELERY=false`.
- Retailer adapters implement a shared interface and only search approved configured retailers.
- Scoring is loaded through `app.scoring.loader`, which prefers the compiled Cython module and falls back to pure Python.

## Search Flow

1. The API or UI validates `SearchCriteria`.
2. A `SearchJob` and immutable `SearchCriteriaRecord` are stored.
3. The job is dispatched to Celery or to a local async task.
4. Enabled adapters search fixture-backed retailer pages.
5. Scraped products are normalized, filtered, deduplicated, scored, and saved.
6. `SearchResult` rows connect products to jobs with ranking, scores, filtering reasons, and score explanations.
7. The UI polls job status and renders products as they are saved.
8. Cancellation sets `cancel_requested`; the runner checks it between retailers.

## Scraping Safeguards

Adapters are allowlisted through database records. The demo adapters read local fixtures and do not bypass authentication, CAPTCHAs, rate limits, or anti-bot systems. The shared context supports descriptive user agents, redirects refusal, request delays, and request caching.

## Deal Scoring

The deal score is an estimate built from separate components:

- discount component
- comparable market price component
- brand, size, color, keyword, and condition preference components
- stock component
- shipping and uncertainty penalties

The UI exposes every component in the "Why this score?" dialog.

