# src/constants/paths.py
# Centralizes project file and directory paths (e.g., data, reports, images) to keep imports consistent and avoid hard-coded paths.

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # repo root
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
IMG_DIR = PROJECT_ROOT / "img"
REPORTS_DIR = PROJECT_ROOT / "reports"

FEATURES_PATH = DATA_RAW_DIR / "ai_productivity_features.csv"
TARGETS_PATH = DATA_RAW_DIR / "ai_productivity_targets.csv"
