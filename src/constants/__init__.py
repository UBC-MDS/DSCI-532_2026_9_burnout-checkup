# src/constants/__init__.py
# Marks constants/ as a Python package and (optionally) re-exports commonly used constants for cleaner imports.

from .paths import (
    PROJECT_ROOT,
    DATA_RAW_DIR,
    IMG_DIR,
    REPORTS_DIR,
    FEATURES_PATH,
    TARGETS_PATH,
)

__all__ = [
    "PROJECT_ROOT",
    "DATA_RAW_DIR",
    "IMG_DIR",
    "REPORTS_DIR",
    "FEATURES_PATH",
    "TARGETS_PATH",
]
