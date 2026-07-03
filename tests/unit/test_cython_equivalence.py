from __future__ import annotations

import pytest

from app.scoring import loader, python_engine


def test_loader_falls_back_or_uses_cython() -> None:
    assert loader.engine_name in {"python", "cython"}
    assert loader.normalize_text("Cotton Jacket") == "cotton jacket"


def test_cython_matches_python_when_compiled() -> None:
    cython_engine = pytest.importorskip("app.scoring.cython_engine")
    assert cython_engine.normalize_text("Waxed Jacket") == python_engine.normalize_text("Waxed Jacket")
    assert cython_engine.keyword_match_score("olive jacket", ["olive"], []) == python_engine.keyword_match_score(
        "olive jacket",
        ["olive"],
        [],
    )
    assert cython_engine.size_match_score(["M", "L"], ["S", "L"]) == python_engine.size_match_score(
        ["M", "L"],
        ["S", "L"],
    )
    assert cython_engine.calculate_deal_score(20, 80, 100, 5, 1, 1, 1, 1, 1, True) == python_engine.calculate_deal_score(
        20,
        80,
        100,
        5,
        1,
        1,
        1,
        1,
        1,
        True,
    )

