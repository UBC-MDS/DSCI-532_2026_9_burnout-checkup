# tests/test_charts.py

from __future__ import annotations

import pandas as pd
import pytest

from src.charts import (
    empty_chart,
    make_ai_vs_burnout_chart,
    make_burnout_by_role_chart,
    make_hours_breakdown_chart,
    make_productivity_vs_burnout_chart,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Small representative dataframe for chart tests."""
    return pd.DataFrame(
        {
            "job_role": ["Analyst", "Analyst", "Manager", "Designer"],
            "experience_years": [2, 5, 8, 3],
            "ai_tool_usage_hours_per_week": [4, 10, 15, 7],
            "manual_work_hours_per_week": [20, 25, 18, 22],
            "meeting_hours_per_week": [5, 6, 8, 4],
            "collaboration_hours_per_week": [7, 5, 6, 8],
            "focus_hours_per_day": [4, 5, 6, 3],
            "burnout_risk_score": [6.0, 8.0, 9.0, 5.5],
            "deadline_pressure_level": ["Low", "Medium", "High", "Medium"],
            "productivity_score": [70, 65, 80, 60],
            "ai_band": ["Low", "Moderate", "High", "Low"],
        }
    )


@pytest.fixture
def zero_hours_df(sample_df: pd.DataFrame) -> pd.DataFrame:
    """Dataframe where all time-allocation fields are zero."""
    d = sample_df.copy()
    d["meeting_hours_per_week"] = 0
    d["collaboration_hours_per_week"] = 0
    d["focus_hours_per_day"] = 0
    d["manual_work_hours_per_week"] = 0
    return d


def test_empty_chart_returns_text_chart():
    chart = empty_chart("Nothing to show", height=300)
    spec = chart.to_dict()

    assert spec["mark"]["type"] == "text"
    assert spec["encoding"]["text"]["field"] == "text"
    assert spec["height"] == 300
    assert chart.data.iloc[0]["text"] == "Nothing to show"


def test_make_ai_vs_burnout_chart_returns_placeholder_for_empty_df():
    d = pd.DataFrame()
    chart = make_ai_vs_burnout_chart(d, baseline_median_burnout=8.5)
    spec = chart.to_dict()

    assert spec["mark"]["type"] == "text"
    assert chart.data.iloc[0]["text"] == "No data for current filters."


def test_make_ai_vs_burnout_chart_returns_layered_chart(sample_df: pd.DataFrame):
    chart = make_ai_vs_burnout_chart(sample_df, baseline_median_burnout=8.0)
    spec = chart.to_dict()

    assert "layer" in spec
    assert len(spec["layer"]) == 2
    assert spec["resolve"]["scale"]["color"] == "independent"

    scatter_layer = spec["layer"][0]
    rule_layer = spec["layer"][1]

    assert scatter_layer["mark"]["type"] == "rect"
    assert scatter_layer["encoding"]["x"]["field"] == "ai_tool_usage_hours_per_week"
    assert scatter_layer["encoding"]["y"]["field"] == "burnout_risk_score"

    assert rule_layer["mark"]["type"] == "rule"
    assert rule_layer["encoding"]["y"]["field"] == "y"


def test_make_burnout_by_role_chart_returns_placeholder_for_empty_df():
    d = pd.DataFrame()
    chart = make_burnout_by_role_chart(d)
    spec = chart.to_dict()

    assert spec["mark"]["type"] == "text"
    assert chart.data.iloc[0]["text"] == "No data for current filters."


def test_make_burnout_by_role_chart_aggregates_roles(sample_df: pd.DataFrame):
    chart = make_burnout_by_role_chart(sample_df)
    spec = chart.to_dict()

    assert spec["mark"]["type"] == "bar"
    assert spec["encoding"]["x"]["field"] == "job_role"
    assert spec["encoding"]["y"]["field"] == "avg_burnout"

    chart_data = chart.data
    assert set(chart_data["job_role"]) == {"Analyst", "Manager", "Designer"}
    assert len(chart_data) == 3

    analyst_value = chart_data.loc[
        chart_data["job_role"] == "Analyst", "avg_burnout"
    ].iloc[0]
    assert analyst_value == pytest.approx((6.0 + 8.0) / 2)


def test_make_hours_breakdown_chart_returns_placeholder_for_empty_df():
    d = pd.DataFrame()
    chart = make_hours_breakdown_chart(d)
    spec = chart.to_dict()

    assert spec["mark"]["type"] == "text"
    assert chart.data.iloc[0]["text"] == "No data for current filters."


def test_make_hours_breakdown_chart_returns_placeholder_when_total_hours_zero(
    zero_hours_df: pd.DataFrame,
):
    chart = make_hours_breakdown_chart(zero_hours_df)
    spec = chart.to_dict()

    assert spec["mark"]["type"] == "text"
    assert chart.data.iloc[0]["text"] == "No hours available for current filters."


def test_make_hours_breakdown_chart_returns_arc_chart(sample_df: pd.DataFrame):
    chart = make_hours_breakdown_chart(sample_df)
    spec = chart.to_dict()

    assert spec["mark"]["type"] == "arc"
    assert spec["mark"]["innerRadius"] == 70
    assert spec["encoding"]["theta"]["field"] == "hours"

    chart_data = chart.data
    assert set(chart_data["category"]) == {
        "Meetings",
        "Collaboration",
        "Deep work",
        "Manual work",
    }
    assert len(chart_data) == 4
    assert chart_data["pct"].sum() == pytest.approx(1.0)


def test_make_productivity_vs_burnout_chart_returns_placeholder_for_empty_df():
    d = pd.DataFrame()
    chart = make_productivity_vs_burnout_chart(
        d,
        baseline_median_productivity=65.0,
        baseline_median_burnout=8.0,
    )
    spec = chart.to_dict()

    assert spec["mark"]["type"] == "text"
    assert chart.data.iloc[0]["text"] == "No data for current filters."


def test_make_productivity_vs_burnout_chart_returns_three_layer_chart(
    sample_df: pd.DataFrame,
):
    chart = make_productivity_vs_burnout_chart(
        sample_df,
        baseline_median_productivity=65.0,
        baseline_median_burnout=8.0,
    )
    spec = chart.to_dict()

    assert "layer" in spec
    assert len(spec["layer"]) == 3
    assert spec["resolve"]["scale"]["color"] == "independent"

    scatter_layer = spec["layer"][0]
    vline_layer = spec["layer"][1]
    hline_layer = spec["layer"][2]

    assert scatter_layer["mark"]["type"] == "circle"
    assert scatter_layer["encoding"]["x"]["field"] == "productivity_score"
    assert scatter_layer["encoding"]["y"]["field"] == "burnout_risk_score"

    assert vline_layer["mark"]["type"] == "rule"
    assert vline_layer["encoding"]["x"]["field"] == "x"

    assert hline_layer["mark"]["type"] == "rule"
    assert hline_layer["encoding"]["y"]["field"] == "y"