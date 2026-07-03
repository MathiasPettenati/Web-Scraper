from __future__ import annotations

import os
import subprocess
import sys


def main() -> int:
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./garment_deals.sqlite3")
    os.environ.setdefault("USE_CELERY", "false")
    os.environ.setdefault("AUTO_CREATE_TABLES", "true")
    return subprocess.call([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"])


if __name__ == "__main__":
    raise SystemExit(main())

