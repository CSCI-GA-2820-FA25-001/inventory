"""
Web Steps for Inventory BDD Tests
"""

from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


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

@when('I set the "Condition" filter to "{condition}"')
def step_impl(context, condition: str) -> None:
    element = context.driver.find_element(By.ID, "condition")
    select = Select(element)
    select.select_by_visible_text(condition)


@when('I set the "Quantity Less Than" filter to "{quantity}"')
def step_impl(context, quantity: str) -> None:
    element = context.driver.find_element(By.ID, "quantity_lt")
    element.clear()
    element.send_keys(quantity)


@when('I set the "Restock Needed" filter to "{status}"')
def step_impl(context, status: str) -> None:
    checkbox = context.driver.find_element(By.ID, "restock_needed")
    should_check = status.strip().lower() == "yes"
    if checkbox.is_selected() != should_check:
        checkbox.click()


@then('I should see only inventory items with condition "{condition}" and quantity less than {quantity:d}')
def step_impl(context, condition: str, quantity: int) -> None:
    table = context.driver.find_element(By.ID, "search_results")
    rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        item_condition = cells[2].text.strip()  # 3rd column = condition
        item_quantity = int(cells[3].text.strip())  # 4th column = quantity
        assert item_condition == condition, f"Expected condition {condition} but got {item_condition}"
        assert item_quantity < quantity, f"Expected quantity less than {quantity} but got {item_quantity}"


@then('I should see only inventory items that need restocking')
def step_impl(context) -> None:
    table = context.driver.find_element(By.ID, "search_results")
    rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        quantity = int(cells[3].text.strip())  # 4th column = quantity
        restock_level = int(cells[4].text.strip())  # 5th column = restock_level
        assert quantity < restock_level, f"Expected quantity < restock level but got quantity {quantity} and restock level {restock_level}"      
