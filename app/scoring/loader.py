from __future__ import annotations

try:
    from app.scoring import cython_engine as _engine

    engine_name = "cython"
except ImportError:
    from app.scoring import python_engine as _engine

    engine_name = "python"


normalize_text = _engine.normalize_text
keyword_match_score = _engine.keyword_match_score
size_match_score = _engine.size_match_score
calculate_deal_score = _engine.calculate_deal_score
title_similarity = _engine.title_similarity

