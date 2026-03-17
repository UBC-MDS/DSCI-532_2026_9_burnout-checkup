# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - Milestone 4

### Added

- QueryChat system prompt customization to provide more HR and managers-focused insights.
- Prompt experiment notebook evaluating different system prompt designs (#119).
- `on_tool_request` experimentation notebook evaluating different validation/transformation features to implement in our QueryChat.
- QueryChat response-style experiment notebook evaluating Executive, Analytical, and Technical response modes (#120).
- Structured evaluation framework for LLM responses including scoring criteria (relevance, clarity, actionability, audience fit, faithfulness)
- Detailed and compact summary tables comparing response style performance
- Documentation of experiment narrative, discussion, and final decision for QueryChat customization
- Playwright test verifying that Reset Filters restores dashboard inputs to default values (#125).
- Playwright test verifying that the debug panel correctly displays current filter state and filtered row counts.
- Playwright test verifying that the AI Explorer tab renders and remains functional when accessed.
- Playwright edge-case test verifying that Reset AI filters clears AI Explorer query state and restores default results.
- Documented test behavior descriptions and README instructions for running tests.
- Subtitles in KPI cards to clarify the baseline comparison with median/mean values across the company (#128).

### Changed

- Updated QueryChat prompt in `app.py` to align with dashboard user stories and analytics use cases (#119).
- Updated app specification to document the AI Explorer component and prompt design.
- Updated `app.py` to include all member's experimentation results combined into a customized QueryChat (#124).
- Specification document updated to include QueryChat Response Style control and design rationale
- AI Explorer design documentation expanded to describe response style behavior and default configuration
- Updated `safe_median()` to drop missing values before computing the median, improving handling of empty or all-NaN inputs.
- Updated AI Explorer reset tests to match the current default reset state and preview behavior.
- Removed the non-functional "**Predicted Risk Overlay**" checkbox from the dashboard sidebar to eliminate a misleading control (#127).
- Updated the **app specification document** to reflect the removal of the planned predicted overlay feature.
- Updated the project proposal (**Section 5: App Description**) to remove references to predicted overlays in the burnout-by-role chart.
- Increased AI Explorer sidebar width to improve readability and prevent layout compression of chat responses and tool outputs.
- Refactored `app.py` to remove code smells and improve overall structure, readability, and maintainability.
- Updated the scatter plots including "How AI Usage Relates to Burnout Risk Across Employees" and "Relationship Between Productivity and Burnout Risk" to resolve overplotting issue. (#130)

### Fixed

- Eliminated runtime warnings from median calculations on empty or all-missing series in KPI helpers.
- Fixed failing reset-related end-to-end tests by aligning test expectations with the current AI Explorer reset title and default preview state.

### Known Issues

- Playwright end-to-end tests require the Shiny app to be running locally on `http://localhost:8000`; tests will fail with connection errors if the app is not started before running `pytest`.
- AI Explorer responses depend on external LLM availability and API configuration, which may lead to variability in response quality or delays.
- Certain filter combinations may produce sparse datasets, which can reduce interpretability of charts and KPI summaries.
- QueryChat tool interception currently blocks overly broad queries but does not yet provide adaptive query rewriting.
- Resolved feedback regarding the presence of a non-functional dashboard control that could confuse users.
- Removed residual show_pred references from debug utilities and related logic to eliminate dead code and ensure consistency after feature removal.

### Release Highlight

QueryChat Response Style Control and Tool Interception Integration
(see PR #124)

This release introduces a configurable response-style control (Executive, Analytical, Technical) in the AI Explorer, allowing users to tailor AI explanations to their needs. Combined with on_tool_request interception, the system now prevents overly broad queries and improves the relevance and usability of AI-generated insights.

This feature was selected as the release highlight because it directly enhances the core value of the dashboard: supporting HR decision-making through interpretable, context-aware AI insights, while addressing risks of misleading or overly generic responses.

### Collaboration

- Updated CONTRIBUTING.md to include Milestone 3 retrospective and Milestone 4 collaboration norms (#115).
- Incorporated team-wide experimentation results into a unified QueryChat implementation, integrating prompt design, response-style controls, and tool interception.
- Established clearer division of responsibilities across:
  - AI experimentation and evaluation
  - dashboard testing and validation
  - documentation and specification updates
- Improved coordination through issue-based task tracking and milestone prioritization (e.g., #103, #104).
- Applied lessons from Milestone 3 to:
  - reduce duplication in app logic
  - standardize testing practices
  - improve documentation consistency

### Reflection

We prioritized issues that directly affected the interpretability, correctness, and usability of the dashboard. In particular, unclear KPI baselines, scatterplot overplotting, and the presence of a non-functional overlay toggle were treated as critical because they could mislead users or reduce trust in the insights. In contrast, improvements related to UI layout, styling, and additional explanatory context were considered lower priority since they enhance usability but do not affect analytical outcomes.

A key strength of the dashboard is the integration of interactive filtering with AI-assisted exploration, allowing users to analyze burnout patterns through both structured visualizations and natural language queries. The addition of response-style controls further improves interpretability for different user audiences.

However, limitations remain. The AI Explorer depends on external LLM responses, which may introduce variability, and certain filter combinations can result in sparse datasets that reduce interpretability. Additionally, the current tool interception logic prevents overly broad queries but does not yet support adaptive query refinement.

Trade-offs were made to prioritize analytical correctness, test coverage, and reliable user interactions. As a result, some advanced features (such as predictive overlays) were intentionally removed to avoid exposing incomplete or misleading functionality. Overall, this milestone reflects a shift toward robustness, clarity, and user trust over feature breadth.

#### Tests

To improve reliability and document expected behavior, we added automated tests covering both user-facing interactions and core dashboard logic. The Playwright tests verify key interface behaviors, including resetting dashboard filters, displaying the debug panel state, rendering the AI Explorer view, and clearing AI query state when reset is triggered. These tests help catch regressions that would directly affect user interaction, such as broken navigation or inconsistent UI states.

For unit testing, we added a broader suite of pytest tests covering core data and dashboard logic, including filtering behavior, KPI calculations, chart preparation, debug output, and helper functions used throughout the app. Rather than targeting implementation details, these tests validate that key data transformations and summary computations produce expected outputs under representative conditions. If these behaviors change unexpectedly, the app could display incorrect filtered subsets, misleading KPI values, invalid chart inputs, or inconsistent debug outputs, so the unit tests act as an early warning for logic regressions.

#### Charts

**Scatter plot updates:**

Based on peer feedback regarding overplotting and interpretability, we refined both scatterplots while preserving their analytical intent.

**AI Usage vs Burnout:**  
The original scatterplot was replaced with a binned/density-based visualization to reduce heavy point overlap and improve readability. Since burnout risk is already encoded on the y-axis, we removed the additional color encoding for deadline pressure and retained it as a filter instead. This simplifies the visual encoding and makes overall patterns easier to interpret.  
This update supports **Job Story 1**, enabling clearer comparison of burnout levels across AI usage under controlled conditions.

**Productivity vs Burnout**  
We preserved the original structure, including the quadrant layout defined by company medians, to maintain its analytical purpose. Instead of changing the chart type, we reduced overplotting by lowering point opacity and adding jitter.  
These adjustments improve clarity while preserving interpretability of the quadrants (e.g., identifying high productivity–high burnout scenarios in the top-right quadrant), directly supporting **Job Story 3** in assessing whether productivity gains are associated with increased burnout risk.

#### Future Directions

Looking ahead, future work would focus on extending the AI Explorer with more robust query handling, including adaptive query refinement rather than simple blocking of broad requests. We would also explore reintroducing predictive features, such as a validated burnout risk overlay, once a reliable modeling approach is established. Additional improvements could include better handling of sparse filter results, enhanced visual summaries for edge cases, and deeper evaluation of AI response quality across different user scenarios. These directions aim to expand functionality while maintaining the clarity and reliability established in this milestone.

## [0.3.0] - Milestone 3

### Added

- Added **AI Explore tab** to allow users to interact with the dataset using natural language queries.
- Implemented **QueryChat integration** for AI-driven exploration.
- Added **AI server configuration** to support model interactions.
- Added **API key configuration** using a `.env` file.
- Added `.env` to `.gitignore` for secure handling of API credentials.
- Added **new KPI cards** for the AI Explore tab.
- Added **download button** to export filtered data.
- Added **legend for KPI indicators** in scatter plots.
- Added **dummy table output and query functionality** as the initial structure for AI-assisted querying.
- Introduced modular project structure to improve maintainability and collaboration.
- Created new module files to separate dashboard responsibilities:
  - src/data.py for data loading and preprocessing logic.
  - src/filters.py for reusable dataframe filtering utilities.
  - src/kpis.py for KPI computation and UI helpers.
  - src/charts.py for reusable Altair visualization functions.
  - src/ai_tab.py as a placeholder for the upcoming AI-powered dashboard tab.
- Added src/utils/ package with `__init__.py` to host shared utility functions across modules.
- Added `src/data.py` to encapsulate dashboard dataset preparation and configuration helpers.
- Added minimal NumPy-style docstrings for data-loading and preprocessing helpers.
- Added `DEADLINE_PRESSURE_MAP` constant to standardize workload-score derivation.
- Added .env.example file to provide a template for required environment variables.
- Updated **README** with instructions for setting up environment variables, helping prevent accidental commits of sensitive data and improving onboarding for new developers.### Added
- Unit tests for `src/data.py` covering data loading, filter choice generation, slider range computation, and baseline metric calculations.
- Unit tests for dashboard filtering logic in `apply_dashboard_filters` using `pytest`.
- Test coverage for QueryChat dataframe normalization via `normalize_querychat_result`.
- Synthetic test dataset fixture for validating filter behavior across job roles, AI usage bands, numeric ranges, and deadline pressure levels.
- Unit tests for reusable KPI helpers (`safe_mean`, `safe_median`, `percent_diff`, `trend_arrow`, `trend_class`).
- Tests for KPI UI components (`median_metric_card`, `high_burnout_pct_card`, `count_card`).
- Added unit tests for chart-building functions in `src/charts.py`, covering empty-state placeholders, layered scatter plots, bar chart aggregation, and hours breakdown visualization behavior.
- Added unit tests for the debug formatter in `src/utils/debug.py` to validate filter-state output and filtered row count reporting.

### Changed

- Restructured the **AI Explore tab layout** to improve usability and organization.
- Updated the **job role filter** to allow **multiple selections** instead of a single selection.
- Replaced the **pie chart with a donut chart** to improve readability and visual clarity.
- Removed unused plots and cleaned up visualization components.
- Updated **environment and requirements files** to ensure consistent dependency management.
- Refactored Altair chart construction out of `src/app.py` into reusable helper functions in `src/charts.py`.
- Updated dashboard chart rendering in `app.py` to call chart helper functions instead of building charts inline.
- Rotated x-axis labels in the burnout-by-role chart to improve readability for longer job role names.
- Updated README with instructions for running the project test suite using `pytest`.
- Improved test coverage for KPI computation logic used in dashboard metrics.

### Fixed

- Fixed multiple **code bugs and minor UI issues** identified during development.
- Fixed dependency conflicts in `requirements.txt` and environment configuration.
- Reduced duplication of top-level data setup logic in `src/app.py`.
- Improved separation of concerns by keeping dataset preparation distinct from UI and server logic.

### Refactored

- Prepared the application architecture for modularization of app.py logic in future commits.
- Refactoring groundwork added to support upcoming AI-driven filtering features and easier parallel development.
- Refactored dashboard data-loading logic out of `src/app.py` into `src/data.py`.
- Centralized feature/target CSV loading and merge logic in `load_dashboard_data()`.
- Moved derived-column preprocessing into the data module, including:
  - `workload_score`
  - `workload_band`
  - `ai_band`
- Moved sidebar filter option generation into `get_filter_choices()`.
- Moved numeric slider range computation into `get_slider_ranges()`.
- Moved company-wide baseline metric computation into `get_baselines()`.
- Refactored data filtering logic in filters.py to streamline implementation and remove redundant code.
- Updated app.py to integrate the new filtering logic and ensure AI filtering functionality works correctly with the revised system.
- Extracted reusable KPI card UI and metric helper functions into `src/kpis.py`.
- Centralized median-, percentage-, and count-based KPI generation to reduce duplication across Dashboard and AI Explorer tabs.
- Replaced repeated inline KPI computation logic in `src/app.py` with shared helper calls.
- Standardized baseline comparison behavior for KPI arrows, subtitle messaging, and visual status classes.
- Simplified `app.py` server code by separating KPI presentation logic from reactive dashboard wiring.
- Centralized dashboard plotting logic for:
  - AI usage vs burnout
  - burnout by job role
  - weekly work hours breakdown
  - productivity vs burnout
- Reduced `app.py` complexity by separating visualization logic from Shiny server wiring.
- Prepared chart functions for reuse in other dashboard sections, including the AI Explorer tab.
- Moved debug panel formatting logic from `app.py` to `src/utils/debug.py`.
- Added `format_filter_debug()` utility to simplify server debug output.

### Infrastructure

- Updated **Shiny dependency versions** to resolve compatibility issues.
- Updated and synchronized **environment.yml** and **requirements.txt**.
- Merged several feature and bug-fix branches related to:
  - AI tab implementation
  - API configuration
  - dependency fixes
  - dashboard restructuring
  - lab feedback improvements

### Reflection (Milestone 3)

1. **Implementation Status:**
Most of the planned functionality for Milestone 3 has been implemented. The dashboard was expanded with an **AI Explore tab** to allow users to interact with the dataset in more flexible ways. The AI Explore tab now includes additional KPI cards, improved filtering through the sidebar, and updated visualizations such as the donut chart and enhanced scatterplots with clearer legends. The chatbot integration allows users to query the data using natural language, providing an additional exploratory interface beyond traditional dashboard filters. Supporting infrastructure such as API configuration, environment management, and dependency updates were also implemented to ensure the application runs consistently across environments.

2. **Deviations:**
Some adjustments were made from the original implementation plan as development progressed. The AI tab initially included several experimental components such as dummy tables and placeholder queries, which were used to prototype the chatbot interaction workflow before integrating the final functionality. Additionally, the structure of the AI Explore tab was reorganized to improve usability, and some unused plots were removed to keep the interface focused on the most informative visualizations. The job role filter was also updated to allow **multiple selections**, improving flexibility compared to the earlier design.

3. **Known Issues:**
The chatbot functionality currently serves as an exploratory interface and may still produce limited responses depending on the query structure. Since the model interaction depends on API configuration, users must properly set environment variables for the chatbot to function correctly. Additionally, some filter combinations may still produce sparse datasets, which can reduce the interpretability of certain visualizations.

4. **Best Practices:**
We focused on improving usability and clarity in the dashboard layout. The replacement of the pie chart with a **donut chart** improves readability while maintaining the same conceptual representation. Legends and annotations were added to scatterplots to make KPI comparisons easier to interpret. Environment configuration was also improved by using a `.env` file and synchronizing dependency files, which supports reproducibility and secure handling of API credentials.

Refactoring the dashboard into separate modules for data handling, filtering, KPI calculations, chart generation, and debugging made the codebase much easier to understand and maintain. Breaking the logic into smaller, focused components reduced the complexity of `app.py`, making it clearer how each part of the application works. It also improves collaboration within the team, since individual components can now be developed, tested, and reviewed independently without affecting the rest of the dashboard.

Adding tests improves reliability of the dashboard's reactive filtering logic and reduces risk of regressions during future feature development.

5. **Self-Assessment:**
The addition of the AI components significantly enhances the exploratory capabilities of the dashboard. Users can now interact with the data through both structured visual analytics and conversational querying. The restructuring of the AI Explore tab and improvements to filtering and visualization clarity make the dashboard more intuitive and flexible. While the chatbot feature could be expanded further, the current implementation demonstrates the feasibility of integrating AI-assisted exploration within the dashboard. Future work could focus on improving response quality, adding more guided insights, and further refining visual explanations for users.

## [0.2.0]

### What's Changed

- Removed *Employee ID* from the app `sketch/skeleton` and switched for *AI usage* (low, moderate, high)
- Changed focus from *task complexity and deadline pressure* to just *deadline pressure* in **job story 2** 
- Updated app.py to read `feature/target` data using centralized `FEATURES_PATH` and `TARGETS_PATH` constants.
- Removed hardcoded CSV paths previously used in app.py.
- Updated paths.py constants to reference `ai_productivity_features.csv` and `ai_productivity_targets.csv`.
- Replaced outdated features.csv and targets.csv constants.
- Ensured data loading is now fully centralized and consistent across the project.
- Updated data file paths in `constants/paths.py` and app.py to reflect new raw dataset filenames.
- Added outputs for all charts using `render_widget` instead of `render.ui` for improved rendering consistency.
- Added `src/__init__.py` to make src a package and resolve import errors in app.py.
- Implemented `filtered_df()` as the `@reactive.calc` object to manage all filtering logic.
- Added `reset_btn` and implemented `_reset_filters()` using `@reactive.effect` and `@reactive.event` to reset all filters to default values.
- updated `README.md` for potential users and contributors.
- Implemented styling in KPIs: added badges and coloring to improve readability

### Changes

1. Switch comparison between mean and company median to median vs. median. Our data is slightly skewed, with many value for `burnout_risk_score` at or very close to 10. After discussion, we decided that it's not very reasonable to compare mean and company median(baseline), so we changed all KPIs to median.

2. Implement % high risk score card since comparison between group median and company median is already implemented in each value box, the original `burnout_vs_median` is redundant. We have decided to change this card to % of high burnout risk employees in a group, which would make it easier to track by managers.

### Reflection (Milestone 2)

1. **Implementation Status:**
Most components from our original proposal and sketch have been implemented. The filtering logic is fully centralized through `filtered_df()` using `@reactive.calc`, and all charts are rendered consistently with `render_widget`. Job Stories 1, 2 and 3 are implemented through interactive filters, KPI comparisons, and scatterplots that allow users to evaluate burnout drivers and sustainability of productivity gains. Median-based KPIs and the % High Burnout Risk card are fully functional, and reset functionality has been added. Further refinement of deadline pressure interactions (Job Story 2) could still be improved with clearer summarization.

2. **Deviations:**
We made several intentional changes from the original plan. Due to skewness in the burnout risk scores, we replaced mean-based comparisons with median vs. median comparisons to improve robustness. We narrowed Job Story 2 to focus only on deadline pressure because it is more interpretable and actionable. We removed the `Employee ID` filter and replaced it with `AI usage bands` to better align with PM decision-making. We also replaced the `burnout_vs_median` KPI with a % High Burnout Risk card to avoid redundancy and provide clearer insight.

3. **Known Issues:**
Extreme filter combinations may produce sparse or empty visualizations. The dataset has a high concentration of burnout scores near the maximum value, which causes clustering in scatterplots. These behaviors are data-driven rather than incomplete features. We can also improve the filters so that the user can select multiple job roles since now they can only select one. 

4. **Best Practices:** 
Although pie charts are not ideal for precise comparisons, we retained one for high-level workload composition since the goal is general proportion awareness. We prioritized visual consistency in our color choices while maintaining sufficient contrast. We might change some of the colors for clearer comparison in the plots and KPIs.
5. **Self-Assessment:**
The dashboard strongly aligns with our job stories and uses a clean reactive structure that improves maintainability. The KPI redesign and centralized filtering are key strengths. However, visualizations could be enhanced with trend lines or clearer summaries, and accessibility improvements could be made. Future work would focus on stronger interpretive guidance and improved robustness for edge cases.

## [0.1.0]

### What's Changed

- Added `CONTRIBUTING.md` to provide clear contribution guidelines  
- Added raw data to the repository  
- Updated repository metadata  
- Added Section 2: Description of the Data  
- Added Section 1: Motivation and Purpose  
- Added initial `README.md` with project title and Milestone 1 summary  
- Added Code of Conduct document  
- Added Section 3: Research Questions & Usage Scenarios  
- Added `environment.yml` and `pin_env_versions.py` to the repository  
- Added seaborn to `environment.yml` for data visualization  
- Added EDA plots and explanations  
- Added App Sketch, Section 5 Description, and Paths Module  
- Created initial Shiny app skeleton

- Replace render_widget with
- render_altair for all charts
- Remove invalid alt.JupyterChart usage
- Standardize plots to return native alt.Chart objects
- Remove HTML conversion (to_html) path and unused helper
- Fix _empty_chart to return a valid Altair chart
- Remove unused sklearn.base import