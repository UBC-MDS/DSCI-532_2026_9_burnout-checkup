# tests/test_filters.py

from __future__ import annotations

import pandas as pd
import pytest

from src.filters import apply_dashboard_filters, normalize_querychat_result


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Create a small deterministic dashboard-like dataframe for filter tests."""
    return pd.DataFrame(
        {
            "job_role": ["Analyst", "Manager", "Analyst", "Designer", "Developer"],
            "ai_band": ["Low", "High", "Medium", "High", "Low"],
            "experience_years": [2, 8, 5, 10, 3],
            "ai_tool_usage_hours_per_week": [1, 12, 6, 15, 2],
            "manual_work_hours_per_week": [30, 20, 25, 10, 35],
            "tasks_automated_percent": [10, 80, 50, 90, 20],
            "deadline_pressure_level": ["Low", "High", "Medium", "High", "Low"],
        }
    )


def test_apply_dashboard_filters_returns_all_rows_when_all_defaults_selected(
    sample_df: pd.DataFrame,
) -> None:
    """Return all rows when sentinel/default choices cover the full dataset."""
    result = apply_dashboard_filters(
        df=sample_df,
        job_role=["All"],
        ai_band=["All"],
        experience=(2, 10),
        ai_usage=(1, 15),
        manual_hours=(10, 35),
        tasks_automated=(10, 90),
        deadline_pressure=["Low", "Medium", "High"],
    )

    pd.testing.assert_frame_equal(result.reset_index(drop=True), sample_df)


def test_apply_dashboard_filters_filters_single_job_role(
    sample_df: pd.DataFrame,
) -> None:
    """Filter rows down to a single selected job role."""
    result = apply_dashboard_filters(
        df=sample_df,
        job_role=["Analyst"],
        ai_band=["All"],
        experience=(2, 10),
        ai_usage=(1, 15),
        manual_hours=(10, 35),
        tasks_automated=(10, 90),
        deadline_pressure=["Low", "Medium", "High"],
    )

    assert len(result) == 2
    assert set(result["job_role"]) == {"Analyst"}


def test_apply_dashboard_filters_filters_multiple_job_roles(
    sample_df: pd.DataFrame,
) -> None:
    """Allow multi-select job role filtering."""
    result = apply_dashboard_filters(
        df=sample_df,
        job_role=["Analyst", "Manager"],
        ai_band=["All"],
        experience=(2, 10),
        ai_usage=(1, 15),
        manual_hours=(10, 35),
        tasks_automated=(10, 90),
        deadline_pressure=["Low", "Medium", "High"],
    )

    assert len(result) == 3
    assert set(result["job_role"]) == {"Analyst", "Manager"}


def test_apply_dashboard_filters_does_not_filter_job_role_when_all_present(
    sample_df: pd.DataFrame,
) -> None:
    """Preserve current app logic: 'All' disables job role filtering."""
    result = apply_dashboard_filters(
        df=sample_df,
        job_role=["All", "Analyst"],
        ai_band=["All"],
        experience=(2, 10),
        ai_usage=(1, 15),
        manual_hours=(10, 35),
        tasks_automated=(10, 90),
        deadline_pressure=["Low", "Medium", "High"],
    )

    pd.testing.assert_frame_equal(result.reset_index(drop=True), sample_df)


def test_apply_dashboard_filters_filters_ai_band(
    sample_df: pd.DataFrame,
) -> None:
    """Filter rows by AI usage band."""
    result = apply_dashboard_filters(
        df=sample_df,
        job_role=["All"],
        ai_band=["High"],
        experience=(2, 10),
        ai_usage=(1, 15),
        manual_hours=(10, 35),
        tasks_automated=(10, 90),
        deadline_pressure=["Low", "Medium", "High"],
    )

    assert len(result) == 2
    assert set(result["ai_band"]) == {"High"}


def test_apply_dashboard_filters_inclusive_numeric_bounds(
    sample_df: pd.DataFrame,
) -> None:
    """Use inclusive lower/upper bounds for numeric range filters."""
    result = apply_dashboard_filters(
        df=sample_df,
        job_role=["All"],
        ai_band=["All"],
        experience=(3, 8),
        ai_usage=(2, 12),
        manual_hours=(20, 35),
        tasks_automated=(20, 80),
        deadline_pressure=["Low", "Medium", "High"],
    )

    # Expected rows: Manager, Analyst(row index 2), Developer
    assert len(result) == 3
    assert set(result["experience_years"]) == {8, 5, 3}
    assert set(result["ai_tool_usage_hours_per_week"]) == {12, 6, 2}
    assert set(result["tasks_automated_percent"]) == {80, 50, 20}


def test_apply_dashboard_filters_filters_deadline_pressure(
    sample_df: pd.DataFrame,
) -> None:
    """Retain only selected deadline pressure levels."""
    result = apply_dashboard_filters(
        df=sample_df,
        job_role=["All"],
        ai_band=["All"],
        experience=(2, 10),
        ai_usage=(1, 15),
        manual_hours=(10, 35),
        tasks_automated=(10, 90),
        deadline_pressure=["High"],
    )

    assert len(result) == 2
    assert set(result["deadline_pressure_level"]) == {"High"}


def test_apply_dashboard_filters_combines_all_filters_correctly(
    sample_df: pd.DataFrame,
) -> None:
    """Apply all filter dimensions together as an intersection."""
    result = apply_dashboard_filters(
        df=sample_df,
        job_role=["Manager"],
        ai_band=["High"],
        experience=(7, 9),
        ai_usage=(10, 12),
        manual_hours=(18, 22),
        tasks_automated=(75, 85),
        deadline_pressure=["High"],
    )

    assert len(result) == 1
    row = result.iloc[0]
    assert row["job_role"] == "Manager"
    assert row["ai_band"] == "High"
    assert row["experience_years"] == 8


def test_apply_dashboard_filters_can_return_empty_dataframe(
    sample_df: pd.DataFrame,
) -> None:
    """Return an empty dataframe when no rows satisfy the filters."""
    result = apply_dashboard_filters(
        df=sample_df,
        job_role=["Designer"],
        ai_band=["Low"],
        experience=(1, 2),
        ai_usage=(0, 1),
        manual_hours=(30, 40),
        tasks_automated=(0, 10),
        deadline_pressure=["Medium"],
    )

    assert result.empty
    assert list(result.columns) == list(sample_df.columns)


def test_apply_dashboard_filters_does_not_mutate_input_dataframe(
    sample_df: pd.DataFrame,
) -> None:
    """Leave the original input dataframe unchanged."""
    original = sample_df.copy(deep=True)

    _ = apply_dashboard_filters(
        df=sample_df,
        job_role=["Analyst"],
        ai_band=["Medium"],
        experience=(1, 10),
        ai_usage=(0, 15),
        manual_hours=(0, 40),
        tasks_automated=(0, 100),
        deadline_pressure=["Medium"],
    )

    pd.testing.assert_frame_equal(sample_df, original)


class DummyQueryChatFrame:
    """Simple stand-in for a QueryChat-like object with to_native()."""

    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df

    def to_native(self) -> pd.DataFrame:
        return self._df.copy()


def test_normalize_querychat_result_uses_to_native_when_available() -> None:
    """Convert QueryChat-like dataframe objects via to_native()."""
    expected = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    wrapped = DummyQueryChatFrame(expected)

    result = normalize_querychat_result(wrapped, fallback_df=pd.DataFrame())

    pd.testing.assert_frame_equal(result, expected)


def test_normalize_querychat_result_returns_fallback_copy_when_none() -> None:
    """Return a copy of fallback_df when QueryChat result is None."""
    fallback = pd.DataFrame({"a": [10, 20]})

    result = normalize_querychat_result(None, fallback_df=fallback)

    pd.testing.assert_frame_equal(result, fallback)
    assert result is not fallback


def test_normalize_querychat_result_returns_dataframe_as_is() -> None:
    """Return native pandas DataFrame unchanged when already normalized."""
    df = pd.DataFrame({"a": [1, 2, 3]})

    result = normalize_querychat_result(df, fallback_df=pd.DataFrame())

    pd.testing.assert_frame_equal(result, df)