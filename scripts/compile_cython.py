from __future__ import annotations

import subprocess
import sys


def main() -> int:
    try:
        import Cython  # noqa: F401
    except ImportError:
        print("Cython is not installed. Install the dev extra first: pip install -e \".[dev]\"")
        return 1
    command = [sys.executable, "setup.py", "build_ext", "--inplace"]
    env = dict(**__import__("os").environ, REQUIRE_CYTHON_BUILD="1")
    return subprocess.call(command, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
