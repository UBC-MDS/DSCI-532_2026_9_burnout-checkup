# src/app.py
# Main Shiny app file defining the UI and server logic. Reads data, sets up reactive

from shiny import App, ui, render, reactive
from shiny.render import DataGrid
from shinywidgets import output_widget, render_altair
import ibis
from ibis import _
import re
import pandas as pd

from src.constants.paths import FEATURES_PATH, TARGETS_PATH
from src.constants.paths import PARQUET_PATH 
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
con = ibis.duckdb.connect()
table = con.read_parquet(PARQUET_PATH)

df = load_dashboard_data()  # still load in full dataframe used for baselines and querychat
default_ai_preview_df = df.head(100).copy()

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
👋 Hi! I'm your AI burnout explorer.

You can ask questions about:

- burnout risk
- AI usage
- productivity
- workload patterns

Examples:
- Which job roles have the highest burnout risk?
- Does higher AI usage relate to burnout?
- Show employees with high burnout risk.

You can also press Reset to clear the current AI filter/sort.
"""

# -------------------------
# QueryChat tool interception
# -------------------------
blocking_logs = []

def block_broad_tool_request(req):
    """Intercept QueryChat tool calls and block overly broad SQL queries."""
    tool_name = req.name
    arguments = req.arguments or {}
    query_text = arguments.get("query", "")
    query_upper = query_text.upper()

    has_select_all = "SELECT *" in query_upper
    has_where = "WHERE" in query_upper
    has_group_by = "GROUP BY" in query_upper
    has_limit = "LIMIT" in query_upper

    should_block = (
        has_select_all
        and not has_where
        and not has_group_by
        and not has_limit
    )

    reason = None
    if should_block:
        reason = "That request is too broad. Please narrow it with a filter, grouping, or limit."

    blocking_logs.append(
        {
            "tool_name": tool_name,
            "query": query_text,
            "blocked": should_block,
            "reason": reason,
        }
    )

    if should_block:
        raise Exception(reason)


llm_client = ChatAnthropic(model="claude-sonnet-4-0")
llm_client.on_tool_request(block_broad_tool_request)

qc = QueryChat(
    df.copy(),
    "AIUsageBurnoutCheckup",
    greeting=ai_greeting,
    prompt_template=Path(__file__).parent / "prompts" / "system_prompt.md",
    client=llm_client,
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
                        selected=["Manager"],
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

    # Reset filters button - resets all filters to default values
    @reactive.effect
    @reactive.event(input.reset_btn)
    def _reset_filters():

        # Reset selectize inputs
        ui.update_selectize("job_role", selected=["All"])
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

    # -------------------------
    # Dashboard filters
    # -------------------------
    # Reactive expression for the filtered dataframe based on sidebar inputs
    @reactive.calc
    def filtered_df():

        expr = table

        if input.job_role() and "All" not in input.job_role():
            expr = expr.filter(_.job_role.isin(input.job_role()))

        if input.ai_band() and "All" not in input.ai_band():
            expr = expr.filter(_.ai_band.isin(input.ai_band()))

        lo, hi = input.experience()
        expr = expr.filter(_.experience_years.between(lo, hi))

        lo, hi = input.ai_usage()
        expr = expr.filter(_.ai_tool_usage_hours_per_week.between(lo, hi))

        lo, hi = input.manual_hours()
        expr = expr.filter(_.manual_work_hours_per_week.between(lo, hi))

        lo, hi = input.tasks_automated()
        expr = expr.filter(_.tasks_automated_percent.between(lo, hi))

        if input.deadline_pressure():
            expr = expr.filter(_.deadline_pressure_level.isin(input.deadline_pressure()))

        return expr.execute()

    # -------------------------
    # QueryChat server values for AI Explorer
    # -------------------------
    qc_vals = qc.server()

    # ai filtered df returned by QueryChat
    @reactive.calc
    def ai_filtered_df():
        current_sql = qc_vals.sql()
        result = qc_vals.df()

        # No AI query has been run yet -> show preview only
        if not current_sql:
            return default_ai_preview_df

        # Valid AI query returned a dataframe -> show all matched rows
        if isinstance(result, pd.DataFrame):
            return result

        # Fallback if something unexpected happens
        return default_ai_preview_df

    # title output
    @render.text
    def ai_title():
        return qc_vals.title() if qc_vals.sql() else "Preview of first 100 rows"

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

    # Median work-life balance score for the filtered employees,
    # compared to the company-wide baseline median.
    @render.ui
    def burnout_box():
        return median_metric_card(
            filtered_df(),
            column="burnout_risk_score",
            title="Median Burnout Risk Score",
            baseline=BASELINE_MEDIAN_BURNOUT,
            higher_is_better=False,
        )

    # Median work-life balance score for the filtered employees,
    # compared to the company-wide baseline median.        
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
    # (i.e. the number of rows in the dataframe)
    @render.ui
    def ai_count_box():
        subtitle = (
            "Rows returned by AI query"
            if qc_vals.sql()
            else "Rows shown in default preview"
        )
        return count_card(
            ai_filtered_df(),
            title="Employees Found",
            subtitle=subtitle,
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
    # (scatter plot with a reference median burnout line)
    @output
    @render_altair
    def plot_ai_vs_burnout():
        return make_ai_vs_burnout_chart(
            filtered_df(),
            baseline_median_burnout=BASELINE_MEDIAN_BURNOUT,
        )

    # Render burnout by role chart
    # (bar chart of average burnout risk score by job role)
    @output
    @render_altair
    def plot_burnout_by_role():       
        return make_burnout_by_role_chart(filtered_df())

    # Render hours breakdown chart
    # (stacked bar chart of average hours spent on manual work, meetings, and collaboration)
    @output
    @render_altair
    def plot_hours_breakdown():
        return make_hours_breakdown_chart(filtered_df())

    # Render productivity vs burnout chart
    # (scatter plot with productivity on x-axis and burnout risk score on y-axis, with reference median lines for both)
    @output
    @render_altair
    def plot_prod_vs_burnout():
        return make_productivity_vs_burnout_chart(
            filtered_df(),
            baseline_median_productivity=BASELINE_MEDIAN_PRODUCTIVITY,
            baseline_median_burnout=BASELINE_MEDIAN_BURNOUT,
        )

    # Render df in AI tab
    # (data grid)
    @output
    @render.data_frame
    def ai_table():
        return DataGrid(ai_filtered_df())

    # Download data button in ai tab
    @render.download(filename="ai_filtered_data.csv")
    def download_ai_data():
        yield ai_filtered_df().to_csv(index=False)

    # Debug panel output showing current filter values and number of rows in the filtered dataframe
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
