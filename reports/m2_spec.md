# App Specification

## 2.1 Updated Job Stories

| #   | Job Story                       | Status         | Notes                         |
| --- | ------------------------------- | -------------- | ----------------------------- |
| 1   | **When** reviewing employee well-being and productivity reports, **I want to** separate burnout caused by workload from burnout potentially associated with AI usage, **so I can** make informed AI adoption decisions without misattributing the root cause of burnout. | ✅ Implemented | This job story was implemented through interactive filters (job role, AI usage, manual hours, experience) and visual comparisons (AI Usage vs Burnout scatterplot and Burnout Risk by Job Role). These allow users to isolate workload-related factors from AI usage and assess burnout drivers more accurately. |
| 2   | **When** investigating increased burnout within specific teams, **I want to** analyze how AI usage interacts with deadline pressure, **so I can** design targeted interventions such as workload adjustments or AI training. | 🔄 Revised | Changed focus from *task complexity and deadline pressure* to just *deadline pressure* because it is a more directly actionable and interpretable driver of burnout. |
| 3   | **When** evaluating the impact of AI tools on productivity, **I want to** compare productivity gains against changes in burnout risk, **so I can** ensure performance improvements are sustainable and do not harm employee well-being. | ✅ Implemented | This job story was implemented using KPI cards (Avg Productivity Score, High Burnout %) and the Productivity vs Burnout Risk scatterplot. These components enable evaluation of productivity gains and burnout risk, helping users assess whether AI-related performance improvements are sustainable. |

## 2.2 Component Inventory

| ID                | Type          | Shiny widget / renderer | Depends on                   | Job story  |
| ------------------| ------------- | ----------------------- | ---------------------------- | ---------- |
| `job_role`        | Input         | `ui.input_selectize()`  | —                            | #1, #2     |
| `ai_band`         | Input         | `ui.input_selectize()`  | —                            | #1, #3     |
| `experience_years`| Input         | `ui.input_slider()`     | —                            | #1         |
| `ai_tool_usage_hours_per_week`    | Input         | `ui.input_slider()`     | —            | #1, #3     |
| `manual_work_hours_per_week`      | Input         | `ui.input_slider()`     | —            | #1         |
| `tasks_automated_percent`         | Input         | `ui.input_slider()`     | —            | #1         |
| `deadline_pressure_level`         | Input         | `ui.input_checkbox_group()`| —         | #1, #2     |
| `reset_btn`       | Input         | `ui.input_action_button()` | -                         | #1, #2, #3 |
| `filtered_df`     | Reactive calc | `@reactive.calc`        | all inputs above             | #1, #2, #3 |
| `_reset_filters`  | Reactive effect | `@reactive.effect` + `@reactive.event(input.reset_btn)`| `reset_btn`  | #1, #2, #3 |
| `burnout_box`     | Output        | `@render.ui`                | `filtered_df`, baselines              | #1       |
| `productivity_box`| Output        |` @render.ui`                | `filtered_df`, baselines               | #1, #3   |
| `high_burnout_perc_box`   | Output    | `@render.ui`                | `filtered_df`, baselines     | #1       |
| `wlb_box`             | Output    | `@render.ui`                | `filtered_df` , baselines               | #1       |
| `plot_ai_vs_burnout`  | Output    | `@render_altair`              | `filtered_df`, baselines     | #1, #2   |
| `plot_burnout_by_role`| Output    | `@render_altair`              | `filtered_df`                | #2       |
| `plot_hours_breakdown`| Output    | `@render_altair`              | `filtered_df`                | #1       |
| `plot_prod_vs_burnout`| Output    | `@render_altair`              | `filtered_df`, baselines     | #3       |


## 2.3 Reactivity Diagram

```mermaid
flowchart TD

  %% -------------------
  %% Inputs
  %% -------------------
  job_role[/job_role/]
  ai_band[/ai_band/]
  experience_years[/experience_years/]
  ai_tool_usage_hours_per_week[/ai_tool_usage_hours_per_week/]
  manual_work_hours_per_week[/manual_work_hours_per_week/]
  tasks_automated_percent[/tasks_automated_percent/]
  deadline_pressure_level[/deadline_pressure_level/]
  reset_btn[/reset_btn/]

  %% -------------------
  %% Reactives
  %% -------------------
  filtered_df{{filtered_df}}
  reset_effect{{_reset_filters}}

  %% Input -> filtered_df
  job_role --> filtered_df
  ai_band --> filtered_df
  experience_years --> filtered_df
  ai_tool_usage_hours_per_week --> filtered_df
  manual_work_hours_per_week --> filtered_df
  tasks_automated_percent --> filtered_df
  deadline_pressure_level --> filtered_df

  %% Reset button
  reset_btn --> reset_effect

  %% -------------------
  %% Outputs (ui)
  %% -------------------
  burnout_box([burnout_box])
  productivity_box([productivity_box])
  high_burnout_perc_box([high_burnout_perc_box])
  wlb_box([wlb_box])

  %% -------------------
  %% Outputs (plots)
  %% -------------------
  plot_ai_vs_burnout([plot_ai_vs_burnout])
  plot_burnout_by_role([plot_burnout_by_role])
  plot_hours_breakdown([plot_hours_breakdown])
  plot_prod_vs_burnout([plot_prod_vs_burnout])

  %% filtered_df dependencies
  filtered_df --> plot_burnout_by_role
  filtered_df --> plot_hours_breakdown

  %% filtered_df + baselines dependencies
  filtered_df --> burnout_box
  baselines --> burnout_box

  filtered_df --> productivity_box
  baselines --> productivity_box

  filtered_df --> high_burnout_perc_box
  baselines --> high_burnout_perc_box

  filtered_df --> wlb_box
  baselines --> wlb_box

  filtered_df --> plot_ai_vs_burnout
  baselines --> plot_ai_vs_burnout

  filtered_df --> plot_prod_vs_burnout
  baselines --> plot_prod_vs_burnout
```

