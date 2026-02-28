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