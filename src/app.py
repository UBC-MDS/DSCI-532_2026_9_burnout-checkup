# src/app.py
# Main Shiny app file defining the UI and server logic. Reads data, sets up reactive

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_altair

import pandas as pd
import altair as alt

from src.constants.paths import FEATURES_PATH, TARGETS_PATH
from src.constants.theme import COLORS, deadline_scale, ai_band_scale, hours_breakdown_scale
from pathlib import Path

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
BASELINE_MEDIAN_WLB = float(df["work_life_balance_score"].median())
BASELINE_HIGH_BURNOUT = (
    (df["burnout_risk_level"] == "High").mean()
)

# -------------------------
# UI
# -------------------------
app_ui = ui.page_fluid(
    ui.include_css(Path(__file__).parent / "www" / "styles.css"),
    ui.tags.style(f"""
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
    """),
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap",
        )
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
            ui.br(),
            ui.input_action_button("reset_btn", "Reset Filters"),
            width=320,
        ),
        # -------------------------
        # MAIN CONTENT
        # -------------------------
        ui.div(
            # KPI ROW (4 KPIs)
            ui.layout_columns(
                # # Average burnout risk score for the filtered employees.
                # ui.card(
                #     ui.card_header("Avg Burnout Risk Score"),
                #     ui.h2(ui.output_text("kpi_avg_burnout")),
                # ),
                # ui.card(
                #     ui.card_header("Avg Productivity Score"),
                #     ui.h2(ui.output_text("kpi_avg_productivity")),
                #     # ui.p(
                #     #     ui.em("Average productivity score for the filtered employees.")
                #     # ),
                # ),
                # ui.card(
                #     ui.card_header("Burnout vs Median (%)"),
                #     ui.h2(ui.output_text("kpi_burnout_vs_median")),
                #     ui.p(
                #         # ui.em(
                #         #     "Percentage difference between filtered burnout score and company median."
                #         # )
                #     ),
                # ),
                # ui.card(
                #     ui.card_header("Avg Work-Life Balance Score"),
                #     ui.h2(ui.output_text("kpi_avg_wlb")),
                #     ui.p(
                #         # ui.em(
                #         #     "Average work-life balance score for the filtered employees."
                #         # )
                #     ),
                # ),
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
            # 4 PANELS (2 x 2)
            # Row 1: AI vs Burnout scatter, Burnout by Role bar
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
                    ui.card_header("Debug (reactive inputs + filtered row count)"),
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
    
    # Comparison helper for KPIs, returns theme and badge text based on how current value compares to baseline.
    def compare(current, baseline, higher_is_better=True):
        if baseline == 0 or current is None or pd.isna(current):
            return dict(theme="secondary", badge="no data")

        pct = (current - baseline) / abs(baseline) * 100
        abs_pct = abs(pct)

        # small change treated as stable
        if abs_pct < 1:
            return dict(theme="secondary", badge="≈ same as company baseline")

        is_good = (pct > 0) if higher_is_better else (pct < 0)

        if is_good and abs_pct >= 5:
            theme = "success"
        elif is_good:
            theme = "info"
        elif abs_pct >= 5:
            theme = "warning"
        else:
            theme = "danger"

        arrow = "▲" if pct > 0 else "▼"
        badge = f"{arrow}{abs_pct:.1f}% vs company median"

        return dict(theme=theme, badge=badge)

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
        # if val is None:
        #     return ui.value_box("Median Productivity", "—", theme="secondary")

        # cmp = compare(val, BASELINE_MEDIAN_PRODUCTIVITY, higher_is_better=True)

        # return ui.value_box(
        #     "Median Productivity",
        #     f"{val:.1f}",
        #     ui.tags.div(cmp["badge"], class_="small"),
        #     theme=cmp["theme"],
        # )

        if val is None:
            return kpi_card("Avg Productivity Score", "—")

        diff = (val - BASELINE_MEDIAN_PRODUCTIVITY) / BASELINE_MEDIAN_PRODUCTIVITY
        arrow = "▲" if diff > 0 else "▼" if diff < 0 else "→"

        # Higher productivity is GOOD
        sub_class = "down" if diff > 0 else "up" if diff < 0 else ""

        return kpi_card(
            "Avg Productivity Score",
            f"{val:.1f}",
            f"{arrow} {abs(diff)*100:.0f}% vs baseline",
            sub_class,
        )
    
    # percentage of employees in the filtered set that are at high risk of burnout, 
    # compared to company-wide baseline percentage.
    @render.ui
    def high_burnout_perc_box():
        d = filtered_df()
        # if d.empty:
        #     return ui.value_box("High Burnout %", "—", theme="secondary")

        # pct = (d["burnout_risk_level"] == "High").mean()
        # cmp = compare(pct, BASELINE_HIGH_BURNOUT, higher_is_better=False)

        # return ui.value_box(
        #     "High Burnout %",
        #     f"{pct*100:.1f}%",
        #     ui.tags.div(cmp["badge"], class_="small"),
        #     theme=cmp["theme"],
        # )
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
        # if val is None:
        #     return ui.value_box("Median Burnout Risk", "—", theme="secondary")

        # cmp = compare(val, BASELINE_MEDIAN_BURNOUT, higher_is_better=False)

        # return ui.value_box(
        #     "Median Burnout Risk",
        #     f"{val:.2f}",
        #     ui.tags.div(cmp["badge"], class_="small"),
        #     theme=cmp["theme"],
        # )
        if val is None:
            return kpi_card("Avg Productivity Score", "—")

        return kpi_card("Avg Productivity Score", f"{val:.1f}")
          
    @render.ui
    def wlb_box():
        d = filtered_df()
        val = _safe_median(d["work_life_balance_score"])
        # if val is None:
        #     return ui.value_box("Median Work-Life Balance", "—", theme="secondary")

        # cmp = compare(val, BASELINE_MEDIAN_WLB, higher_is_better=True)

        # return ui.value_box(
        #     "Median Work-Life Balance",
        #     f"{val:.2f}",
        #     ui.tags.div(cmp["badge"], class_="small"),
        #     theme=cmp["theme"],
        # )
        if val is None:
            return kpi_card("Avg Work-Life Balance Score", "—")

        diff = (val - BASELINE_MEDIAN_WLB) / BASELINE_MEDIAN_WLB
        arrow = "▲" if diff > 0 else "▼" if diff < 0 else "→"

        sub_class = "down" if diff > 0 else "up" if diff < 0 else ""

        return kpi_card(
            "Avg Work-Life Balance Score",
            f"{val:.1f}",
            f"{arrow} {abs(diff)*100:.0f}% vs baseline",
            sub_class,
        )
    
    
    # changed card to value box, keeping old code for reference.
    # @output
    # @render.text
    # def kpi_avg_burnout():
    #     d = filtered_df()
    #     m = _safe_mean(d["burnout_risk_score"])
    #     return "—" if m is None else f"{m:.2f}"

    # @output
    # @render.text
    # def kpi_avg_productivity():
    #     d = filtered_df()
    #     m = _safe_mean(d["productivity_score"])
    #     return "—" if m is None else f"{m:.1f}"

    # @output
    # @render.text
    # def kpi_avg_wlb():
    #     d = filtered_df()
    #     m = _safe_mean(d["work_life_balance_score"])
    #     return "—" if m is None else f"{m:.2f}"

    # @output
    # @render.text
    # def kpi_burnout_vs_median():
    #     d = filtered_df()
    #     med = float(d["burnout_risk_score"].median()) if d is not None and len(d) else None
    #     if med is None or BASELINE_MEDIAN_BURNOUT == 0:
    #         return "—"
    #     pct = (med - BASELINE_MEDIAN_BURNOUT) / BASELINE_MEDIAN_BURNOUT * 100.0
    #     if pct > 0:
    #         arrow = "▲"
    #     elif pct < 0:
    #         arrow = "▼"
    #     else:
    #         arrow = "→"
    #     return f"{arrow} {abs(pct):.1f}%"

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
                # color=alt.Color("deadline_pressure_level:N", title="Deadline pressure"),
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
                # color=alt.Color("category:N", title=None),
                color=alt.Color(
                    "category:N",
                    title=None,
                    scale=alt.Scale(
                        domain=["Meetings", "Collaboration", "Deep work", "Manual work"],
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
                # color=alt.Color("ai_band:N", title="AI usage band"),
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


# def altair_to_html(chart: alt.Chart) -> str:
#     # Shiny for Python can render HTML; this is a simple, dependency-light way to embed Altair.
#     return chart.to_html()


app = App(app_ui, server)
