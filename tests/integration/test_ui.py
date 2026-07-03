from __future__ import annotations

import asyncio


async def test_nicegui_dashboard_page_loads(api_client) -> None:
    from nicegui import core

    core.loop = asyncio.get_running_loop()
    response = await api_client.get("/")
    assert response.status_code == 200
    assert "Garment Deal Finder" in response.text
