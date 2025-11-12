Feature: Inventory Service UI
    As an inventory manager
    I need a user interface for the inventory service
    So that I can manage inventory items

    Background:
        Given the inventory service is running

    Scenario: The API is accessible
        When I visit the home page
        Then the page should load successfully

    Scenario: Listing inventory items
        When I visit the home page
        And I click the search button
        Then I should see a list of inventory items

    Scenario: Create an inventory item
        When I fill in the product ID with "12345"
        And I select condition "NEW"
        And I fill in quantity with "100"
        And I click the create button
        Then I should see "Success: Inventory item created!"

    # Scenario: Retrieve an inventory item
    #     When I click the search button
    #     And I enter "1" in the item ID field
    #     And I click the retrieve button
    #     Then I should see the item details in the form

    # Scenario: Update an inventory item
    #     When I fill in the product ID with "99999"
    #     And I select condition "NEW"
    #     And I fill in quantity with "100"
    #     And I click the create button
    #     And I fill in quantity with "200"
    #     And I click the update button
    #     Then I should see "Success: Inventory item updated!"

    Scenario: Restock an inventory item
        Given the inventory service is running
        When I visit the home page
        And I click the search button
        And I click the "Restock" action button for item with ID "123"
        Then I should see a success message "Success: Item restocked!"
        And the item with ID "123" should have its quantity updated
        