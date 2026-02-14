from shiny import App, ui, render

# -------------------------
# UI
# -------------------------
app_ui = ui.page_fluid(
    ui.h2("burnout_checkup"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Filters"),
            ui.input_selectize(
                "job_role",
                "Job Role",
                choices=["All"],  # TODO: populate from data
                selected=["All"],
                multiple=True,
            ),
            ui.input_slider(
                "experience", "Experience (years)", min=0, max=30, value=(0, 30)
            ),
            ui.input_slider(
                "ai_usage", "AI usage (hrs/week)", min=0, max=40, value=(0, 40)
            ),
            ui.input_slider(
                "manual_hours", "Manual work (hrs/week)", min=0, max=60, value=(0, 60)
            ),
            ui.input_checkbox_group(
                "deadline_pressure",
                "Deadline pressure",
                choices=["Low", "Medium", "High"],
                selected=["Low", "Medium", "High"],
            ),
            ui.hr(),
            ui.input_checkbox("show_pred", "Show predicted risk overlay", value=False),
            width=300,
        ),
        # Main content
        ui.div(
            # KPI row (comparison-driven)
            ui.layout_columns(
                ui.card(
                    ui.card_header("% High Burnout (Filtered)"),
                    ui.h2(ui.output_text("kpi_pct_high_burnout")),
                ),
                ui.card(
                    ui.card_header("Burnout vs Company Median"),
                    ui.h2(ui.output_text("kpi_vs_median")),
                    ui.p(ui.em("Difference in % High Burnout")),
                ),
                ui.card(
                    ui.card_header("Difference in Burnout: High AI vs Low AI"),
                    ui.h2(ui.output_text("kpi_delta_ai")),
                    ui.p(ui.em("Workload-controlled comparison (planned)")),
                ),
                ui.card(
                    ui.card_header("Productivity-Burnout Gap"),
                    ui.h2(ui.output_text("kpi_prod_gap")),
                    ui.p(ui.em("Avg Prod (High) - Avg Prod (Low)")),
                ),
                ui.card(
                    ui.card_header("Predicted % High Risk"),
                    ui.h2(ui.output_text("kpi_pred_pct_high")),
                    ui.p(ui.em("Shown only if overlay enabled")),
                ),
                col_widths=(2, 2, 3, 2, 2),
            ),
            ui.br(),
            # Main plots: left large + right stacked
            ui.layout_columns(
                # Panel 1 (large): AI Usage vs Burnout
                ui.card(
                    ui.card_header(
                        "AI Usage vs Burnout (with median reference line)"
                    ),
                    ui.p(
                        "Scatter plot (X = AI usage hrs/week, Y = burnout risk score). "
                        "Color by deadline pressure. Add horizontal reference line = company median burnout. "
                        "If prediction overlay is enabled, highlight/outline predicted high-risk points."
                    ),
                    ui.output_text_verbatim("debug_filters"),
                ),
                # Right column: Burnout by AI group + Productivity vs Burnout
                ui.div(
                    ui.card(
                        ui.card_header(
                            "Burnout by AI Usage Group (Low / Moderate / High)"
                        ),
                        ui.p(
                            "Bar chart showing % High Burnout per AI group, "
                            "with company median as a dashed reference line."
                        ),
                        ui.input_radio_buttons(
                            "observed_pred",
                            "Display mode",
                            choices=["Observed", "Predicted (optional)"],
                            selected="Observed",
                            inline=True,
                        ),
                    ),
                    ui.br(),
                    ui.card(
                        ui.card_header("Productivity vs Burnout (quadrant view)"),
                        ui.p(
                            "Scatter plot (X = productivity score, Y = burnout risk score). "
                            "Color by AI usage group. Add quadrant guides to flag high-prod/high-burnout scenarios."
                        ),
                    ),
                ),
                col_widths=(7, 5),
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
    def kpi_pct_high_burnout():
        return "xx%"

    @output
    @render.text
    def kpi_vs_median():
        # Example format: "+6.2%"
        return "+x.x%"

    @output
    @render.text
    def kpi_delta_ai():
        # Example format: "+4.5%"
        return "+x.x%"

    @output
    @render.text
    def kpi_prod_gap():
        # Example format: "-3.1 pts"
        return "-x.x"

    @output
    @render.text
    def kpi_pred_pct_high():
        return "xx%" if input.show_pred() else "—"

    # Temporary debug output to confirm inputs are reactive and connected (M1 scaffold)
    @output
    @render.text
    def debug_filters():
        return (
            f"job_role={input.job_role()}\n"
            f"experience={input.experience()}\n"
            f"ai_usage={input.ai_usage()}\n"
            f"manual_hours={input.manual_hours()}\n"
            f"deadline_pressure={input.deadline_pressure()}\n"
            f"show_pred={input.show_pred()}\n"
            f"display_mode={input.observed_pred()}"
        )


app = App(app_ui, server)
