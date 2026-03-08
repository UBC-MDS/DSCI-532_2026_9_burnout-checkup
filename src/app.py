# src/app.py
# Main Shiny app file defining the UI and server logic. Reads data, sets up reactive

from shiny import App, ui, render, reactive
from shiny.render import DataGrid
from shinywidgets import output_widget, render_altair

import pandas as pd
import altair as alt

from src.constants.paths import FEATURES_PATH, TARGETS_PATH
from src.constants.theme import (
    COLORS,
    deadline_scale,
    ai_band_scale,
    hours_breakdown_scale,
)
from pathlib import Path
from dotenv import load_dotenv
from querychat import QueryChat
from chatlas import ChatAnthropic
import os

load_dotenv()
anthropic_key = os.getenv("ANTHROPIC_API_KEY")

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
BASELINE_MEDIAN_WLB = float(df["work_life_balance_score"].median())
BASELINE_HIGH_BURNOUT = (df["burnout_risk_level"] == "High").mean()

# -------------------------
# QueryChat setup for AI Explorer
# -------------------------
ai_greeting = """
👋 Hi! I’m your AI burnout explorer.

Ask me questions about employee burnout, productivity, AI usage, workload, and work-life balance.

Examples:
- Show employees with high burnout risk
- Show employees with high AI usage and low productivity
- Sort employees by burnout risk from highest to lowest
- Which job roles have the highest burnout risk?
- Show employees with high manual work hours

You can also say Reset to clear the current AI filter/sort.
"""

ai_data_description = """
Employee-level workplace wellbeing and productivity dataset.

Each row represents one employee.

Columns:
- Employee_ID: unique identifier for each employee.
- job_role: employee job role/category.
- experience_years: years of experience.
- ai_tool_usage_hours_per_week: hours per week spent using AI tools.
- tasks_automated_percent: percent of tasks automated with AI/tools.
- manual_work_hours_per_week: hours per week spent on manual work.
- meeting_hours_per_week: hours per week spent in meetings.
- collaboration_hours_per_week: hours per week spent collaborating.
- focus_hours_per_day: average focus/deep work hours per day.
- deadline_pressure_level: categorical deadline pressure level (Low, Medium, High).
- burnout_risk_score: numeric burnout risk score.
- burnout_risk_level: burnout category label.
- productivity_score: numeric productivity score.
- work_life_balance_score: numeric work-life balance score.
- workload_score: derived workload metric combining manual work, meetings, and deadline pressure.
- workload_band: workload category (Low, Medium, High).
- ai_band: AI usage category (Low, Moderate, High).

This dataset can be used to analyze:
- Burnout risk by role or experience
- AI usage patterns across employees
- Links between productivity and burnout
- Work-life balance differences
- Manual work and deadline pressure patterns
- High-risk employee subgroups
"""

qc = QueryChat(
    df.copy(),
    "AIUsageBurnoutCheckup",
    greeting=ai_greeting,
    data_description=ai_data_description,
    client=ChatAnthropic(model="claude-sonnet-4-0"),
)

