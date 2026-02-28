# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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