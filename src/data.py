# src/data.py

from __future__ import annotations

from typing import Any

import pandas as pd

import duckdb

from src.constants.paths import FEATURES_PATH, TARGETS_PATH

from src.constants.paths import PARQUET_PATH 


DEADLINE_PRESSURE_MAP: dict[str, int] = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
}


def load_dashboard_data() -> pd.DataFrame:
    """
    Load, merge, and preprocess the dashboard dataset.

    The function reads the feature and target CSV files, merges them on
    ``Employee_ID``, and creates derived columns used throughout the app.

    Returns
    -------
    pandas.DataFrame
        Employee-level dataset containing original columns and derived
        dashboard variables.

    Notes
    -----
    Derived columns created:
    - ``workload_score``
    - ``workload_band``
    - ``ai_band``
    """
    features = pd.read_csv(FEATURES_PATH)
    targets = pd.read_csv(TARGETS_PATH)

    df = features.merge(targets, on="Employee_ID")

    df["workload_score"] = (
        df["manual_work_hours_per_week"]
        + df["meeting_hours_per_week"]
        + df["deadline_pressure_level"].map(DEADLINE_PRESSURE_MAP)
    )

    df["workload_band"] = pd.qcut(
        df["workload_score"],
        q=3,
        labels=["Low", "Medium", "High"],
    )

    df["ai_band"] = pd.qcut(
        df["ai_tool_usage_hours_per_week"],
        q=3,
        labels=["Low", "Moderate", "High"],
    )

    return df


def get_filter_choices(df: pd.DataFrame) -> dict[str, list[Any]]:
    """
    Build sidebar filter choices from the preprocessed dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        Preprocessed dashboard dataset.

    Returns
    -------
    dict[str, list[Any]]
        Dictionary containing choice lists for dashboard filter inputs.
    """
    return {
        "job_role_choices": ["All"] + sorted(df["job_role"].dropna().unique().tolist()),
        "ai_band_choices": ["All"]
        + sorted(df["ai_band"].dropna().astype(str).unique().tolist()),
        "deadline_choices": sorted(
            df["deadline_pressure_level"].dropna().unique().tolist()
        ),
    }


def get_slider_ranges(df: pd.DataFrame) -> dict[str, tuple[int, int]]:
    """
    Compute min-max ranges for numeric slider inputs.

    Parameters
    ----------
    df : pandas.DataFrame
        Preprocessed dashboard dataset.

    Returns
    -------
    dict[str, tuple[int, int]]
        Dictionary mapping slider input names to ``(min, max)`` tuples.
    """
    return {
        "experience": (
            int(df["experience_years"].min()),
            int(df["experience_years"].max()),
        ),
        "ai_usage": (
            int(df["ai_tool_usage_hours_per_week"].min()),
            int(df["ai_tool_usage_hours_per_week"].max()),
        ),
        "manual_hours": (
            int(df["manual_work_hours_per_week"].min()),
            int(df["manual_work_hours_per_week"].max()),
        ),
        "tasks_automated": (
            int(df["tasks_automated_percent"].min()),
            int(df["tasks_automated_percent"].max()),
        ),
    }


def get_baselines(df: pd.DataFrame) -> dict[str, float]:
    """
    Compute company-wide baseline metrics used across dashboard outputs.

    Parameters
    ----------
    df : pandas.DataFrame
        Preprocessed dashboard dataset.

    Returns
    -------
    dict[str, float]
        Dictionary of baseline summary statistics for KPI cards and
        reference lines in plots.
    """
    return {
        "median_burnout": float(df["burnout_risk_score"].median()),
        "median_productivity": float(df["productivity_score"].median()),
        "median_wlb": float(df["work_life_balance_score"].median()),
        "high_burnout_rate": float((df["burnout_risk_level"] == "High").mean()),
    }