# -------------------------
# UI
# -------------------------
app_ui = ui.page_fluid(
    # -------------------------
    # Global CSS and font setup
    # -------------------------
    ui.include_css(Path(__file__).parent / "www" / "styles.css"),
    ui.tags.style(
        f"""
        .bslib-sidebar-layout > .sidebar > .sidebar-content {{
            gap: 0 !important;
        }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
        }}

        .kpi-card {{
            background: {COLORS["card_bg"]};
            border-radius: 12px;
            padding: 16px 18px;
            box-shadow: 0 2px 0 rgba(90,45,12,0.25);
            min-height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .kpi-title {{
            font-size: 18px;
            font-weight: 700;
            color: {COLORS["dark_brown"]};
            margin-bottom: 6px;
        }}

        .kpi-value {{
            font-size: 56px;
            line-height: 1;
            font-weight: 800;
            color: {COLORS["dark_brown"]};
        }}

        .kpi-sub {{
            min-height: 20px;
            margin-top: 6px;
            font-size: 14px;
            font-weight: 700;
        }}

        .kpi-sub.up {{
            color: {COLORS["alert_red"]};
        }}

        .kpi-sub.down {{
            color: {COLORS["medium_brown"]};
        }}    
    """
    ),
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap",
        )
    ),
    # -------------------------
    # Main app navigation tabs
    # -------------------------
    ui.navset_tab(
        # ==================================================
        # Dashboard tab
        # ==================================================
        ui.nav_panel(
            "Dashboard",
            ui.layout_sidebar(
                # -------------------------
                # Dashboard sidebar filters
                # -------------------------
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
                        "experience",
                        None,
                        min=exp_min,
                        max=exp_max,
                        value=(exp_min, exp_max),
                    ),
                    ui.br(),
                    ui.h6("Weekly AI Usage:"),
                    ui.input_slider(
                        "ai_usage", None, min=ai_min, max=ai_max, value=(ai_min, ai_max)
                    ),
                    ui.br(),
                    ui.h6("Manual Work Hours:"),
                    ui.input_slider(
                        "manual_hours",
                        None,
                        min=man_min,
                        max=man_max,
                        value=(man_min, man_max),
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
                    ui.input_checkbox(
                        "show_pred", "Show Predicted Risk Overlay", value=True
                    ),
                    ui.input_checkbox("show_debug", "Show debug panel", value=False),
                    ui.br(),
                    ui.input_action_button("reset_btn", "Reset Filters"),
                    width=320,
                ),
                # -------------------------
                # Dashboard main content
                # -------------------------
                ui.div(
                    # -------------------------
                    # KPI row
                    # -------------------------
                    ui.layout_columns(
                        # Average burnout risk score for the filtered employees.
                        # These boxes are ordered this way because the first two are key KPIs and are both lower the better,
                        # while the last two are higher the better.
                        ui.output_ui("burnout_box"),
                        ui.output_ui("high_burnout_perc_box"),
                        ui.output_ui("productivity_box"),
                        ui.output_ui("wlb_box"),
                        col_widths=(3, 3, 3, 3),
                        class_="kpi-grid",
                    ),
                    ui.br(),
                    # -------------------------
                    # Dashboard plots - row 1
                    # -------------------------
                    ui.layout_columns(
                        ui.card(
                            ui.card_header("AI Usage vs Burnout"),
                            output_widget("plot_ai_vs_burnout"),
                        ),
                        ui.card(
                            ui.card_header("Burnout Risk by Job Role"),
                            # ui.p(ui.em("Observed values are shown; prediction overlay is planned for a later milestone.")),
                            output_widget("plot_burnout_by_role"),
                        ),
                        col_widths=(6, 6),
                    ),
                    ui.br(),
                    # -------------------------
                    # Dashboard plots - row 2
                    # -------------------------
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
                    # Optional debug panel
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
        ),
        # ==================================================
        # AI Explorer tab
        # ==================================================
        ui.nav_panel(
            "AI Explorer",
            ui.layout_sidebar(
                # -------------------------
                # AI Explorer sidebar
                # -------------------------
                ui.sidebar(
                    ui.h3("AI Explorer"),
                    ui.p("Use natural language to explore the filtered dataset."),
                    qc.ui(),
                    ui.hr(),
                    ui.input_action_button("reset_ai_query", "Reset AI filters"),
                    width=320,
                ),
                # -------------------------
                # AI Explorer main content
                # -------------------------
                ui.div(
                    # -------------------------
                    # AI Explorer KPI row
                    # -------------------------
                    ui.layout_columns(
                        ui.output_ui("ai_count_box"),
                        ui.output_ui("ai_burnout_box"),
                        ui.output_ui("ai_productivity_box"),
                        ui.output_ui("ai_high_burnout_box"),
                        col_widths=(3, 3, 3, 3),
                        class_="kpi-grid",
                    ),
                    ui.br(),
                    # -------------------------
                    # AI Explorer table preview
                    # -------------------------
                    ui.card(
                        ui.card_header(
                            ui.output_text("ai_title"),
                            ui.download_button(
                                "download_ai_data",
                                "Download AI-filtered data",
                            ),
                            class_="d-flex justify-content-between align-items-center",
                        ),
                        ui.output_data_frame("ai_table"),
                    ),
                ),
            ),
        ),
    ),
)


