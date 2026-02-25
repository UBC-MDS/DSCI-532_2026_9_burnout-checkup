# App Specification

## 2.1 Updated Job Stories

| #   | Job Story                       | Status         | Notes                         |
| --- | ------------------------------- | -------------- | ----------------------------- |
| 1   | When I … I want to … so I can … | ✅ Implemented |                               |
| 2   | When I … I want to … so I can … | 🔄 Revised     | Changed from X to Y because … |
| 3   | When I … I want to … so I can … | ⏳ Pending M3  |                               |

## 2.2 Component Inventory

| ID            | Type          | Shiny widget / renderer | Depends on                   | Job story  |
| ------------- | ------------- | ----------------------- | ---------------------------- | ---------- |
| `input_var`   | Input         | `ui.input_slider()`     | —                            | #1, #2     |
| `filtered_df` | Reactive calc | `@reactive.calc`        | `input_year`, `input_region` | #1, #2, #3 |
| `plot_trend`  | Output        | `@render.plot`          | `filtered_df`                | #1         |
| `tbl_summary` | Output        | `@render.data_frame`    | `filtered_df`                | #2         |

## 2.3 Reactivity Diagram

Draw your planned reactive graph as a Mermaid flowchart using the notation from Lecture 3:

[/Input/] (Parallelogram) (or [Input] Rectangle) = reactive input
Hexagon {{Name}} = @reactive.calc expression
Stadium ([Name]) (or Circle) = rendered output
Example:

```mermaid
flowchart TD
  A[/input_year/] --> F{{filtered_df}}
  B[/input_region/] --> F
  F --> P1([plot_trend])
  F --> P2([tbl_summary])
  C[/input_color/] --> P3([plot_scatter])
```

## 2.4 Calculation Details

For each @reactive.calc in your diagram, briefly describe:

Which inputs it depends on.
What transformation it performs (e.g., "filters rows to the selected year range and region(s)").
Which outputs consume it.