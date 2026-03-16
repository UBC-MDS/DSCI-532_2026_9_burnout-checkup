def test_reset_filters(page):
    """
    This test verifies that clicking the Reset Filters button restores modified dashboard filters
    to their default values so users can restart exploration easily.
    """
    page.goto("http://localhost:8000")

    # Change job role away from default
    page.locator("#job_role + .selectize-control").click()
    page.locator(".selectize-dropdown-content div").filter(has_text="Developer").click()
    page.wait_for_timeout(500)

    # Reset filters
    page.get_by_role("button", name="Reset Filters").click()
    page.wait_for_timeout(1000)

    # Check that All is restored
    selected_text = page.locator("#job_role + .selectize-control").text_content()
    assert "All" in selected_text