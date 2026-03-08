# tests/test_kpis.py

"""Tests for reusable KPI helpers in src.kpis."""

from __future__ import annotations

import pandas as pd
import pytest

from src.kpis import (
    count_card,
    high_burnout_pct_card,
    kpi_card,
    median_metric_card,
    percent_diff,
    safe_mean,
    safe_median,
    trend_arrow,
    trend_class,
)


def _rendered_tag_text(tag) -> str:
    """Convert a Shiny tag to string for lightweight content assertions."""
    return str(tag)


def test_safe_mean_returns_none_for_empty_series():
    """safe_mean should return None when given an empty series."""
    series = pd.Series([], dtype=float)

    assert safe_mean(series) is None


def test_safe_mean_returns_float_for_non_empty_series():
    """safe_mean should return the mean as a float."""
    series = pd.Series([2, 4, 6])

    assert safe_mean(series) == 4.0
    assert isinstance(safe_mean(series), float)


def test_safe_median_returns_none_for_empty_series():
    """safe_median should return None for an empty series."""
    series = pd.Series([], dtype=float)

    assert safe_median(series) is None


def test_safe_median_returns_none_when_median_is_nan():
    """safe_median should return None when the computed median is NaN."""
    series = pd.Series([float("nan"), float("nan")])

    assert safe_median(series) is None


def test_safe_median_returns_float_for_valid_series():
    """safe_median should return the median as a float for valid input."""
    series = pd.Series([1, 3, 5])

    assert safe_median(series) == 3.0
    assert isinstance(safe_median(series), float)


@pytest.mark.parametrize(
    ("value", "baseline", "expected"),
    [
        (12.0, 10.0, 0.2),
        (8.0, 10.0, -0.2),
        (10.0, 10.0, 0.0),
        (10.0, 0.0, 0.0),
    ],
)
def test_percent_diff(value, baseline, expected):
    """percent_diff should compute relative change and guard baseline=0."""
    assert percent_diff(value, baseline) == expected


@pytest.mark.parametrize(
    ("diff", "expected"),
    [
        (0.1, "▲"),
        (-0.1, "▼"),
        (0.0, "→"),
    ],
)
def test_trend_arrow(diff, expected):
    """trend_arrow should map positive, negative, and zero diffs correctly."""
    assert trend_arrow(diff) == expected


@pytest.mark.parametrize(
    ("diff", "higher_is_better", "expected"),
    [
        (0.0, True, ""),
        (0.0, False, ""),
        (0.1, True, "down"),
        (-0.1, True, "up"),
        (0.1, False, "up"),
        (-0.1, False, "down"),
    ],
)
def test_trend_class(diff, higher_is_better, expected):
    """trend_class should return the correct CSS modifier."""
    assert trend_class(diff, higher_is_better=higher_is_better) == expected


def test_kpi_card_contains_expected_content():
    """kpi_card should include title, value, and subtitle in rendered output."""
    card = kpi_card("Median Productivity", "64.8", "▲ 5% vs baseline", "down")
    rendered = _rendered_tag_text(card)

    assert "Median Productivity" in rendered
    assert "64.8" in rendered
    assert "▲ 5% vs baseline" in rendered
    assert "kpi-card" in rendered
    assert "kpi-sub down" in rendered


def test_median_metric_card_returns_dash_for_empty_dataframe():
    """median_metric_card should show a dash when the dataframe is empty."""
    df = pd.DataFrame({"productivity_score": pd.Series(dtype=float)})

    card = median_metric_card(
        df,
        column="productivity_score",
        title="Median Productivity",
        baseline=60.0,
        higher_is_better=True,
    )
    rendered = _rendered_tag_text(card)

    assert "Median Productivity" in rendered
    assert "—" in rendered


def test_median_metric_card_formats_positive_diff_when_higher_is_better():
    """median_metric_card should render correct value, arrow, and class."""
    df = pd.DataFrame({"productivity_score": [70, 80, 90]})  # median = 80

    card = median_metric_card(
        df,
        column="productivity_score",
        title="Median Productivity",
        baseline=64.0,
        higher_is_better=True,
    )
    rendered = _rendered_tag_text(card)

    assert "Median Productivity" in rendered
    assert "80.0" in rendered
    assert "▲ 25% vs baseline" in rendered
    assert "kpi-sub down" in rendered


def test_median_metric_card_formats_negative_diff_when_higher_is_better():
    """median_metric_card should mark lower-than-baseline as unfavorable."""
    df = pd.DataFrame({"productivity_score": [40, 50, 60]})  # median = 50

    card = median_metric_card(
        df,
        column="productivity_score",
        title="Median Productivity",
        baseline=100.0,
        higher_is_better=True,
    )
    rendered = _rendered_tag_text(card)

    assert "50.0" in rendered
    assert "▼ 50% vs baseline" in rendered
    assert "kpi-sub up" in rendered


def test_median_metric_card_for_burnout_uses_inverse_directionality():
    """median_metric_card should treat higher burnout as worse."""
    df = pd.DataFrame({"burnout_risk_score": [8, 9, 10]})  # median = 9

    card = median_metric_card(
        df,
        column="burnout_risk_score",
        title="Median Burnout Risk Score",
        baseline=6.0,
        higher_is_better=False,
    )
    rendered = _rendered_tag_text(card)

    assert "9.0" in rendered
    assert "▲ 50% vs baseline" in rendered
    assert "kpi-sub up" in rendered


def test_high_burnout_pct_card_returns_dash_for_empty_dataframe():
    """high_burnout_pct_card should show a dash when no rows are present."""
    df = pd.DataFrame({"burnout_risk_level": pd.Series(dtype=str)})

    card = high_burnout_pct_card(df, baseline_high_burnout=0.5)
    rendered = _rendered_tag_text(card)

    assert "High Burnout %" in rendered
    assert "—" in rendered


def test_high_burnout_pct_card_renders_percent_and_comparison():
    """high_burnout_pct_card should compute filtered high-burnout share."""
    df = pd.DataFrame(
        {
            "burnout_risk_level": ["High", "High", "Low", "Medium"]
        }
    )  # 50%

    card = high_burnout_pct_card(df, baseline_high_burnout=0.25)
    rendered = _rendered_tag_text(card)

    assert "High Burnout %" in rendered
    assert "50.0%" in rendered
    assert "▲ 100% vs baseline" in rendered
    assert "kpi-sub up" in rendered


def test_count_card_returns_zero_for_empty_dataframe():
    """count_card should show zero when the dataframe is empty."""
    df = pd.DataFrame()

    card = count_card(df)
    rendered = _rendered_tag_text(card)

    assert "Employees Found" in rendered
    assert ">0<" in rendered or "0" in rendered


def test_count_card_renders_row_count_and_subtitle():
    """count_card should show formatted row count and subtitle."""
    df = pd.DataFrame({"a": range(1234)})

    card = count_card(df)
    rendered = _rendered_tag_text(card)

    assert "Employees Found" in rendered
    assert "1,234" in rendered
    assert "Rows returned by AI query" in rendered