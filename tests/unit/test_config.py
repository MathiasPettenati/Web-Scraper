from __future__ import annotations

import os
from unittest.mock import patch

from app.core.config import Settings


def test_settings_default_to_sqlite_database_url() -> None:
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()

    assert settings.database_url.startswith("sqlite")
