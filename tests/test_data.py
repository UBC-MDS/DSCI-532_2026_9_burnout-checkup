# tests/test_data.py

from __future__ import annotations

import pandas as pd
import pytest

from src.data import (
    DEADLINE_PRESSURE_MAP,
    get_baselines,
    get_filter_choices,
    get_slider_ranges,
    load_dashboard_data,
)


@pytest.fixture
def sample_features() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Employee_ID": [1, 2, 3],
            "job_role": ["Analyst", "Manager", "Analyst"],
            "experience_years": [2, 10, 5],
            "ai_tool_usage_hours_per_week": [2, 10, 20],
            "manual_work_hours_per_week": [15, 30, 25],
            "meeting_hours_per_week": [5, 8, 6],
            "deadline_pressure_level": ["Low", "High", "Medium"],
            "tasks_automated_percent": [10, 50, 80],
            "focus_hours_per_day": [4, 3, 5],
            "collaboration_hours_per_week": [6, 10, 8],
        }
    )


@pytest.fixture
def sample_targets() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Employee_ID": [1, 2, 3],
            "burnout_risk_score": [4.0, 9.0, 7.0],
            "burnout_risk_level": ["Low", "High", "High"],
            "productivity_score": [80.0, 60.0, 75.0],
            "work_life_balance_score": [7.0, 4.0, 5.0],
        }
    )


@pytest.fixture
def sample_dashboard_df(sample_features: pd.DataFrame, sample_targets: pd.DataFrame) -> pd.DataFrame:
    df = sample_features.merge(sample_targets, on="Employee_ID")
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


def test_load_dashboard_data_merges_and_creates_derived_columns(
    monkeypatch: pytest.MonkeyPatch,
    sample_features: pd.DataFrame,
    sample_targets: pd.DataFrame,
) -> None:
    """Test that the function correctly merges data and creates derived columns."""
    def mock_read_csv(path):
        path_str = str(path)
        if "feature" in path_str.lower():
            return sample_features
        return sample_targets

    monkeypatch.setattr("src.data.pd.read_csv", mock_read_csv)

    df = load_dashboard_data()

    assert len(df) == 3
    assert "workload_score" in df.columns
    assert "workload_band" in df.columns
    assert "ai_band" in df.columns

    expected_workload_scores = [
        15 + 5 + 1,  # Low -> 1
        30 + 8 + 3,  # High -> 3
        25 + 6 + 2,  # Medium -> 2
    ]
    assert df["workload_score"].tolist() == expected_workload_scores

    assert set(df["ai_band"].astype(str)) == {"Low", "Moderate", "High"}
    assert set(df["workload_band"].astype(str)) == {"Low", "Medium", "High"}


def test_get_filter_choices_returns_expected_options(
    sample_dashboard_df: pd.DataFrame,
) -> None:
    """Test that the function returns the expected filter options."""
    choices = get_filter_choices(sample_dashboard_df)

    assert choices["job_role_choices"] == ["All", "Analyst", "Manager"]
    assert choices["ai_band_choices"] == ["All", "High", "Low", "Moderate"]
    assert choices["deadline_choices"] == ["High", "Low", "Medium"]


def test_get_slider_ranges_returns_correct_min_max(
    sample_dashboard_df: pd.DataFrame,
) -> None:
    """Test that the function returns the correct min and max values for each slider."""
    ranges = get_slider_ranges(sample_dashboard_df)

    assert ranges["experience"] == (2, 10)
    assert ranges["ai_usage"] == (2, 20)
    assert ranges["manual_hours"] == (15, 30)
    assert ranges["tasks_automated"] == (10, 80)


def test_get_baselines_returns_expected_summary_values(    
    sample_dashboard_df: pd.DataFrame,
) -> None:
    """Test that the function returns the expected summary values."""
    baselines = get_baselines(sample_dashboard_df)

    assert baselines["median_burnout"] == 7.0
    assert baselines["median_productivity"] == 75.0
    assert baselines["median_wlb"] == 5.0
    assert baselines["high_burnout_rate"] == pytest.approx(2 / 3)