from shiny import App, ui, render

# -------------------------
# UI
# -------------------------
app_ui = ui.page_fluid(
    ui.tags.style("""
        .bslib-sidebar-layout > .sidebar > .sidebar-content {
            gap: 0 !important;
        }
        """),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3("AI Usage &\nBurnout Checkup"),
            ui.hr(),
            ui.h6("Employee ID:"),
            ui.input_selectize(
                "employee_id",
                None,
                choices=["All"],  # TODO: populate from data
                selected="All",
            ),
            ui.br(),
            ui.h6("Job Role:"),
            ui.input_selectize(
                "job_role",
                None,
                choices=["All"],  # TODO: populate from data
                selected=["All"],
                multiple=True,
            ),
            ui.br(),
            ui.h6("Experience (years):"),
            ui.input_slider("experience", None, min=0, max=30, value=(0, 30)),
            ui.br(),
            ui.h6("Weekly AI Usage:"),
            ui.input_slider("ai_usage", None, min=0, max=40, value=(0, 40)),
            ui.br(),
            ui.h6("Manual Work Hours:"),
            ui.input_slider("manual_hours", None, min=0, max=60, value=(0, 60)),
            ui.br(),
            ui.h6("Tasks Automated:"),
            ui.input_slider("tasks_automated", None, min=0, max=100, value=(0, 100)),
            ui.br(),
            ui.h6("Deadline Pressure:"),
            ui.input_checkbox_group(
                "deadline_pressure",
                None,
                choices=["Low", "Medium", "High"],
                selected=["Low", "Medium", "High"],
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
                    ui.card_header("Development utility: echoes filter values to validate reactivity"),
                    ui.output_text_verbatim("debug_filters"),
                )
            )            
        ),
    ),
)


# -------------------------
# Server
# -------------------------
def server(input, output, session):
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
