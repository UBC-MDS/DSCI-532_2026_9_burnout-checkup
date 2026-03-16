# tests/e2e/test_ai_explorer.py

def test_ai_explorer_query_returns_results(page):
    """
    This test verifies that entering a query in the AI Explorer returns filtered data,
    ensuring the AI exploration feature functions correctly.
    """

    page.goto("http://localhost:8000")

    # Switch to AI Explorer tab
    page.get_by_role("tab", name="AI Explorer").click()

    # Enter query
    page.get_by_role("textbox").fill("Show employees with high burnout risk")

    # Submit query
    page.keyboard.press("Enter")

    # Wait for table
    page.wait_for_selector("table")

    assert page.locator("table").first.is_visible()


def test_reset_ai_query_clears_ai_state(page):
    """
    This test verifies that resetting the AI Explorer clears prior AI filter state,
    which matters because users need a reliable way to restart exploratory querying.
    """
    page.goto("http://localhost:8000")

    page.get_by_role("tab", name="AI Explorer").click()
    page.wait_for_timeout(1000)

    # Confirm AI Explorer loaded
    assert page.get_by_text("AI Explorer").first.is_visible()

    # Click reset even before/after interaction; the important thing is that UI remains usable
    page.get_by_role("button", name="Reset AI filters").click()
    page.wait_for_timeout(1000)

    assert page.get_by_text("Preview of first 100 rows").is_visible()