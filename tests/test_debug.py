# tests/test_debug.py

from __future__ import annotations

import pandas as pd

from src.utils.debug import format_filter_debug


def test_format_filter_debug_returns_expected_multiline_string():
    """Test that the function returns a correctly formatted multi-line string."""
    filtered_df = pd.DataFrame({"x": [1, 2, 3]})

    result = format_filter_debug(
        job_role="Analyst",
        ai_band=["Low", "Moderate"],
        experience=(2, 8),
        ai_usage=(1, 12),
        manual_hours=(10, 30),
        tasks_automated=(20, 80),
        deadline_pressure=["Low", "High"],
        filtered_df=filtered_df,
    )

    expected = (
        "job_role=Analyst\n"
        "ai_band=['Low', 'Moderate']\n"
        "experience=(2, 8)\n"
        "ai_usage=(1, 12)\n"
        "manual_hours=(10, 30)\n"
        "tasks_automated=(20, 80)\n"
        "deadline_pressure=['Low', 'High']\n"
        "filtered_rows=3"
    )

    assert result == expected


def test_format_filter_debug_reports_zero_filtered_rows():
    """Test that the function correctly reports zero filtered rows."""
    filtered_df = pd.DataFrame()

    result = format_filter_debug(
        job_role="All",
        ai_band=["All"],
        experience=(0, 10),
        ai_usage=(0, 20),
        manual_hours=(0, 40),
        tasks_automated=(0, 100),
        deadline_pressure=["Low", "Medium", "High"],
        filtered_df=filtered_df,
    )

    assert "filtered_rows=0" in result