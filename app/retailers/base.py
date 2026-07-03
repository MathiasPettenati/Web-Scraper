from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, Field

from app.core.config import get_settings


FIXTURE_DIR = Path(__file__).with_name("fixtures")


class RetailerUnavailable(RuntimeError):
    def __init__(self, retailer: str, message: str, details: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.retailer = retailer
        self.message = message
        self.details = details or {}


class ScrapedProduct(BaseModel):
    retailer: str
    retailer_product_id: str | None = None
    title: str
    description: str | None = None
    brand: str | None = None
    category: str | None = None
    available_sizes: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    material: str | None = None
    condition: str | None = "new"
    original_price: Decimal | None = None
    sale_price: Decimal
    shipping_price: Decimal | None = Decimal("0.00")
    currency: str = "USD"
    product_url: str
    image_url: str | None = None
    in_stock: bool = True
    date_discovered: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    date_last_checked: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScrapeContext:
    def __init__(
        self,
        user_agent: str | None = None,
        request_delay_seconds: float | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        settings = get_settings()
        self.user_agent = user_agent or settings.user_agent
        self.request_delay_seconds = (
            settings.retailer_request_delay_seconds
            if request_delay_seconds is None
            else request_delay_seconds
        )
        self.timeout_seconds = settings.request_timeout_seconds if timeout_seconds is None else timeout_seconds
        self._cache: dict[str, str] = {}
        self._last_request_by_domain: dict[str, float] = {}

    async def fetch_text(self, url: str) -> str:
        if url in self._cache:
            return self._cache[url]
        domain = urlparse(url).netloc
        await self._respect_delay(domain)
        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
            follow_redirects=False,
            headers={"User-Agent": self.user_agent},
        ) as client:
            response = await client.get(url)
            if 300 <= response.status_code < 400:
                raise RetailerUnavailable(domain, "Unsafe redirect was refused", {"status": response.status_code})
            response.raise_for_status()
            self._cache[url] = response.text
            return response.text

    def load_fixture(self, filename: str) -> str:
        path = FIXTURE_DIR / filename
        return path.read_text(encoding="utf-8")

    async def _respect_delay(self, domain: str) -> None:
        if not self.request_delay_seconds:
            return
        now = asyncio.get_running_loop().time()
        previous = self._last_request_by_domain.get(domain, 0.0)
        wait_time = self.request_delay_seconds - (now - previous)
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        self._last_request_by_domain[domain] = asyncio.get_running_loop().time()


class RetailerAdapter(ABC):
    retailer_name: str
    retailer_slug: str
    base_url: str
    enabled_by_default: bool = True

    @abstractmethod
    async def search(self, query, context: ScrapeContext) -> list[ScrapedProduct]:
        raise NotImplementedError

    @abstractmethod
    async def parse_product(self, raw_product: object) -> ScrapedProduct:
        raise NotImplementedError

