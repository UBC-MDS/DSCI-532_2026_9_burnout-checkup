# Burnout Check-up

## Section 1: Motivation and Purpose

**Our role:** Data science consulting firm
**Target audience:** HR leaders and people analytics professionals

Burnout is widespread among full-time workers, with nearly two-thirds reporting feeling burned out at least sometimes (Wigert & Agrawal, 2018). Beyond personal strain, burnout carries major organizational costs since burned-out employees are significantly more likely to take sick days, seek new jobs, and report lower confidence and engagement in their performance.

The rapid adoption of AI tools in the workplace has transformed how employees approach tasks, collaboration, and productivity expectations. While AI has the potential to improve efficieny and reduce the time spent in minor tasks, concerns about the increased usage of AI are increasing since they can also contribute to employee burnout, rather than alleviate it.

To address this challenge, we propose bulding an interactive data visualization app that allows HR leaders and people analytics teams to explore the relationship between AI usage and employee burnout levels across different degrees of AI adoption under different work conditions. This will help understand whether AI is acting as a protective factor or a risk factor for employees.

## Section 2: Description of the Data

We will be visualizing a dataset consisting of two CSV files, each containing approximately 4,500 employee records. Each record represents an individual employee measured over a fixed time period and captures information related to job characteristics, AI tool usage, workload, work habits, and well-being outcomes.

The first dataset contains 15 variables describing employee characteristics and work patterns, which we hypothesize may influence burnout risk and productivity outcomes:

- Employee demographics and role information (e.g., `Employee_ID`, `job_role`, `experience_years`)
- AI usage and task automation (e.g., `ai_tool_usage_hours_per_week`, `tasks_automated_percent`, `learning_time_hours_per_week`)
- Workload and time allocation (e.g., `manual_work_hours_per_week`, `meeting_hours_per_week`, `collaboration_hours_per_week`, `focus_hours_per_day`)
- Work pressure and task demands (e.g., `deadline_pressure_level`, `task_complexity_score`)
- Work quality and well-being indicators (e.g., `error_rate_percent`, `work_life_balance_score`, `burnout_risk_score`)

The second dataset contains our target variables related to employee performance and well-being, including:

- Productivity outcomes (e.g., `productivity_score`)
- Burnout classification (e.g., `burnout_risk_level`)

The two datasets are linked using the shared `Employee_ID` field, allowing employee-level integration of workload, AI usage, productivity, and burnout indicators.

## Section 3: Research Questions & Usage Scenarios

### Usage Scenario


## References

Wigert, B., and Agrawal, S. (2018). Employee burnout, part 1: The 5 main causes. https://www.gallup.com/workplace/237059/employee-burnout-part-main-causes.aspx