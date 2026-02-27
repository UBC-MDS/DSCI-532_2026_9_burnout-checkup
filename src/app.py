from sklearn import base

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import altair as alt

from constants.paths import FEATURES_PATH, TARGETS_PATH

# Read our data
features = pd.read_csv(FEATURES_PATH)
targets = pd.read_csv(TARGETS_PATH)
df = features.merge(
    targets, on="Employee_ID"
)  # merge features and targets in a single df

# Preprocessing taken from EDA file
df["workload_score"] = (
    df["manual_work_hours_per_week"]
    + df["meeting_hours_per_week"]
    + df["deadline_pressure_level"].map({"Low": 1, "Medium": 2, "High": 3})
)

df["workload_band"] = pd.qcut(
    df["workload_score"], q=3, labels=["Low", "Medium", "High"]
)
df["ai_band"] = pd.qcut(
    df["ai_tool_usage_hours_per_week"], q=3, labels=["Low", "Moderate", "High"]
)

# Input variables' options for filters
# employee_choices = ["All"] + sorted(df["Employee_ID"].astype(str).unique().tolist())
job_role_choices = ["All"] + sorted(df["job_role"].dropna().unique().tolist())
ai_band_choices = ["All"] + sorted(df["ai_band"].dropna().astype(str).unique().tolist())
deadline_choices = sorted(df["deadline_pressure_level"].dropna().unique().tolist())

# Slider ranges
exp_min, exp_max = int(df["experience_years"].min()), int(df["experience_years"].max())
ai_min, ai_max = int(df["ai_tool_usage_hours_per_week"].min()), int(
    df["ai_tool_usage_hours_per_week"].max()
)
man_min, man_max = int(df["manual_work_hours_per_week"].min()), int(
    df["manual_work_hours_per_week"].max()
)
task_min, task_max = int(df["tasks_automated_percent"].min()), int(
    df["tasks_automated_percent"].max()
)

# Company-wide baselines (computed once, used across outputs)
# Burnout median for reference in plots
BASELINE_MEDIAN_BURNOUT = float(df["burnout_risk_score"].median())
BASELINE_MEDIAN_PRODUCTIVITY = float(df["productivity_score"].median())

# -------------------------
# UI
# -------------------------
app_ui = ui.page_fluid(
    ui.tags.style(
        """
        .bslib-sidebar-layout > .sidebar > .sidebar-content {
            gap: 0 !important;
        }
        """
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3("AI Usage &\nBurnout Checkup"),
            ui.hr(),
            ui.h6("Job Role:"),
            ui.input_selectize(
                "job_role",
                None,
                choices=job_role_choices,
                selected="All",
            ),
            ui.br(),
            ui.h6("AI Usage Band:"),
            ui.input_selectize(
                "ai_band",
                None,
                choices=ai_band_choices,
                selected=["All"],
                multiple=True,
            ),
            ui.br(),
            ui.h6("Experience (years):"),
            ui.input_slider(
                "experience", None, min=exp_min, max=exp_max, value=(exp_min, exp_max)
            ),
            ui.br(),
            ui.h6("Weekly AI Usage:"),
            ui.input_slider(
                "ai_usage", None, min=ai_min, max=ai_max, value=(ai_min, ai_max)
            ),
            ui.br(),
            ui.h6("Manual Work Hours:"),
            ui.input_slider(
                "manual_hours", None, min=man_min, max=man_max, value=(man_min, man_max)
            ),
            ui.br(),
            ui.h6("Tasks Automated:"),
            ui.input_slider(
                "tasks_automated",
                None,
                min=task_min,
                max=task_max,
                value=(task_min, task_max),
            ),
            ui.br(),
            ui.h6("Deadline Pressure:"),
            ui.input_checkbox_group(
                "deadline_pressure",
                None,
                choices=deadline_choices,
                selected=deadline_choices,
                inline=True,
            ),
            ui.hr(),
            ui.input_checkbox("show_pred", "Show Predicted Risk Overlay", value=True),
            ui.input_checkbox("show_debug", "Show debug panel", value=False),
            width=320,
        ),
        # -------------------------
        # MAIN CONTENT
        # -------------------------
        ui.div(
            # KPI ROW (4 KPIs)
            ui.layout_columns(
                ui.card(
                    ui.card_header("Avg Burnout Risk Score"),
                    ui.h2(ui.output_text("kpi_avg_burnout")),
                    ui.p(
                        ui.em("Average burnout risk score for the filtered employees.")
                    ),
                ),
                ui.card(
                    ui.card_header("Avg Productivity Score"),
                    ui.h2(ui.output_text("kpi_avg_productivity")),
                    ui.p(
                        ui.em("Average productivity score for the filtered employees.")
                    ),
                ),
                ui.card(
                    ui.card_header("Burnout vs Median (%)"),
                    ui.h2(ui.output_text("kpi_burnout_vs_median")),
                    ui.p(
                        ui.em(
                            "Percentage difference between filtered burnout score and company median."
                        )
                    ),
                ),
                ui.card(
                    ui.card_header("Avg Work-Life Balance Score"),
                    ui.h2(ui.output_text("kpi_avg_wlb")),
                    ui.p(
                        ui.em(
                            "Average work-life balance score for the filtered employees."
                        )
                    ),
                ),
                col_widths=(3, 3, 3, 3),
            ),
            
            ui.br(),
            
            # 4 PANELS (2 x 2)
            # Row 1: AI vs Burnout scatter, Burnout by Role bar
            ui.layout_columns(
                ui.card(
                    ui.card_header("AI Usage vs Burnout"),
                    output_widget("plot_ai_vs_burnout"),
                ),
                ui.card(
                    ui.card_header("Burnout Risk by Job Role"),
                    ui.p(ui.em("Observed values are shown; prediction overlay is planned for a later milestone.")),
                    output_widget("plot_burnout_by_role"),
                ),
                col_widths=(6, 6),
            ),
            
            ui.br(),
            
            # Row 2: Weekly hours breakdown, Productivity vs Burnout scatter
            ui.layout_columns(
                ui.card(
                    ui.card_header("Weekly Work Hours Breakdown"),
                    output_widget("plot_hours_breakdown"),
                ),
                ui.card(
                    ui.card_header("Productivity vs Burnout Risk Score"),
                    output_widget("plot_prod_vs_burnout"),
                ),
                col_widths=(6, 6),
            ),

            ui.br(),
            
            ui.panel_conditional(
                "input.show_debug",
                ui.card(
                    ui.card_header(
                        "Debug (reactive inputs + filtered row count)"
                    ),
                    ui.output_text_verbatim("debug_filters"),
                ),
            ),
        ),
    ),
)


