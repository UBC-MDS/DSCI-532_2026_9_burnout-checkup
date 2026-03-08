from __future__ import annotations

import altair as alt
import pandas as pd

from src.constants.theme import COLORS, deadline_scale, ai_band_scale


def empty_chart(message: str, height: int = 260) -> alt.Chart:
    """
    Create a placeholder chart for empty-filter results.

    Parameters
    ----------
    message : str
        Message to display in the chart area.
    height : int, default=260
        Chart height in pixels.

    Returns
    -------
    alt.Chart
        Altair text chart displaying the provided message.
    """
    return (
        alt.Chart(pd.DataFrame({"text": [message]}))
        .mark_text(align="center", baseline="middle", size=14)
        .encode(text="text:N")
        .properties(height=height)
    )


def make_ai_vs_burnout_chart(
    d: pd.DataFrame,
    baseline_median_burnout: float,
    height: int = 260,
) -> alt.Chart:
    """
    Build the AI usage vs burnout scatter plot.

    Parameters
    ----------
    d : pandas.DataFrame
        Filtered dashboard dataframe.
    baseline_median_burnout : float
        Company-wide median burnout score used as the reference line.
    height : int, default=260
        Chart height in pixels.

    Returns
    -------
    alt.Chart
        Scatter plot with a reference median burnout line.
    """
    if d.empty:
        return empty_chart("No data for current filters.", height=height)

    chart = (
        alt.Chart(d)
        .mark_circle(opacity=0.7)
        .encode(
            x=alt.X(
                "ai_tool_usage_hours_per_week:Q",
                title="AI tool usage (hrs/week)",
            ),
            y=alt.Y("burnout_risk_score:Q", title="Burnout risk score"),
            color=alt.Color(
                "deadline_pressure_level:N",
                title="Deadline pressure",
                scale=deadline_scale(),
            ),
            tooltip=[
                "job_role:N",
                "experience_years:Q",
                "ai_tool_usage_hours_per_week:Q",
                "manual_work_hours_per_week:Q",
                "burnout_risk_score:Q",
            ],
        )
        .properties(height=height)
    )

    median_line = (
        alt.Chart(
            pd.DataFrame(
                {"y": [baseline_median_burnout], "line": ["Company Median Burnout"]}
            )
        )
        .mark_rule(strokeDash=[6, 4])
        .encode(
            y="y:Q",
            color=alt.Color(
                "line:N",
                scale=alt.Scale(range=[COLORS["alert_red"]]),
                legend=alt.Legend(title=None),
            ),
        )
    )

    return (chart + median_line).resolve_scale(color="independent")


def make_burnout_by_role_chart(
    d: pd.DataFrame,
    height: int = 260,
) -> alt.Chart:
    """
    Build the mean burnout-by-role bar chart.

    Parameters
    ----------
    d : pandas.DataFrame
        Filtered dashboard dataframe.
    height : int, default=260
        Chart height in pixels.

    Returns
    -------
    alt.Chart
        Bar chart of average burnout risk score by job role.
    """
    if d.empty:
        return empty_chart("No data for current filters.", height=height)

    summary = (
        d.groupby("job_role", as_index=False)["burnout_risk_score"]
        .mean()
        .rename(columns={"burnout_risk_score": "avg_burnout"})
        .sort_values("avg_burnout", ascending=False)
    )

    return (
        alt.Chart(summary)
        .mark_bar(color=COLORS["medium_brown"])
        .encode(
            x=alt.X("job_role:N", sort="-y", title="Job role"),
            y=alt.Y("avg_burnout:Q", title="Avg burnout risk score"),
            tooltip=["job_role:N", alt.Tooltip("avg_burnout:Q", format=".2f")],
        )
        .properties(height=height)
    )