# -------------------------
# Server
# -------------------------
def server(input, output, session):
    @reactive.effect
    @reactive.event(input.reset_btn)
    def _reset_filters():

        # Reset selectize inputs
        ui.update_selectize("job_role", selected="All")
        ui.update_selectize("ai_band", selected=["All"])

        # Reset sliders
        ui.update_slider("experience", value=(exp_min, exp_max))
        ui.update_slider("ai_usage", value=(ai_min, ai_max))
        ui.update_slider("manual_hours", value=(man_min, man_max))
        ui.update_slider("tasks_automated", value=(task_min, task_max))

        # Reset checkbox group
        ui.update_checkbox_group("deadline_pressure", selected=deadline_choices)

        # Reset checkboxes
        ui.update_checkbox("show_pred", value=True)
        ui.update_checkbox("show_debug", value=False)

    @reactive.calc
    def filtered_df():
        d = df

        # job role
        if input.job_role() != "All":
            d = d[d["job_role"] == input.job_role()]

        # ai band
        if "All" not in input.ai_band():
            d = d[d["ai_band"].astype(str).isin(input.ai_band())]

        # experience
        d = d[
            (d["experience_years"] >= input.experience()[0])
            & (d["experience_years"] <= input.experience()[1])
        ]

        # ai usage
        d = d[
            (d["ai_tool_usage_hours_per_week"] >= input.ai_usage()[0])
            & (d["ai_tool_usage_hours_per_week"] <= input.ai_usage()[1])
        ]

        # manual hours
        d = d[
            (d["manual_work_hours_per_week"] >= input.manual_hours()[0])
            & (d["manual_work_hours_per_week"] <= input.manual_hours()[1])
        ]

        # tasks automated
        d = d[
            (d["tasks_automated_percent"] >= input.tasks_automated()[0])
            & (d["tasks_automated_percent"] <= input.tasks_automated()[1])
        ]

        # deadline pressure
        d = d[d["deadline_pressure_level"].isin(input.deadline_pressure())]

        return d

    # -------------------------
    # QueryChat server values for AI Explorer
    # -------------------------
    qc_vals = qc.server()

    # ai filtered df returned by QueryChat
    @reactive.calc
    @reactive.event(input.run_ai_query)
    def ai_filtered_df():
        result = qc_vals.df()

        # convert querychat df to pandas df (code generated with GPT-5)
        if hasattr(result, "to_native"):
            return result.to_native()
        return result

    # title output
    @render.text
    def ai_title():
        return qc_vals.title() or "Preview of AI-filtered data"

    # reset button for AI filters
    @reactive.effect
    @reactive.event(input.reset_ai_query)
    def _reset_ai_query():
        qc_vals.sql("")
        qc_vals.title(None)

    # KPIs
    def kpi_card(title: str, value: str, sub: str = "", sub_class: str = ""):
        return ui.div(
            ui.div(title, class_="kpi-title"),
            ui.div(value, class_="kpi-value"),
            # Always render this div to keep consistent height
            ui.div(sub, class_=f"kpi-sub {sub_class}"),
            class_="kpi-card",
        )

    def _safe_mean(series: pd.Series) -> float | None:
        if series.empty:
            return None
        return float(series.mean())

    def _safe_median(series: pd.Series) -> float | None:
        if series.empty:
            return None
        val = series.median()
        if pd.isna(val):
            return None
        return float(val)

    @render.ui
    def productivity_box():
        d = filtered_df()
        val = _safe_median(d["productivity_score"])

        if val is None:
            return kpi_card("Median Productivity", "—")

        diff = (val - BASELINE_MEDIAN_PRODUCTIVITY) / BASELINE_MEDIAN_PRODUCTIVITY
        arrow = "▲" if diff > 0 else "▼" if diff < 0 else "→"

        # Higher productivity is good
        sub_class = "down" if diff > 0 else "up" if diff < 0 else ""

        return kpi_card(
            "Median Productivity",
            f"{val:.1f}",
            f"{arrow} {abs(diff)*100:.0f}% vs baseline",
            sub_class,
        )

    # percentage of employees in the filtered set that are at high risk of burnout,
    # compared to company-wide baseline percentage.
    @render.ui
    def high_burnout_perc_box():
        d = filtered_df()
        if d.empty:
            return kpi_card("High Burnout %", "—")

        pct = (d["burnout_risk_level"] == "High").mean()
        diff = (pct - BASELINE_HIGH_BURNOUT) / BASELINE_HIGH_BURNOUT
        arrow = "▲" if diff > 0 else "▼" if diff < 0 else "→"

        sub_class = "up" if diff > 0 else "down" if diff < 0 else ""

        return kpi_card(
            "High Burnout %",
            f"{pct*100:.1f}%",
            f"{arrow} {abs(diff)*100:.0f}% vs baseline",
            sub_class,
        )

    @render.ui
    def burnout_box():
        d = filtered_df()
        val = _safe_median(d["burnout_risk_score"])
        if val is None:
            return kpi_card("Median Burnout Risk Score", "—")

        diff = (val - BASELINE_MEDIAN_BURNOUT) / BASELINE_MEDIAN_BURNOUT
        arrow = "▲" if diff > 0 else "▼" if diff < 0 else "→"
        sub_class = "up" if diff > 0 else "down" if diff < 0 else ""

        return kpi_card(
            "Median Burnout Risk Score",
            f"{val:.1f}",
            f"{arrow} {abs(diff)*100:.0f}% vs baseline",
            sub_class,
        )

    @render.ui
    def wlb_box():
        d = filtered_df()
        val = _safe_median(d["work_life_balance_score"])
        if val is None:
            return kpi_card("Median Work-Life Balance Score", "—")

        diff = (val - BASELINE_MEDIAN_WLB) / BASELINE_MEDIAN_WLB
        arrow = "▲" if diff > 0 else "▼" if diff < 0 else "→"

        sub_class = "down" if diff > 0 else "up" if diff < 0 else ""

        return kpi_card(
            "Median Work-Life Balance Score",
            f"{val:.1f}",
            f"{arrow} {abs(diff)*100:.0f}% vs baseline",
            sub_class,
        )

    # -------------------------
    # AI Explorer KPIs
    # -------------------------

    # Number of employees returned by the AI-filtered subset
    @render.ui
    def ai_count_box():
        d = ai_filtered_df()

        if d.empty:
            return kpi_card("Employees Found", "0")

        return kpi_card(
            "Employees Found",
            f"{len(d):,}",
            "Rows returned by AI query",
            "",
        )

    # Median burnout risk score for the AI-filtered subset,
    # compared to the company-wide baseline median.
    @render.ui
    def ai_burnout_box():
        d = ai_filtered_df()
        val = _safe_median(d["burnout_risk_score"])

        if val is None:
            return kpi_card("Median Burnout Risk Score", "—")

        diff = (val - BASELINE_MEDIAN_BURNOUT) / BASELINE_MEDIAN_BURNOUT
        arrow = "▲" if diff > 0 else "▼" if diff < 0 else "→"
        sub_class = "up" if diff > 0 else "down" if diff < 0 else ""

        return kpi_card(
            "Median Burnout Risk Score",
            f"{val:.1f}",
            f"{arrow} {abs(diff)*100:.0f}% vs baseline",
            sub_class,
        )

    # Median productivity score for the AI-filtered subset,
    # compared to the company-wide baseline median
    @render.ui
    def ai_productivity_box():
        d = ai_filtered_df()
        val = _safe_median(d["productivity_score"])

        if val is None:
            return kpi_card("Median Productivity", "—")

        diff = (val - BASELINE_MEDIAN_PRODUCTIVITY) / BASELINE_MEDIAN_PRODUCTIVITY
        arrow = "▲" if diff > 0 else "▼" if diff < 0 else "→"

        # Higher productivity is good
        sub_class = "down" if diff > 0 else "up" if diff < 0 else ""

        return kpi_card(
            "Median Productivity",
            f"{val:.1f}",
            f"{arrow} {abs(diff)*100:.0f}% vs baseline",
            sub_class,
        )

    # Percentage of employees in the AI-filtered subset that are at high burnout risk,
    # compared to the company-wide baseline percentage
    @render.ui
    def ai_high_burnout_box():
        d = ai_filtered_df()

        if d.empty:
            return kpi_card("High Burnout %", "—")

        pct = (d["burnout_risk_level"] == "High").mean()
        diff = (pct - BASELINE_HIGH_BURNOUT) / BASELINE_HIGH_BURNOUT
        arrow = "▲" if diff > 0 else "▼" if diff < 0 else "→"
        sub_class = "up" if diff > 0 else "down" if diff < 0 else ""

        return kpi_card(
            "High Burnout %",
            f"{pct*100:.1f}%",
            f"{arrow} {abs(diff)*100:.0f}% vs baseline",
            sub_class,
        )

    # Plots (Altair)
    def _empty_chart(message: str) -> alt.Chart:
        return (
            alt.Chart(pd.DataFrame({"text": [message]}))
            .mark_text(align="center", baseline="middle", size=14)
            .encode(text="text:N")
            .properties(height=260)
        )

    @output
    @render_altair
    def plot_ai_vs_burnout():
        d = filtered_df()
        if d.empty:
            return _empty_chart("No data for current filters.")

        chart = (
            alt.Chart(d)
            .mark_circle(opacity=0.7)
            .encode(
                x=alt.X(
                    "ai_tool_usage_hours_per_week:Q", title="AI tool usage (hrs/week)"
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
            .properties(height=260)
        )

        median_line = (
            alt.Chart(pd.DataFrame({"y": [BASELINE_MEDIAN_BURNOUT]}))
            .mark_rule(color=COLORS["alert_red"], strokeDash=[6, 4])
            .encode(y="y:Q")
        )

        return chart + median_line

    @output
    @render_altair
    def plot_burnout_by_role():
        d = filtered_df()
        if d.empty:
            return _empty_chart("No data for current filters.")

        # mean burnout by role
        summary = (
            d.groupby("job_role", as_index=False)["burnout_risk_score"]
            .mean()
            .rename(columns={"burnout_risk_score": "avg_burnout"})
            .sort_values("avg_burnout", ascending=False)
        )

        chart = (
            alt.Chart(summary)
            .mark_bar(color=COLORS["medium_brown"])
            .encode(
                x=alt.X("job_role:N", sort="-y", title="Job role"),
                y=alt.Y("avg_burnout:Q", title="Avg burnout risk score"),
                tooltip=["job_role:N", alt.Tooltip("avg_burnout:Q", format=".2f")],
            )
            .properties(height=260)
        )
        return chart

    @output
    @render_altair
    def plot_hours_breakdown():
        d = filtered_df()
        if d.empty:
            return _empty_chart("No data for current filters.")

        # Convert focus hours/day to approximate weekly focus hours (5-day workweek assumption)
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
            return _empty_chart("No hours available for current filters.")

        breakdown["pct"] = breakdown["hours"] / total
        breakdown["pct_label"] = (breakdown["pct"] * 100).round(0).astype(int).astype(
            str
        ) + "%"

        pie = (
            alt.Chart(breakdown)
            .mark_arc()
            .encode(
                theta=alt.Theta("hours:Q", title=None),
                color=alt.Color(
                    "category:N",
                    title=None,
                    scale=alt.Scale(
                        domain=[
                            "Meetings",
                            "Collaboration",
                            "Deep work",
                            "Manual work",
                        ],
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
            .properties(height=260)
        )

        return pie

    @output
    @render_altair
    def plot_prod_vs_burnout():
        d = filtered_df()
        if d.empty:
            return _empty_chart("No data for current filters.")

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
            .properties(height=260)
        )

        vline = (
            alt.Chart(pd.DataFrame({"x": [BASELINE_MEDIAN_PRODUCTIVITY]}))
            .mark_rule(color=COLORS["alert_red"], strokeDash=[6, 4])
            .encode(x="x:Q")
        )
        hline = (
            alt.Chart(pd.DataFrame({"y": [BASELINE_MEDIAN_BURNOUT]}))
            .mark_rule(color=COLORS["alert_red"], strokeDash=[6, 4])
            .encode(y="y:Q")
        )

        return chart + vline + hline

    # Render df in AI tab
    @output
    @render.data_frame
    def ai_table():
        return DataGrid(ai_filtered_df().head(10))

    # Download data button in ai tab
    @render.download(filename="ai_filtered_data.csv")
    def download_ai_data():
        yield ai_filtered_df().to_csv(index=False)

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


app = App(app_ui, server)
