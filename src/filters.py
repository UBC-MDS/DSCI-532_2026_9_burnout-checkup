from __future__ import annotations

from typing import Sequence

import pandas as pd


def apply_dashboard_filters(
    df: pd.DataFrame,
    job_role: Sequence[str],
    ai_band: Sequence[str],
    experience: tuple[int, int],
    ai_usage: tuple[int, int],
    manual_hours: tuple[int, int],
    tasks_automated: tuple[int, int],
    deadline_pressure: Sequence[str],
) -> pd.DataFrame:
    """
    Filter the dashboard dataframe using the current sidebar input values.

    This function applies the same filtering rules used by the dashboard's
    reactive filter panel. It supports multi-select job roles and AI bands,
    numeric range filters, and deadline pressure category filtering.

    Parameters
    ----------
    df : pandas.DataFrame
        Input employee-level dataframe to filter.
    job_role : Sequence[str]
        Selected job role values from the UI. If ``"Manager"`` is present,
        the job role filter is not applied under the current dashboard logic.
    ai_band : Sequence[str]
        Selected AI usage band values from the UI. If ``"All"`` is present,
        the AI band filter is not applied.
    experience : tuple[int, int]
        Inclusive lower and upper bounds for ``experience_years``.
    ai_usage : tuple[int, int]
        Inclusive lower and upper bounds for
        ``ai_tool_usage_hours_per_week``.
    manual_hours : tuple[int, int]
        Inclusive lower and upper bounds for
        ``manual_work_hours_per_week``.
    tasks_automated : tuple[int, int]
        Inclusive lower and upper bounds for ``tasks_automated_percent``.
    deadline_pressure : Sequence[str]
        Selected deadline pressure levels to retain.

    Returns
    -------
    pandas.DataFrame
        Filtered dataframe matching the provided UI selections.

    Notes
    -----
    The current app logic treats ``"Manager"`` in ``job_role`` as the
    default sentinel value meaning "do not filter by role". This behavior is
    preserved here so the refactor does not change app behavior.

    Examples
    --------
    >>> filtered = apply_dashboard_filters(
    ...     df=data,
    ...     job_role=["Analyst"],
    ...     ai_band=["High"],
    ...     experience=(2, 8),
    ...     ai_usage=(3, 10),
    ...     manual_hours=(10, 30),
    ...     tasks_automated=(20, 80),
    ...     deadline_pressure=["Medium", "High"],
    ... )
    >>> isinstance(filtered, pd.DataFrame)
    True
    """
    d = df.copy()

    if "All" not in job_role:
        d = d[d["job_role"].isin(job_role)]

    if "All" not in ai_band:
        d = d[d["ai_band"].astype(str).isin(ai_band)]

    d = d[
        (d["experience_years"] >= experience[0])
        & (d["experience_years"] <= experience[1])
    ]

    d = d[
        (d["ai_tool_usage_hours_per_week"] >= ai_usage[0])
        & (d["ai_tool_usage_hours_per_week"] <= ai_usage[1])
    ]

    d = d[
        (d["manual_work_hours_per_week"] >= manual_hours[0])
        & (d["manual_work_hours_per_week"] <= manual_hours[1])
    ]

    d = d[
        (d["tasks_automated_percent"] >= tasks_automated[0])
        & (d["tasks_automated_percent"] <= tasks_automated[1])
    ]

    d = d[d["deadline_pressure_level"].isin(deadline_pressure)]

    return d


def normalize_querychat_result(result: object, fallback_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize a QueryChat dataframe result to a native pandas DataFrame.

    QueryChat may return a dataframe-like object rather than a native pandas
    dataframe. This helper standardizes the return value for downstream use
    in Shiny outputs and chart functions.

    Parameters
    ----------
    result : object
        Object returned by ``qc_vals.df()``.
    fallback_df : pandas.DataFrame
        Dataframe to return when the QueryChat result is ``None``.

    Returns
    -------
    pandas.DataFrame
        Native pandas dataframe corresponding to the QueryChat result.

    Notes
    -----
    If ``result`` has a ``to_native()`` method, that method is used to
    convert it to pandas. If ``result`` is ``None``, a copy of
    ``fallback_df`` is returned.

    Examples
    --------
    >>> normalize_querychat_result(None, fallback_df=data).equals(data)
    True
    """
    if hasattr(result, "to_native"):
        return result.to_native()

    if result is None:
        return fallback_df.copy()

    return result
