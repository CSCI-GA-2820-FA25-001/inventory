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

    Scenario: Retrieve an inventory item
        When I fill in the product ID with "88888"
        And I select condition "USED"
        And I fill in quantity with "50"
        And I fill in restock level with "10"
        And I fill in restock amount with "20"
        And I click the create button
        Then I should see "Success: Inventory item created!"
        When I store the created item ID
        And I click the clear button
        And I enter the stored item ID in the item ID field
        And I click the retrieve button
        Then I should see the item details in the form
        And the product ID field should contain "88888"

    Scenario: Update an inventory item
        When I fill in the product ID with "99999"
        And I select condition "NEW"
        And I fill in quantity with "100"
        And I click the create button
        Then I should see "Success: Inventory item created!"
        When I fill in quantity with "200"
        And I click the update button
        Then I should see "Success: Inventory item updated!"

    Scenario: Query inventory by condition
        # Create test data
        When I fill in the product ID with "11111"
        And I select condition "NEW"
        And I fill in quantity with "10"
        And I click the create button
        Then I should see "Success: Inventory item created!"
        When I click the clear button
        And I fill in the product ID with "22222"
        And I select condition "USED"
        And I fill in quantity with "20"
        And I click the create button
        Then I should see "Success: Inventory item created!"
        # Test filtering
        When I click the clear button
        And I select condition "NEW"
        And I click the search button
        Then I should see "11111" in the results table
        And I should not see "22222" in the results table

    Scenario: Query inventory with quantity filter
        # Create test data
        When I fill in the product ID with "33333"
        And I select condition "NEW"
        And I fill in quantity with "5"
        And I click the create button
        Then I should see "Success: Inventory item created!"
        When I click the clear button
        And I fill in the product ID with "44444"
        And I select condition "NEW"
        And I fill in quantity with "15"
        And I click the create button
        Then I should see "Success: Inventory item created!"
        # Test quantity_lt filter (though UI doesn't have this field yet)
        When I click the clear button
        And I click the search button
        Then I should see both items in the results

    Scenario: Restock an inventory item
        When I fill in the product ID with "55555"
        And I select condition "NEW"
        And I fill in quantity with "10"
        And I fill in restock level with "5"
        And I fill in restock amount with "20"
        And I click the create button
        Then I should see "Success: Inventory item created!"
        When I store the created item ID
        And I click the clear button
        And I enter the stored item ID in the item ID field
        And I click the retrieve button
        Then the quantity field should contain "10"
        When I click the restock button
        Then I should see "Success: Item restocked!"
        And the quantity field should contain "30"

    Scenario: Delete an inventory item
        When I fill in the product ID with "66666"
        And I select condition "OPEN_BOX"
        And I fill in quantity with "25"
        And I click the create button
        Then I should see "Success: Inventory item created!"
        When I click the delete button
        Then I should see "Success: Inventory item has been deleted!"
        And the form should be cleared