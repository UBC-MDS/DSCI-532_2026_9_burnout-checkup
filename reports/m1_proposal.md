# Burnout Check-up

## Section 1: Motivation and Purpose

**Our role:** Data science consulting firm
**Target audience:** HR leaders and people analytics professionals

Burnout is widespread among full-time workers, with nearly two-thirds reporting feeling burned out at least sometimes (Wigert & Agrawal, 2018). Beyond personal strain, burnout carries major organizational costs since burned-out employees are significantly more likely to take sick days, seek new jobs, and report lower confidence and engagement in their performance.

The rapid adoption of AI tools in the workplace has transformed how employees approach tasks, collaboration, and productivity expectations. While AI has the potential to improve efficieny and reduce the time spent in minor tasks, concerns about the increased usage of AI are increasing since they can also contribute to employee burnout, rather than alleviate it.

To address this challenge, we propose bulding an interactive data visualization app that allows HR leaders and people analytics teams to explore the relationship between AI usage and employee burnout levels across different degrees of AI adoption under different work conditions. This will enable HR leaders to compare burnout risk across different AI usage intensities and workload conditions, supporting evidence-based decisions around AI deployment and workforce planning.

## Section 2: Description of the Data

We will be visualizing a dataset consisting of two CSV files, each containing approximately 4,500 employee records. Each record represents an individual employee measured over a fixed time period and captures information related to job characteristics, AI tool usage, workload, work habits, and well-being outcomes.

The first dataset contains 15 variables describing employee characteristics and work patterns, which we hypothesize may influence burnout risk and productivity outcomes:

- Employee demographics and role information (e.g., `Employee_ID`, `job_role`, `experience_years`)
- AI usage and task automation (e.g., `ai_tool_usage_hours_per_week`, `tasks_automated_percent`, `learning_time_hours_per_week`)
- Workload and time allocation (e.g., `manual_work_hours_per_week`, `meeting_hours_per_week`, `collaboration_hours_per_week`, `focus_hours_per_day`)
- Work pressure and task demands (e.g., `deadline_pressure_level`, `task_complexity_score`)
- Work quality and well-being indicators (e.g., `error_rate_percent`, `work_life_balance_score`, `burnout_risk_score`)

The second dataset contains our outcome variables related to employee performance and well-being, including:

- Productivity outcomes (e.g., `productivity_score`)
- Burnout classification (e.g., `burnout_risk_level`)

The two datasets are linked using the shared `Employee_ID` field, allowing employee-level integration of workload, AI usage, productivity, and burnout indicators.

## Section 3: Research Questions & Usage Scenarios

### Usage Scenario

Monica is an HR analytics manager at a mid-sized organization that has recently expanded the use of AI tools across multiple teams. While leadership expects AI adoption to improve productivity, Monica is concerned about rising reports of employee stress and burnout. Monica wants to understand whether AI tool usage is associated with lower or higher burnout risk when controlling for workload, in order to inform responsible AI deployment and workforce planning decisions.

When Monica logs into our AI & Burnout app, she is presented with an overview of key variables related to AI usage, workload, productivity, and burnout across the organization. Monica can explore the distribution of burnout risk across different levels of AI tool usage and compare employees with similar workload profiles. Interactive filters allow Monica to isolate specific job roles, experience levels, or workload intensity bands to conduct comparisons.

Through this exploration, Monica may observe that employees with moderate AI usage and balanced workloads tend to report lower burnout risk, while high AI usage combined with high deadline pressure is associated with elevated burnout levels. By examining productivity metrics alongside burnout indicators, Monica can identify scenarios where productivity gains coincide with increased burnout, suggesting potentially unsustainable work practices. Monica may recommend targeted interventions such as workload rebalancing, additional training time for AI tools, or revised productivity expectations to ensure that AI adoption supports employee well-being rather than undermines it.

### User Stories

#### User Story 1

As an **HR analytics manager**, I want to filter employees by AI usage intensity and workload level in order to compare burnout risk across employees with similar workloads.

#### User Story 2

As an **HR analytics manager**, I want to compare burnout risk and productivity across AI usage levels relative to company-wide baselines (overall % high burnout, overall average productivity), so that I can determine whether AI adoption is associated with improved outcomes or elevated burnout risk.

#### User Story 3

As an **HR analytics manager**, I want to analyze burnout risk across job roles and experience levels in order to identify teams or career stages that may be disproportionately affected by AI-related work pressure.

### Jobs to Be Done

#### JTBD 1:

**Situation:** When reviewing employee well-being and productivity reports…
**Motivation:** …I want to distinguish burnout driven by excessive workload from burnout potentially associated with AI tool usage…
**Outcome:** …so I can make informed decisions about AI adoption policies without misattributing burnout to the wrong causes.

#### JTBD 2:

**Situation:** When investigating an increase in reported burnout or stress levels within specific teams…
**Motivation:** …I want to assess whether high AI usage combined with deadline pressure and task complexity is contributing to elevated burnout risk…
**Outcome:** …so I can design targeted interventions such as workload rebalancing, additional AI training, or revised performance expectations.

#### JTBD 3:

**Situation:** When evaluating the impact of AI tools on employee productivity…
**Motivation:** …I want to understand whether productivity gains are occurring alongside increases in burnout risk…
**Outcome:** …so I can ensure that productivity improvements are sustainable and do not come at the expense of employee well-being.

## References

Wigert, B., and Agrawal, S. (2018). Employee burnout, part 1: The 5 main causes. https://www.gallup.com/workplace/237059/employee-burnout-part-main-causes.asp