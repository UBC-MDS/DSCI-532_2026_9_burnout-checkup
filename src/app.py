# src/app.py
# Main Shiny app file defining the UI and server logic. Reads data, sets up reactive

from shiny import App, ui, render, reactive
from shiny.render import DataGrid
from shinywidgets import output_widget, render_altair

import pandas as pd

from src.constants.paths import FEATURES_PATH, TARGETS_PATH
from src.constants.theme import (
    COLORS,
    deadline_scale,
    ai_band_scale,
)
from pathlib import Path
from dotenv import load_dotenv
from querychat import QueryChat
from chatlas import ChatAnthropic
import os
from src.data import (
    load_dashboard_data,
    get_baselines,
    get_filter_choices,
    get_slider_ranges,
)
from src.filters import apply_dashboard_filters, normalize_querychat_result
from src.kpis import (
    count_card,
    high_burnout_pct_card,
    kpi_card,
    median_metric_card,
)
from src.charts import (
    make_ai_vs_burnout_chart,
    make_burnout_by_role_chart,
    make_hours_breakdown_chart,
    make_productivity_vs_burnout_chart,
)
from src.utils.debug import format_filter_debug

load_dotenv()
anthropic_key = os.getenv("ANTHROPIC_API_KEY")

# Load and preprocess data
df = load_dashboard_data()

# Input variables' options for filters
filter_choices = get_filter_choices(df)
job_role_choices = filter_choices["job_role_choices"]
ai_band_choices = filter_choices["ai_band_choices"]
deadline_choices = filter_choices["deadline_choices"]

# Slider ranges for numeric filters - experience, ai usage hours, manual hours, tasks automated
slider_ranges = get_slider_ranges(df)
exp_min, exp_max = slider_ranges["experience"]
ai_min, ai_max = slider_ranges["ai_usage"]
man_min, man_max = slider_ranges["manual_hours"]
task_min, task_max = slider_ranges["tasks_automated"]

# Company-wide baselines (computed once, used across outputs)
baselines = get_baselines(df)
BASELINE_MEDIAN_BURNOUT = baselines["median_burnout"]
BASELINE_MEDIAN_PRODUCTIVITY = baselines["median_productivity"]
BASELINE_MEDIAN_WLB = baselines["median_wlb"]
BASELINE_HIGH_BURNOUT = baselines["high_burnout_rate"]

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
                        selected=["All"],
                        multiple=True,
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
                    # ui.p("Use natural language to explore the filtered dataset."),
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
        ui.update_selectize("job_role", selected=["Manager"])
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
        return apply_dashboard_filters(
            df=df,
            job_role=input.job_role(),
            ai_band=input.ai_band(),
            experience=input.experience(),
            ai_usage=input.ai_usage(),
            manual_hours=input.manual_hours(),
            tasks_automated=input.tasks_automated(),
            deadline_pressure=input.deadline_pressure(),
        )

    # -------------------------
    # QueryChat server values for AI Explorer
    # -------------------------
    qc_vals = qc.server()

    # ai filtered df returned by QueryChat
    @reactive.calc
    def ai_filtered_df():
        result = qc_vals.df()
        return normalize_querychat_result(result=result, fallback_df=df)

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

    # -------------------------
    # KPIs
    # -------------------------

    # Returns a KPI card for the median productivity of the filtered employees.
    @render.ui
    def productivity_box():
        return median_metric_card(
            filtered_df(),
            column="productivity_score",
            title="Median Productivity",
            baseline=BASELINE_MEDIAN_PRODUCTIVITY,
            higher_is_better=True,
        )
        
    # percentage of employees in the filtered set that are at high risk of burnout,
    # compared to company-wide baseline percentage.
    @render.ui
    def high_burnout_perc_box():
        return high_burnout_pct_card(
            filtered_df(),
            baseline_high_burnout=BASELINE_HIGH_BURNOUT,
            title="High Burnout %",
        )

    @render.ui
    def burnout_box():
        return median_metric_card(
            filtered_df(),
            column="burnout_risk_score",
            title="Median Burnout Risk Score",
            baseline=BASELINE_MEDIAN_BURNOUT,
            higher_is_better=False,
        )
        
    @render.ui
    def wlb_box():
        return median_metric_card(
            filtered_df(),
            column="work_life_balance_score",
            title="Median Work-Life Balance Score",
            baseline=BASELINE_MEDIAN_WLB,
            higher_is_better=True,
        )

    # -------------------------
    # AI Explorer KPIs
    # -------------------------

    # Number of employees returned by the AI-filtered subset
    @render.ui
    def ai_count_box():
        return count_card(
            ai_filtered_df(),
            title="Employees Found",
            subtitle="Rows returned by AI query",
        )

    # Median burnout risk score for the AI-filtered subset,
    # compared to the company-wide baseline median.
    @render.ui
    def ai_burnout_box():
        return median_metric_card(
            ai_filtered_df(),
            column="burnout_risk_score",
            title="Median Burnout Risk Score",
            baseline=BASELINE_MEDIAN_BURNOUT,
            higher_is_better=False,
        )

    # Median productivity score for the AI-filtered subset,
    # compared to the company-wide baseline median
    @render.ui
    def ai_productivity_box():
        return median_metric_card(
            ai_filtered_df(),
            column="productivity_score",
            title="Median Productivity",
            baseline=BASELINE_MEDIAN_PRODUCTIVITY,
            higher_is_better=True,
        )

    # Percentage of employees in the AI-filtered subset that are at high burnout risk,
    # compared to the company-wide baseline percentage
    @render.ui
    def ai_high_burnout_box():
        return high_burnout_pct_card(
            ai_filtered_df(),
            baseline_high_burnout=BASELINE_HIGH_BURNOUT,
            title="High Burnout %",
        )

    # -------------------------
    # Plots (Altair)
    # -------------------------

    # Render AI usage vs burnout chart
    @output
    @render_altair
    def plot_ai_vs_burnout():
        return make_ai_vs_burnout_chart(
            filtered_df(),
            baseline_median_burnout=BASELINE_MEDIAN_BURNOUT,
        )

    # Render burnout by role chart
    @output
    @render_altair
    def plot_burnout_by_role():       
        return make_burnout_by_role_chart(filtered_df())

    # Render hours breakdown chart
    @output
    @render_altair
    def plot_hours_breakdown():
        return make_hours_breakdown_chart(filtered_df())

    # Render productivity vs burnout chart
    @output
    @render_altair
    def plot_prod_vs_burnout():
        return make_productivity_vs_burnout_chart(
            filtered_df(),
            baseline_median_productivity=BASELINE_MEDIAN_PRODUCTIVITY,
            baseline_median_burnout=BASELINE_MEDIAN_BURNOUT,
        )

    # Render df in AI tab
    @output
    @render.data_frame
    def ai_table():
        return DataGrid(ai_filtered_df())

    # Download data button in ai tab
    @render.download(filename="ai_filtered_data.csv")
    def download_ai_data():
        yield ai_filtered_df().to_csv(index=False)

    # Debug panel
    @output
    @render.text
    def debug_filters():
        return format_filter_debug(
            job_role=input.job_role(),
            ai_band=input.ai_band(),
            experience=input.experience(),
            ai_usage=input.ai_usage(),
            manual_hours=input.manual_hours(),
            tasks_automated=input.tasks_automated(),
            deadline_pressure=input.deadline_pressure(),
            show_pred=input.show_pred(),
            filtered_df=filtered_df(),
        )


app = App(app_ui, server)
