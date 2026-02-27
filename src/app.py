from shiny import App, ui, render
import pandas as pd
from shiny import reactive

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
    df["ai_tool_usage_hours_per_week"], q=3, labels=["Low", "Medium", "High"]
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

# Burnout median for reference in plots
company_median_burnout = float(df["burnout_risk_score"].median())


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
            ui.h6("AI Usage:"),
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
            # KPI ROW (4)
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
            ui.layout_columns(
                ui.card(
                    ui.card_header("AI Usage vs Burnout"),
                    ui.p(
                        "Scatter plot of AI usage hours per week versus burnout risk score. "
                        "Points are grouped by deadline pressure level (Low, Medium, High), and a horizontal "
                        "reference line marks the median burnout score."
                    ),
                ),
                ui.card(
                    ui.card_header("Burnout Risk Score Prediction"),
                    ui.p(
                        "Grouped bar chart showing observed burnout risk scores across job roles. "
                        "Predicted burnout scores may be overlaid to assess divergence between "
                        "observed and model-estimated risk."
                    ),
                ),
                col_widths=(6, 6),
            ),
            ui.br(),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Weekly Work Hours Breakdown"),
                    ui.p(
                        "Pie chart showing the breakdown of weekly work hours across Meetings, Collaboration, "
                        "Deep work, and Manual work for the selected filters."
                    ),
                ),
                ui.card(
                    ui.card_header("Productivity vs Burnout Risk Score"),
                    ui.p(
                        "Scatter plot of productivity score versus burnout risk score. Points are grouped by AI "
                        "usage level (Low, Medium, High), and a horizontal reference line marks the median "
                        "productivity score."
                    ),
                ),
                col_widths=(6, 6),
            ),
            ui.br(),
            ui.panel_conditional(
                "input.show_debug",
                ui.card(
                    ui.card_header(
                        "Development utility: echoes filter values to validate reactivity"
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
    @reactive.calc
    def filtered_df():
        d = df.copy()

        # job role
        if input.job_role() != "All":
            d = d[d["job_role"] == input.job_role()]

        # ai band
        if "All" not in input.ai_band():
            d = d[d["ai_band"].astype(str).isin(input.ai_band())]

        # experience
        d = d[
            (d["experience_years"] >= input.experience()[0]) &
            (d["experience_years"] <= input.experience()[1])
        ]

        # ai usage
        d = d[
            (d["ai_tool_usage_hours_per_week"] >= input.ai_usage()[0]) &
            (d["ai_tool_usage_hours_per_week"] <= input.ai_usage()[1])
        ]

        # manual hours
        d = d[
            (d["manual_work_hours_per_week"] >= input.manual_hours()[0]) &
            (d["manual_work_hours_per_week"] <= input.manual_hours()[1])
        ]

        # tasks automated
        d = d[
            (d["tasks_automated_percent"] >= input.tasks_automated()[0]) &
            (d["tasks_automated_percent"] <= input.tasks_automated()[1])
        ]

        # deadline pressure
        d = d[d["deadline_pressure_level"].isin(input.deadline_pressure())]

        return d

    @output
    @render.text
    def kpi_avg_burnout():
        return "x.x"

    @output
    @render.text
    def kpi_avg_productivity():
        return "xx.x"

    @output
    @render.text
    def kpi_burnout_vs_median():
        return "xx%"

    @output
    @render.text
    def kpi_avg_wlb():
        return "x.x"

    @output
    @render.text
    def debug_filters():
        return (
            f"employee_id={input.employee_id()}\n"
            f"job_role={input.job_role()}\n"
            f"experience={input.experience()}\n"
            f"ai_usage={input.ai_usage()}\n"
            f"manual_hours={input.manual_hours()}\n"
            f"tasks_automated={input.tasks_automated()}\n"
            f"deadline_pressure={input.deadline_pressure()}\n"
            f"show_pred={input.show_pred()}\n"
            f"display_mode={input.observed_pred()}"
        )


app = App(app_ui, server)
