# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa

"""
Web Steps for Inventory BDD Tests
"""

from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

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


@when('I fill in the product ID with "{text}"')
def step_impl(context, text):
    context.driver.find_element(By.ID, "product_id").send_keys(text)


@when('I select condition "{condition}"')
def step_impl(context, condition):
    from selenium.webdriver.support.ui import Select

    select = Select(context.driver.find_element(By.ID, "condition"))
    select.select_by_value(condition)


@when('I fill in quantity with "{text}"')
def step_impl(context, text):
    field = context.driver.find_element(By.ID, "quantity")
    field.clear()
    field.send_keys(text)


@when("I click the create button")
def step_impl(context):
    context.driver.find_element(By.ID, "create-btn").click()
    import time

    time.sleep(2)


@when("I click the update button")
def step_impl(context):
    context.driver.find_element(By.ID, "update-btn").click()
    import time

    time.sleep(2)


@then('I should see "{text}"')
def step_impl(context, text):
    import time

    time.sleep(1)  # Wait for flash message
    assert text in context.driver.page_source, f"Expected '{text}' not found in page"


@when('I enter "{text}" in the item ID field')
def step_impl(context, text):
    field = context.driver.find_element(By.ID, "item_id")
    field.clear()
    field.send_keys(text)


@when("I click the retrieve button")
def step_impl(context):
    button = context.driver.find_element(By.ID, "retrieve-btn")
    button.click()
    import time

    time.sleep(2)


@then("I should see the item details in the form")
def step_impl(context):
    product_id = context.driver.find_element(By.ID, "product_id").get_attribute("value")
    assert product_id, "Product ID should be populated"
    assert "Success" in context.driver.page_source

@when('I set the "Condition" filter to "{condition}"')
def step_impl(context, condition: str) -> None:
    element = context.driver.find_element(By.ID, "condition")
    select = Select(element)
    select.select_by_visible_text(condition)


@when('I set the "Quantity Less Than" filter to "{quantity}"')
def step_impl(context, quantity: str) -> None:
    element_id = "quantity"  
    wait = WebDriverWait(context.driver, context.wait_seconds)
    element = wait.until(expected_conditions.presence_of_element_located((By.ID, element_id)))
    element.clear()
    element.send_keys(quantity)

@then('I should see only inventory items with condition "{condition}" and quantity less than {quantity:d}')
def step_impl(context, condition, quantity):
    table = context.driver.find_element(By.ID, "search_results")
    rows = table.find_elements(By.TAG_NAME, "tr")
    for row in rows[1:]: 
        cells = row.find_elements(By.TAG_NAME, "td")
        item_condition = cells[2].text.strip()    
        item_quantity = int(cells[3].text.strip())  
        assert item_condition == condition, f"Expected {condition} but got {item_condition}"
        assert item_quantity < quantity, f"Expected quantity < {quantity} but got {item_quantity}"

@when('I set the "Restock Needed" filter to "{status}"')
def step_impl(context, status: str) -> None:
    button_id = "restock-btn"
    wait = WebDriverWait(context.driver, context.wait_seconds)
    button = wait.until(expected_conditions.element_to_be_clickable((By.ID, button_id)))
    if status.strip().lower() == "yes":
        button.click()

@then('I should see only inventory items that need restocking')
def step_impl(context):
    table = context.driver.find_element(By.ID, "search_results")
    rows = table.find_elements(By.TAG_NAME, "tr")
    for row in rows[1:]: 
        cells = row.find_elements(By.TAG_NAME, "td")
        quantity = int(cells[3].text.strip())       
        restock_level = int(cells[4].text.strip())  
        assert quantity < restock_level, f"Expected quantity < restock level but got quantity {quantity} and restock level {restock_level}"
