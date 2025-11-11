Feature: Inventory Service UI
    As an inventory manager
    I need a user interface for the inventory service
    So that I can manage inventory items

    Background:
        Given the inventory service is running

    Scenario: The API is accessible
        When I visit the home page
        Then the page should load successfully