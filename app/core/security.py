from __future__ import annotations

from ipaddress import ip_address
from urllib.parse import urlparse

from pydantic import AnyUrl, TypeAdapter, ValidationError


URL_ADAPTER = TypeAdapter(AnyUrl)


class UnsafeUrlError(ValueError):
    pass


def validate_external_url(url: str, allowed_hosts: list[str] | None = None) -> str:
    try:
        URL_ADAPTER.validate_python(url)
    except ValidationError as exc:
        raise UnsafeUrlError("Invalid URL") from exc

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeUrlError("Only HTTP and HTTPS URLs are allowed")
    if not parsed.hostname:
        raise UnsafeUrlError("URL host is required")
    if _is_private_host(parsed.hostname):
        raise UnsafeUrlError("Private network URLs are not allowed")
    if allowed_hosts and parsed.hostname not in allowed_hosts:
        raise UnsafeUrlError("URL host is not on the approved list")
    return url


def validate_adapter_url(url: str) -> str:
    if url.startswith("fixture://"):
        return url
    return validate_external_url(url)


def _is_private_host(hostname: str) -> bool:
    try:
        addr = ip_address(hostname)
    except ValueError:
        return hostname in {"localhost"} or hostname.endswith(".local")
    return addr.is_private or addr.is_loopback or addr.is_link_local