## 2.4 Calculation Details

### filtered_df (@reactive.calc)

**Depends on:**

- `job_role`
- `ai_band`
- `experience_years`
- `ai_tool_usage_hours_per_week`
- `manual_work_hours_per_week`
- `tasks_automated_percent`
- `deadline_pressure_level`

**Transformation:**
Filters the full dataset to retain only observations matching the selected input criteria by the user.

**Consumed by:**

- `burnout_box`
- `productivity_box`
- `high_burnout_perc_box`
- `wlb_box`
- `plot_ai_vs_burnout`
- `plot_burnout_by_role`
- `plot_hours_breakdown`
- `plot_prod_vs_burnout`


## 2.5 AI Explorer (QueryChat)

### AI Prompt

The dashboard includes an AI assistant powered by QueryChat that allows users to ask questions about the dataset.

The system prompt was customized to reflect the dashboard’s target audience (HR analytics managers) and the key analytical goals of the app, including:

- identifying burnout patterns across job roles
- understanding relationships between AI usage and burnout
- evaluating productivity vs burnout trade-offs

This prompt customization helps ensure that the AI assistant provides explanations aligned with HR decision-making rather than generic statistical descriptions.

### QueryChat Response Style Control

The AI Explorer tab also includes a **Response Style control** that allows users to modify how the large language model (LLM) frames its responses. This control was introduced to provide users with flexibility in how AI-generated explanations are presented while maintaining consistency with the dataset context.

#### Feature Description

A dropdown input is provided in the AI Explorer sidebar with the following options:

- **Executive Summary** - concise, high-level insights suitable for quick decision-making.
- **Analytical Explanation** - balanced interpretation of dataset patterns and relationships.
- **Technical Interpretation** - more precise explanations referencing dataset variables and analytical limitations.

The selected response style is incorporated into the prompt instructions passed to the LLM, influencing the tone, level of detail, and framing of generated responses.

#### Default Behavior

The **Analytical Explanation** style is selected as the default mode. This style provides the best balance between interpretability, dataset grounding, and readability for typical dashboard users.

#### Design Rationale

The response style control was selected after evaluating several potential QueryChat customization options, including a verbosity slider and a scope-restriction toggle. These alternatives were not prioritized due to either limited behavioral impact (verbosity control) or higher implementation complexity (scope restriction).

An experiment was conducted comparing three response styles across representative user questions about the dataset. Responses were evaluated using the following criteria:

- relevance to the dataset
- clarity
- actionability
- audience fit
- faithfulness to the dataset context

The **Analytical Explanation** style achieved the highest overall evaluation score and demonstrated the most consistent performance across the criteria. As a result, it was selected as the default response style while still allowing users to switch to other modes depending on their needs.

#### Alignment with User Needs

The QueryChat Response Style control supports several of the project's user stories and Jobs-to-Be-Done by enabling users to explore and interpret burnout patterns in different ways depending on their analytical needs.

**User Story 3**  
The AI Explorer allows HR analytics managers to investigate burnout patterns across job roles, experience levels, and AI usage. The response style control improves this exploration by allowing users to choose explanations that best match their decision-making context. For example, an Executive Summary provides quick insights about which roles or experience levels may be most affected, while Analytical or Technical styles provide deeper interpretation of the data.

**JTBD 1 – Distinguishing workload-driven vs AI-associated burnout**  
The analytical and technical response styles help users interpret relationships between workload indicators (manual work hours, deadlines, task complexity) and AI usage variables. This helps users avoid misattributing burnout to AI adoption when other factors may be more influential.

**JTBD 3 – Evaluating productivity alongside burnout risk**  
When examining productivity outcomes relative to burnout scores, the AI Explorer can explain observed patterns in different levels of detail. Analytical responses help managers understand whether productivity gains appear alongside increased burnout risk, while technical responses provide more cautious interpretations of potential relationships in the data.

Overall, the response-style control improves the usability of the AI Explorer by allowing explanations to adapt to different analytical contexts while remaining grounded in the dashboard's dataset.

