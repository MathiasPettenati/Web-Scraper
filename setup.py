from __future__ import annotations

import os

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


REQUIRE_CYTHON_BUILD = os.environ.get("REQUIRE_CYTHON_BUILD") == "1"


class OptionalBuildExt(build_ext):
    def run(self):
        try:
            super().run()
        except Exception as exc:
            if REQUIRE_CYTHON_BUILD:
                raise
            print(f"warning: Cython scoring extension was not built: {exc}")

    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except Exception as exc:
            if REQUIRE_CYTHON_BUILD:
                raise
            print(f"warning: optional extension {ext.name} was skipped: {exc}")

try:
    from Cython.Build import cythonize
except ImportError:
    if REQUIRE_CYTHON_BUILD:
        raise
    ext_modules = []
else:
    ext_modules = cythonize(
        [
            Extension(
                "app.scoring.cython_engine",
                ["app/scoring/cython_engine.pyx"],
            )
        ],
        compiler_directives={"language_level": "3"},
    )


setup(ext_modules=ext_modules, cmdclass={"build_ext": OptionalBuildExt})
