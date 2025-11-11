"""
Environment configuration for Behave BDD tests
"""

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def before_all(context):
    """Runs once before all tests"""
    context.base_url = os.getenv("BASE_URL", "http://localhost:8080")


def before_scenario(context, scenario):
    """Runs before each scenario"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service("/usr/bin/chromedriver")
    context.driver = webdriver.Chrome(service=service, options=chrome_options)
    context.driver.implicitly_wait(5)


def after_scenario(context, scenario):
    """Runs after each scenario"""
    if hasattr(context, "driver"):
        context.driver.quit()