def make_hours_breakdown_chart(
    d: pd.DataFrame,
    height: int = 260,
) -> alt.Chart:
    """
    Build the weekly work hours breakdown donut chart.

    Parameters
    ----------
    d : pandas.DataFrame
        Filtered dashboard dataframe.
    height : int, default=260
        Chart height in pixels.

    Returns
    -------
    alt.Chart
        Donut chart showing average weekly hours composition.
    """
    if d.empty:
        return empty_chart("No data for current filters.", height=height)

    weekly_focus = d["focus_hours_per_day"] * 5.0

    breakdown = pd.DataFrame(
        {
            "category": ["Meetings", "Collaboration", "Deep work", "Manual work"],
            "hours": [
                float(d["meeting_hours_per_week"].mean()),
                float(d["collaboration_hours_per_week"].mean()),
                float(weekly_focus.mean()),
                float(d["manual_work_hours_per_week"].mean()),
            ],
        }
    )

    total = breakdown["hours"].sum()
    if total <= 0:
        return empty_chart("No hours available for current filters.", height=height)

    breakdown["pct"] = breakdown["hours"] / total
    breakdown["pct_label"] = (
        (breakdown["pct"] * 100).round(0).astype(int).astype(str) + "%"
    )

    return (
        alt.Chart(breakdown)
        .mark_arc(innerRadius=70)
        .encode(
            theta=alt.Theta("hours:Q", title=None),
            color=alt.Color(
                "category:N",
                title=None,
                scale=alt.Scale(
                    domain=["Meetings", "Collaboration", "Deep work", "Manual work"],
                    range=[
                        COLORS["medium_brown"],
                        COLORS["light_orange"],
                        COLORS["deep_maroon"],
                        COLORS["soft_gold"],
                    ],
                ),
            ),
            tooltip=[
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("hours:Q", title="Avg hours/week", format=".1f"),
                alt.Tooltip("pct:Q", title="Share", format=".0%"),
            ],
        )
        .properties(height=height)
    )


def make_productivity_vs_burnout_chart(
    d: pd.DataFrame,
    baseline_median_productivity: float,
    baseline_median_burnout: float,
    height: int = 260,
) -> alt.Chart:
    """
    Build the productivity vs burnout scatter plot.

    Parameters
    ----------
    d : pandas.DataFrame
        Filtered dashboard dataframe.
    baseline_median_productivity : float
        Company-wide median productivity score used as vertical reference.
    baseline_median_burnout : float
        Company-wide median burnout score used as horizontal reference.
    height : int, default=260
        Chart height in pixels.

    Returns
    -------
    alt.Chart
        Scatter plot with productivity and burnout median reference lines.
    """
    if d.empty:
        return empty_chart("No data for current filters.", height=height)

    chart = (
        alt.Chart(d)
        .mark_circle(opacity=0.7)
        .encode(
            x=alt.X("productivity_score:Q", title="Productivity score"),
            y=alt.Y("burnout_risk_score:Q", title="Burnout risk score"),
            color=alt.Color(
                "ai_band:N",
                title="AI usage band",
                scale=ai_band_scale(),
            ),
            tooltip=[
                "job_role:N",
                "ai_band:N",
                "productivity_score:Q",
                "burnout_risk_score:Q",
            ],
        )
        .properties(height=height)
    )

    vline = (
        alt.Chart(
            pd.DataFrame(
                {
                    "x": [baseline_median_productivity],
                    "line": ["Company Median Productivity"],
                }
            )
        )
        .mark_rule(strokeDash=[6, 4])
        .encode(
            x="x:Q",
            color=alt.Color(
                "line:N",
                scale=alt.Scale(range=[COLORS["alert_red"]]),
                legend=alt.Legend(title=None),
            ),
        )
    )

    hline = (
        alt.Chart(
            pd.DataFrame(
                {"y": [baseline_median_burnout], "line": ["Company Median Burnout"]}
            )
        )
        .mark_rule(strokeDash=[6, 4])
        .encode(
            y="y:Q",
            color=alt.Color(
                "line:N",
                scale=alt.Scale(range=[COLORS["alert_red"]]),
                legend=alt.Legend(title=None),
            ),
        )
    )

    return (chart + vline + hline).resolve_scale(color="independent")