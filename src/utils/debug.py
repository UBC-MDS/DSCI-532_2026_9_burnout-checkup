from __future__ import annotations

import pandas as pd


def format_filter_debug(
    *,
    job_role,
    ai_band,
    experience,
    ai_usage,
    manual_hours,
    tasks_automated,
    deadline_pressure,
    show_pred,
    filtered_df: pd.DataFrame,
) -> str:
    """
    Format dashboard filter state for the debug panel.

    Parameters
    ----------
    job_role : Any
        Current job role input value.
    ai_band : Any
        Current AI band input value.
    experience : Any
        Current experience slider value.
    ai_usage : Any
        Current AI usage slider value.
    manual_hours : Any
        Current manual hours slider value.
    tasks_automated : Any
        Current tasks automated slider value.
    deadline_pressure : Any
        Current deadline pressure input value.
    show_pred : Any
        Current show-prediction toggle value.
    filtered_df : pandas.DataFrame
        Current filtered dataframe.

    Returns
    -------
    str
        Multi-line debug string.
    """
    return (
        f"job_role={job_role}\n"
        f"ai_band={ai_band}\n"
        f"experience={experience}\n"
        f"ai_usage={ai_usage}\n"
        f"manual_hours={manual_hours}\n"
        f"tasks_automated={tasks_automated}\n"
        f"deadline_pressure={deadline_pressure}\n"
        f"show_pred={show_pred}\n"
        f"filtered_rows={len(filtered_df)}"
    )
