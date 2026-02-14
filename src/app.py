from shiny import App, ui, render

# -------------------------
# UI
# -------------------------
app_ui = ui.page_fluid(
    # ui.h2("burnout_checkup"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3("AI Usage & Burnout Checkup"),
            ui.h5("Employee ID"),
            ui.input_selectize(
                "employee_id",
                None,
                choices=["All"],  # TODO: populate from data
                selected="All",
            ),
            ui.h5("Job Role"),
            ui.input_selectize(
                "job_role",
                None,
                choices=["All"],  # TODO: populate from data
                selected=["All"],
                multiple=True,
            ),
            ui.h5("Experience (years)"),
            ui.input_slider("experience", None, min=0, max=30, value=(0, 30)),
            ui.h5("Weekly AI Usage (hrs)"),
            ui.input_slider("ai_usage", None, min=0, max=40, value=(0, 40)),
            ui.h5("Manual Work Hours (hrs)"),
            ui.input_slider("manual_hours", None, min=0, max=60, value=(0, 60)),
            ui.h5("Tasks Automated (%)"),
            ui.input_slider("tasks_automated", None, min=0, max=100, value=(0, 100)),
            ui.h5("Deadline Pressure"),
            ui.input_checkbox_group(
                "deadline_pressure",
                None,
                choices=["Low", "Medium", "High"],
                selected=["Low", "Medium", "High"],
                inline=True,
            ),
            ui.hr(),
            ui.input_checkbox("show_pred", "Show predicted risk overlay", value=True),
            width=320,
        ),
        # -------------------------
        # MAIN CONTENT
        # -------------------------
        ui.div(
            # ---- KPI ROW (4) ----
            ui.layout_columns(
                ui.card(
                    ui.card_header("% Avg Burnout Risk Score"),
                    ui.h2(ui.output_text("kpi_avg_burnout")),
                    ui.p(
                        ui.em(
                            "Placeholder: % of filtered employees classified as High burnout."
                        )
                    ),
                ),
                ui.card(
                    ui.card_header("Burnout vs Company Median"),
                    ui.h2(ui.output_text("kpi_vs_median")),
                    ui.p(ui.em("Placeholder: difference vs overall company baseline.")),
                ),
                ui.card(
                    ui.card_header("Burnout Diff (High AI vs Low AI)"),
                    ui.h2(ui.output_text("kpi_delta_ai")),
                    ui.p(
                        ui.em(
                            "Placeholder: difference in % high burnout between High vs Low AI groups."
                        )
                    ),
                ),
                ui.card(
                    ui.card_header("Productivity–Burnout Gap"),
                    ui.h2(ui.output_text("kpi_prod_gap")),
                    ui.p(
                        ui.em(
                            "Placeholder: Avg productivity (High burnout) − Avg productivity (Low burnout)."
                        )
                    ),
                ),
                col_widths=(3, 3, 3, 3),
            ),
            ui.br(),
            # ---- PLOTS (4) ----
            ui.layout_columns(
                ui.card(
                    ui.card_header("AI Usage vs Burnout"),
                    ui.p(
                        "Placeholder: Scatter plot (X = AI usage hrs/week, Y = burnout risk score). "
                        "Color by deadline pressure. Add horizontal reference line = company median burnout. "
                        "If prediction overlay is enabled, outline predicted high-risk points."
                    ),
                ),
                ui.card(
                    ui.card_header("Burnout by Role / Prediction View"),
                    ui.input_radio_buttons(
                        "observed_pred",
                        "Display mode",
                        choices=["Observed", "Predicted (optional)"],
                        selected="Observed",
                        inline=True,
                    ),
                    ui.p(
                        "Placeholder: Bar chart comparing burnout risk across job roles (or AI groups). "
                        "Include a dashed reference line for company baseline."
                    ),
                ),
                col_widths=(6, 6),
            ),
            ui.br(),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Weekly Work Hours Breakdown"),
                    ui.p(
                        "Placeholder: Composition chart (pie/stacked bar) showing weekly time allocation across "
                        "manual work, meetings, collaboration, and deep/focus work."
                    ),
                ),
                ui.card(
                    ui.card_header("Productivity vs Burnout (Quadrant View)"),
                    ui.p(
                        "Placeholder: Scatter plot (X = productivity score, Y = burnout risk score). "
                        "Color by AI usage group. Add quadrant guides (median productivity and median burnout)."
                    ),
                ),
                col_widths=(6, 6),
            ),
            ui.br(),
            ui.card(
                ui.card_header("Development utility"),
                ui.p(
                    "Temporary debug output to confirm inputs are reactive and connected (M1 scaffold)."
                ),
                ui.output_text_verbatim("debug_filters"),
            ),
        ),
    ),
)


# -------------------------
# Server
# -------------------------
def server(input, output, session):

    # KPI placeholders (replace with computed values in later milestones)
    @output
    @render.text
    def kpi_avg_burnout():
        return "xx%"

    @output
    @render.text
    def kpi_vs_median():
        return "+x.x pp"  # percentage points

    @output
    @render.text
    def kpi_delta_ai():
        return "+x.x pp"  # percentage points

    @output
    @render.text
    def kpi_prod_gap():
        return "-x.x"  # points

    # Development utility: echoes filter values to validate reactivity during initial scaffold phase
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
