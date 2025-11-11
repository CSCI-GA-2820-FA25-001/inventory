"""
Web Steps for Inventory BDD Tests
"""

from behave import given, when, then


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
