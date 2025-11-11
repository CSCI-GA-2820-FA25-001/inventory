"""
Web Steps for Inventory BDD Tests
"""

from behave import given, when, then
from selenium.webdriver.common.by import By


@given("the inventory service is running")
def step_impl(context):
    """Verify service is accessible"""
    context.driver.get(context.base_url)
    assert context.driver.current_url is not None


@when("I visit the home page")
def step_impl(context):
    """Navigate to home page"""
    context.driver.get(context.base_url + "/")


@then("the page should load successfully")
def step_impl(context):
    """Verify page loaded"""
    assert "Inventory REST API Service" in context.driver.page_source


# -------------------------------------------------------------
# Listing Scenario Steps
# -------------------------------------------------------------


@when("I click the search button")
def step_impl(context):
    """Click the Search button to list inventory items"""
    search_button = context.driver.find_element(By.ID, "search-btn")
    search_button.click()


@then("I should see a list of inventory items")
def step_impl(context):
    """Verify the list of items appears in the table"""
    table = context.driver.find_element(By.ID, "search_results")
    rows = table.find_elements(By.TAG_NAME, "tr")
    assert len(rows) > 1, "Expected at least one inventory row (plus header)"
    assert "Success" in context.driver.page_source or "✅" in context.driver.page_source
