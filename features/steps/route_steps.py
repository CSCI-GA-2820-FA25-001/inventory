"""
BDD Step Definitions for OpenShift Route Testing
"""
import os
import subprocess
import requests
from behave import given, when, then


@given("the inventory microservice is deployed to OpenShift")
def step_impl(context):
    """Verify the inventory service deployment exists"""
    result = subprocess.run(
        ["oc", "get", "deployment", "inventory"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, "Inventory deployment not found"


@when('I create a route using "oc expose service inventory"')
def step_impl(context):
    """Create the route using oc command"""
    # First check if route already exists
    check_result = subprocess.run(
        ["oc", "get", "route", "inventory"],
        capture_output=True,
        text=True,
        check=False,
    )
    
    if check_result.returncode != 0:
        # Route doesn't exist, create it
        result = subprocess.run(
            ["oc", "expose", "service", "inventory"],
            capture_output=True,
            text=True,
            check=False,
        )
        context.route_creation_output = result.stdout
        context.route_creation_result = result.returncode
    else:
        # Route already exists
        context.route_creation_result = 0
        context.route_creation_output = "Route already exists"


@then('the route should be visible in "oc get routes"')
def step_impl(context):
    """Verify route appears in route list"""
    result = subprocess.run(
        ["oc", "get", "routes"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "inventory" in result.stdout, "Route 'inventory' not found in routes list"


@then('the route should have the name "{name}"')
def step_impl(context, name):
    """Verify route has the expected name"""
    result = subprocess.run(
        ["oc", "get", "route", name, "-o", "jsonpath={.metadata.name}"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == name, f"Route name mismatch: expected {name}, got {result.stdout.strip()}"


@then('the route should target service "{service_name}"')
def step_impl(context, service_name):
    """Verify route targets the correct service"""
    result = subprocess.run(
        ["oc", "get", "route", "inventory", "-o", "jsonpath={.spec.to.name}"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == service_name, f"Route targets wrong service: {result.stdout.strip()}"


@then('the route should target port "{port}"')
def step_impl(context, port):
    """Verify route targets the correct port"""
    result = subprocess.run(
        ["oc", "get", "route", "inventory", "-o", "jsonpath={.spec.port.targetPort}"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == port, f"Route targets wrong port: {result.stdout.strip()}"


@given("a route exists for the inventory service")
def step_impl(context):
    """Verify route exists"""
    result = subprocess.run(
        ["oc", "get", "route", "inventory"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, "Route 'inventory' does not exist"


@when("I get the route URL")
def step_impl(context):
    """Get the route URL from OpenShift"""
    result = subprocess.run(
        ["oc", "get", "route", "inventory", "-o", "jsonpath={.spec.host}"],
        capture_output=True,
        text=True,
        check=True,
    )
    context.route_host = result.stdout.strip()
    context.route_url = f"http://{context.route_host}"


@then("the microservice should be accessible via the route URL")
def step_impl(context):
    """Verify the route URL is accessible"""
    response = requests.get(f"{context.route_url}/health", timeout=10)
    assert response.status_code == 200, f"Route not accessible: {response.status_code}"


@then('GET request to "{endpoint}" returns 200 OK')
def step_impl(context, endpoint):
    """Verify specific endpoint returns 200"""
    # Replace {route-url} placeholder with actual route URL
    url = endpoint.replace("{route-url}", context.route_url)
    
    response = requests.get(url, timeout=10)
    assert response.status_code == 200, f"Expected 200, got {response.status_code} for {url}"


@then('the Swagger docs are accessible at "{endpoint}"')
def step_impl(context, endpoint):
    """Verify Swagger documentation is accessible"""
    url = endpoint.replace("{route-url}", context.route_url)
    
    response = requests.get(url, timeout=10)
    assert response.status_code == 200, f"Swagger docs not accessible: {response.status_code}"
    assert "swagger" in response.text.lower() or "openapi" in response.text.lower(), \
        "Response does not appear to be Swagger documentation"


@given("I have the route URL")
def step_impl(context):
    """Store the route URL for later use"""
    result = subprocess.run(
        ["oc", "get", "route", "inventory", "-o", "jsonpath={.spec.host}"],
        capture_output=True,
        text=True,
        check=True,
    )
    context.route_host = result.stdout.strip()
    context.route_url = f"http://{context.route_host}"


@when("I POST a new inventory item via the route")
def step_impl(context):
    """Create a new inventory item via the route"""
    test_data = {
        "product_id": 99999,
        "quantity": 100,
        "restock_level": 20,
        "restock_amount": 50,
        "condition": "NEW",
        "description": "Test item via route"
    }
    
    response = requests.post(
        f"{context.route_url}/api/inventory",
        json=test_data,
        timeout=10
    )
    context.post_response = response
    context.created_item = response.json() if response.status_code == 201 else None


@then("I should receive a 201 Created response")
def step_impl(context):
    """Verify POST returned 201"""
    assert context.post_response.status_code == 201, \
        f"Expected 201, got {context.post_response.status_code}"


@then("the Location header should contain the route URL")
def step_impl(context):
    """Verify Location header contains route URL"""
    location = context.post_response.headers.get("Location", "")
    assert context.route_host in location, \
        f"Location header does not contain route host: {location}"


@when("I GET the created item via the route")
def step_impl(context):
    """Retrieve the created item via the route"""
    assert context.created_item is not None, "No item was created"
    item_id = context.created_item["id"]
    
    response = requests.get(
        f"{context.route_url}/api/inventory/{item_id}",
        timeout=10
    )
    context.get_response = response


@then("I should receive a 200 OK response")
def step_impl(context):
    """Verify GET returned 200"""
    assert context.get_response.status_code == 200, \
        f"Expected 200, got {context.get_response.status_code}"


@then("the response should contain the correct item data")
def step_impl(context):
    """Verify retrieved item matches created item"""
    retrieved_item = context.get_response.json()
    created_item = context.created_item
    
    assert retrieved_item["id"] == created_item["id"], "Item ID mismatch"
    assert retrieved_item["product_id"] == created_item["product_id"], "Product ID mismatch"
    assert retrieved_item["quantity"] == created_item["quantity"], "Quantity mismatch"