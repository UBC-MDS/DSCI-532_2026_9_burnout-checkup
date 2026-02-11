# Contributing to burnout_checkup

Thank you for your interest in contributing to **burnout_checkup**.

This project is developed as part of DSCI 532 and follows a structured
GitHub workflow to ensure reproducibility, collaboration quality, and
transparency. All contributions --- code, documentation, design
suggestions, or issue reports --- are welcome.

------------------------------------------------------------------------

## Collaboration Workflow

We follow a GitHub Flow--based workflow:

-   All work is done on branches created from `main`
-   Each GitHub issue corresponds to a single task
-   Issues are assigned to exactly one team member
-   Pull requests require review by at least one other team member
-   No direct commits are made to `main`
-   All project discussions occur through GitHub Issues or Pull Requests

This ensures traceability and aligns with course grading expectations.

------------------------------------------------------------------------

## Branch Naming Convention

Create a branch from `main` for each piece of work using the following
prefixes:

-   `feature/<short-description>` -- new dashboard components or
    features\
-   `fix/<short-description>` -- bug fixes\
-   `docs/<short-description>` -- documentation updates\
-   `test/<short-description>` -- testing-related updates\
-   `chore/<short-description>` -- maintenance tasks

Examples: - `feature/risk-indicator-card` - `fix/filter-bug` -
`docs/readme-update` - `test/eda-notebook-check` -
`chore/environment-update`

------------------------------------------------------------------------

## Ways to Contribute

### Report Issues

If you encounter a bug or have a suggestion: - Open a GitHub issue -
Clearly describe the problem or idea - Include steps to reproduce (if
applicable) - Attach screenshots where helpful

### Implement Features

When implementing a feature: - Ensure it aligns with the dashboard's
scope (burnout analysis, workload exploration, AI usage comparisons) -
Keep changes focused and incremental - Reference the related issue in
your pull request

### Improve Documentation

You may contribute by: - Improving the README - Clarifying setup
instructions - Adding comments to code - Enhancing proposal or report
documentation

------------------------------------------------------------------------

## Development Setup

1.  Clone the repository:

    ``` bash
    git clone <repository-url>
    cd burnout_checkup
    ```

2.  Create and activate the environment:

    ``` bash
    conda env create -f environment.yml
    conda activate burnout_checkup
    ```

3.  Run the dashboard locally:

    ``` bash
    shiny run --reload src/app.py
    ```

------------------------------------------------------------------------

## Code Guidelines

-   Follow PEP 8 for Python formatting
-   Write clear, readable, and modular code
-   Keep visualization logic separate from data wrangling when possible
-   Comment non-obvious logic
-   Update documentation when functionality changes

------------------------------------------------------------------------

## Pull Request Checklist

Before submitting a pull request:

1.  Ensure the app runs locally
2.  Confirm that changes are small and focused
3.  Link the related GitHub issue
4.  Request a review from at least one team member
5.  Ensure no direct commits were made to `main`

------------------------------------------------------------------------

## Code of Conduct

By contributing to this project, you agree to adhere to the team's Code
of Conduct and maintain respectful, constructive communication.

Thank you for contributing to burnout_checkup!