# -------------------------
# Server
# -------------------------
def server(input, output, session):

    # Shared reactive calc (depends on MANY inputs; consumed by multiple outputs)
    @reactive.calc
    def filtered_df() -> pd.DataFrame:
        d = df.copy()

        # Job role

        # AI band (multi)

        # Ranges      

        # Deadline pressure (multi)    

        return d

    # KPIs 
    def _safe_mean(series: pd.Series) -> float | None:
        if series.empty:
            return None
        return float(series.mean())

    @output
    @render.text
    def kpi_avg_burnout():
        d = filtered_df()
        m = _safe_mean(d["burnout_risk_score"])
        return "—" if m is None else f"{m:.2f}"

    @output
    @render.text
    def kpi_avg_productivity():
        d = filtered_df()
        m = _safe_mean(d["productivity_score"])
        return "—" if m is None else f"{m:.1f}"

    @output
    @render.text
    def kpi_avg_wlb():
        d = filtered_df()
        m = _safe_mean(d["work_life_balance_score"])
        return "—" if m is None else f"{m:.2f}"

    @output
    @render.text
    def kpi_burnout_vs_median():
        d = filtered_df()
        m = _safe_mean(d["burnout_risk_score"])
        if m is None or BASELINE_MEDIAN_BURNOUT == 0:
            return "—"
        pct = (m - BASELINE_MEDIAN_BURNOUT) / BASELINE_MEDIAN_BURNOUT * 100.0
        arrow = "▲" if pct > 0 else ("▼" if pct < 0 else "•")
        return f"{arrow}{abs(pct):.1f}%"

    # ---- Plots (Altair) ----
    def _empty_chart(message: str):
        base_chart = (
            alt.Chart(pd.DataFrame({"text": [message]}))
            .mark_text(align="center", baseline="middle", size=14)
            .encode(text="text:N")
            .properties(height=260)
        )
        return alt.JupyterChart(base_chart)

    @output
    @render_widget
    def plot_ai_vs_burnout():
        d = filtered_df()
        if d.empty:
            return ui.HTML(altair_to_html(_empty_chart("No data for current filters.")))

        chart = (
            alt.Chart(d)
            .mark_circle(opacity=0.7)
            .encode(
                x=alt.X(
                    "ai_tool_usage_hours_per_week:Q", title="AI tool usage (hrs/week)"
                ),
                y=alt.Y("burnout_risk_score:Q", title="Burnout risk score"),
                color=alt.Color("deadline_pressure_level:N", title="Deadline pressure"),
                tooltip=[
                    "job_role:N",
                    "experience_years:Q",
                    "ai_tool_usage_hours_per_week:Q",
                    "manual_work_hours_per_week:Q",
                    "burnout_risk_score:Q",
                ],
            )
            .properties(height=260)
        )

        median_line = (
            alt.Chart(pd.DataFrame({"y": [BASELINE_MEDIAN_BURNOUT]}))
            .mark_rule()
            .encode(y="y:Q")
        )

        return alt.JupyterChart(chart + median_line)

    @output
    @render_widget
    def plot_burnout_by_role():
        d = filtered_df()
        if d.empty:
            return ui.HTML(altair_to_html(_empty_chart("No data for current filters.")))

        # mean burnout by role
        summary = (
            d.groupby("job_role", as_index=False)["burnout_risk_score"]
            .mean()
            .rename(columns={"burnout_risk_score": "avg_burnout"})
            .sort_values("avg_burnout", ascending=False)
        )

        chart = (
            alt.Chart(summary)
            .mark_bar()
            .encode(
                x=alt.X("job_role:N", sort="-y", title="Job role"),
                y=alt.Y("avg_burnout:Q", title="Avg burnout risk score"),
                tooltip=["job_role:N", alt.Tooltip("avg_burnout:Q", format=".2f")],
            )
            .properties(height=260)
        )
        return alt.JupyterChart(chart)

    @output
    @render_widget
    def plot_hours_breakdown():
        d = filtered_df()
        if d.empty:
            return ui.HTML(altair_to_html(_empty_chart("No data for current filters.")))

        # Convert focus hours/day to approximate weekly focus hours (5-day workweek assumption for prototype)
        weekly_focus = d["focus_hours_per_day"] * 5.0

        breakdown = pd.DataFrame(
            {
                "category": ["Manual", "Meetings", "Collaboration", "Focus (approx)"],
                "hours": [
                    float(d["manual_work_hours_per_week"].mean()),
                    float(d["meeting_hours_per_week"].mean()),
                    float(d["collaboration_hours_per_week"].mean()),
                    float(weekly_focus.mean()),
                ],
            }
        )

        chart = (
            alt.Chart(breakdown)
            .mark_bar()
            .encode(
                x=alt.X("hours:Q", title="Avg hours per week"),
                y=alt.Y("category:N", sort="-x", title=None),
                tooltip=["category:N", alt.Tooltip("hours:Q", format=".1f")],
            )
            .properties(height=260)
        )

        return alt.JupyterChart(chart)

    @output
    @render_widget
    def plot_prod_vs_burnout():
        d = filtered_df()
        if d.empty:
            return ui.HTML(altair_to_html(_empty_chart("No data for current filters.")))

        chart = (
            alt.Chart(d)
            .mark_circle(opacity=0.7)
            .encode(
                x=alt.X("productivity_score:Q", title="Productivity score"),
                y=alt.Y("burnout_risk_score:Q", title="Burnout risk score"),
                color=alt.Color("ai_band:N", title="AI usage band"),
                tooltip=[
                    "job_role:N",
                    "ai_band:N",
                    "productivity_score:Q",
                    "burnout_risk_score:Q",
                ],
            )
            .properties(height=260)
        )

        vline = (
            alt.Chart(pd.DataFrame({"x": [BASELINE_MEDIAN_PRODUCTIVITY]}))
            .mark_rule()
            .encode(x="x:Q")
        )
        hline = (
            alt.Chart(pd.DataFrame({"y": [BASELINE_MEDIAN_BURNOUT]}))
            .mark_rule()
            .encode(y="y:Q")
        )

        return alt.JupyterChart(chart + vline + hline)

    # Debug panel
    @output
    @render.text
    def debug_filters():
        d = filtered_df()
        return (
            f"job_role={input.job_role()}\n"
            f"ai_band={input.ai_band()}\n"
            f"experience={input.experience()}\n"
            f"ai_usage={input.ai_usage()}\n"
            f"manual_hours={input.manual_hours()}\n"
            f"tasks_automated={input.tasks_automated()}\n"
            f"deadline_pressure={input.deadline_pressure()}\n"
            f"show_pred={input.show_pred()}\n"
            f"filtered_rows={len(d)}"
        )


def altair_to_html(chart: alt.Chart) -> str:
    # Shiny for Python can render HTML; this is a simple, dependency-light way to embed Altair.
    return chart.to_html()


app = App(app_ui, server)
