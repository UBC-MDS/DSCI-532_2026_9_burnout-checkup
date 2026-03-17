# src/kpis.py

"""Reusable KPI helpers for the burnout dashboard."""

from __future__ import annotations

import pandas as pd
from shiny import ui


def kpi_card(title: str, value: str, sub: str = "", sub_class: str = ""):
    """
    Build a KPI card UI element.

    Parameters
    ----------
    title : str
        KPI title text.
    value : str
        Main KPI value to display.
    sub : str, default=""
        Supporting subtitle text shown below the main value.
    sub_class : str, default=""
        Optional CSS modifier class for the subtitle (for example, "up" or "down").

    Returns
    -------
    shiny.ui.TagChild
        A Shiny UI div representing the KPI card.
    """
    return ui.div(
        ui.div(title, class_="kpi-title"),
        ui.div(value, class_="kpi-value"),
        ui.div(sub, class_=f"kpi-sub {sub_class}"),
        class_="kpi-card",
    )


def safe_mean(series: pd.Series) -> float | None:
    """
    Safely compute the mean of a pandas Series.

    Parameters
    ----------
    series : pandas.Series
        Numeric series to summarize.

    Returns
    -------
    float | None
        Mean value, or None if the series is empty.
    """
    if series.empty:
        return None
    return float(series.mean())


def safe_median(series: pd.Series) -> float | None:
    """
    Safely compute the median of a pandas Series.

    Parameters
    ----------
    series : pandas.Series
        Numeric series to summarize.

    Returns
    -------
    float | None
        Median value, or None if the series is empty or median is missing.
    """
    clean = series.dropna()

    if clean.empty:
        return None

    val = clean.median()

    return float(val)


def percent_diff(value: float, baseline: float) -> float:
    """
    Compute relative percent difference from a baseline.

    Parameters
    ----------
    value : float
        Observed value.
    baseline : float
        Reference baseline value.

    Returns
    -------
    float
        Relative difference as a proportion.
    """
    if baseline == 0:
        return 0.0
    return (value - baseline) / baseline


def trend_arrow(diff: float) -> str:
    """
    Return an arrow symbol describing direction of change.

    Parameters
    ----------
    diff : float
        Relative difference from baseline.

    Returns
    -------
    str
        Up, down, or neutral arrow.
    """
    if diff > 0:
        return "▲"
    if diff < 0:
        return "▼"
    return "→"


def trend_class(diff: float, higher_is_better: bool) -> str:
    """
    Return the CSS class for KPI subtitle coloring.

    Parameters
    ----------
    diff : float
        Relative difference from baseline.
    higher_is_better : bool
        Whether an increase should be treated as favorable.

    Returns
    -------
    str
        CSS modifier class: "up", "down", or "".
    """
    if diff == 0:
        return ""

    if higher_is_better:
        return "down" if diff > 0 else "up"

    return "up" if diff > 0 else "down"


def median_metric_card(
    df: pd.DataFrame,
    column: str,
    title: str,
    baseline: float,
    *,
    higher_is_better: bool,
):
    """
    Build a KPI card for a median-based metric.

    Parameters
    ----------
    df : pandas.DataFrame
        Filtered dataframe.
    column : str
        Column whose median will be displayed.
    title : str
        KPI title.
    baseline : float
        Baseline median used for comparison.
    higher_is_better : bool
        Whether larger values are considered favorable.

    Returns
    -------
    shiny.ui.TagChild
        KPI card UI element.
    """
    val = safe_median(df[column])
    if val is None:
        return kpi_card(title, "—")

    diff = percent_diff(val, baseline)
    arrow = trend_arrow(diff)
    sub_class = trend_class(diff, higher_is_better=higher_is_better)

    return kpi_card(
        title,
        f"{val:.1f}",
        f"{arrow} {abs(diff) * 100:.0f}% vs baseline",
        sub_class,
    )


def high_burnout_pct_card(
    df: pd.DataFrame,
    baseline_high_burnout: float,
    *,
    title: str = "High Burnout %",
):
    """
    Build a KPI card for the percentage of employees with high burnout.

    Parameters
    ----------
    df : pandas.DataFrame
        Filtered dataframe.
    baseline_high_burnout : float
        Company-wide baseline proportion of high burnout.
    title : str, default="High Burnout %"
        KPI title text.

    Returns
    -------
    shiny.ui.TagChild
        KPI card UI element.
    """
    if df.empty:
        return kpi_card(title, "—")

    pct = float((df["burnout_risk_level"] == "High").mean())
    diff = percent_diff(pct, baseline_high_burnout)
    arrow = trend_arrow(diff)
    sub_class = trend_class(diff, higher_is_better=False)

    return kpi_card(
        title,
        f"{pct * 100:.1f}%",
        f"{arrow} {abs(diff) * 100:.0f}% vs baseline",
        sub_class,
    )


def count_card(
    df: pd.DataFrame,
    *,
    title: str = "Employees Found",
    subtitle: str = "Rows returned by AI query",
):
    """
    Build a KPI card showing the number of rows in a dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        Filtered dataframe.
    title : str, default="Employees Found"
        KPI title text.
    subtitle : str, default="Rows returned by AI query"
        Subtitle text.

    Returns
    -------
    shiny.ui.TagChild
        KPI card UI element.
    """
    if df.empty:
        return kpi_card(title, "0")

    return kpi_card(
        title,
        f"{len(df):,}",
        subtitle,
        "",
    )