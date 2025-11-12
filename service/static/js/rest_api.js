$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#item_id").val(res.id);
        $("#product_id").val(res.product_id);
        $("#condition").val(res.condition);
        $("#quantity").val(res.quantity);
        $("#restock_level").val(res.restock_level);
        $("#restock_amount").val(res.restock_amount);
        $("#description").val(res.description);
    }

    // Clears all form fields
    function clear_form_data() {
        $("#item_id").val("");
        $("#product_id").val("");
        $("#condition").val("");
        $("#quantity").val("");
        $("#restock_level").val("");
        $("#restock_amount").val("");
        $("#description").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // CREATE an Inventory Item
    // ****************************************
    
    $("#create-btn").click(function () {
    
        let product_id = $("#product_id").val();
        let condition = $("#condition").val();
        let quantity = $("#quantity").val();
        let restock_level = $("#restock_level").val();
        let restock_amount = $("#restock_amount").val();
        let description = $("#description").val();
    
        // Validation: Check required fields
        if (!product_id) {
            flash_message("Error: Product ID is required!");
            return;
        }
        if (!condition) {
            flash_message("Error: Condition is required!");
            return;
        }
        if (!quantity) {
            flash_message("Error: Quantity is required!");
            return;
        }
    
        let data = {
            "product_id": parseInt(product_id),
            "condition": condition,
            "quantity": parseInt(quantity),
            "restock_level": parseInt(restock_level) || 0,
            "restock_amount": parseInt(restock_amount) || 0,
            "description": description || ""
        };
    
        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/inventory",
            contentType: "application/json",
            data: JSON.stringify(data),
        });
    
        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success: Inventory item created!");
        });
    
        ajax.fail(function(res){
            flash_message(res.responseJSON?.message || "Error: Failed to create inventory item!");
        });
    });

    // ****************************************
    // UPDATE an Inventory Item
    // ****************************************
    
    $("#update-btn").click(function () {
    
        let item_id = $("#item_id").val();
        let product_id = $("#product_id").val();
        let condition = $("#condition").val();
        let quantity = $("#quantity").val();
        let restock_level = $("#restock_level").val();
        let restock_amount = $("#restock_amount").val();
        let description = $("#description").val();
    
        // Validation: Check that item_id exists
        if (!item_id) {
            flash_message("Error: Item ID is required for update! Please retrieve an item first.");
            return;
        }
    
        // Validation: Check required fields
        if (!product_id) {
            flash_message("Error: Product ID is required!");
            return;
        }
        if (!condition) {
            flash_message("Error: Condition is required!");
            return;
        }
        if (!quantity) {
            flash_message("Error: Quantity is required!");
            return;
        }
    
        let data = {
            "product_id": parseInt(product_id),
            "condition": condition,
            "quantity": parseInt(quantity),
            "restock_level": parseInt(restock_level) || 0,
            "restock_amount": parseInt(restock_amount) || 0,
            "description": description || ""
        };
    
        $("#flash_message").empty();
    
        let ajax = $.ajax({
            type: "PUT",
            url: `/inventory/${item_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });
    
        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success: Inventory item updated!");
        });
    
        ajax.fail(function(res){
            flash_message(res.responseJSON?.message || "Error: Failed to update inventory item!");
        });
    });

    // ****************************************
    // RETRIEVE AN INVENTORY ITEM
    // ****************************************

    $("#retrieve-btn").click(function () {
        let item_id = $("#item_id").val();

        if (!item_id) {
            flash_message("Error: Please enter an Item ID");
            return;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/inventory/${item_id}`,
            contentType: "application/json"
        });

        ajax.done(function (res) {
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function (res) {
            clear_form_data();
            flash_message(res.responseJSON?.message || "Item not found!");
        });
    });    

    // ****************************************
    // LIST (Search for Inventory Items)
    // ****************************************

    $("#search-btn").click(function () {

        let product_id = $("#product_id").val();
        let condition = $("#condition").val();
        let description = $("#description").val();

        let queryString = "";

        if (product_id) {
            queryString += "product_id=" + product_id;
        }
        if (condition) {
            if (queryString.length > 0) queryString += "&";
            queryString += "condition=" + condition;
        }
        if (description) {
            if (queryString.length > 0) queryString += "&";
            queryString += "query=" + encodeURIComponent(description);
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/inventory?${queryString}`,
            contentType: "application/json",
            data: ""
        });

        ajax.done(function (res) {
            $("#search_results").empty();

            let table = '<table class="table table-striped" cellpadding="10">';
            table += '<thead><tr>';
            table += '<th class="col-md-1">ID</th>';
            table += '<th class="col-md-2">Product ID</th>';
            table += '<th class="col-md-2">Condition</th>';
            table += '<th class="col-md-2">Quantity</th>';
            table += '<th class="col-md-2">Restock Level</th>';
            table += '<th class="col-md-2">Restock Amount</th>';
            table += '<th class="col-md-3">Description</th>';
            table += '</tr></thead><tbody>';

            let firstItem = "";
            for (let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `<tr id="row_${i}">
                            <td>${item.id}</td>
                            <td>${item.product_id}</td>
                            <td>${item.condition}</td>
                            <td>${item.quantity}</td>
                            <td>${item.restock_level}</td>
                            <td>${item.restock_amount}</td>
                            <td>${item.description}</td>
                          </tr>`;
                if (i === 0) {
                    firstItem = item;
                }
            }

            table += '</tbody></table>';
            $("#search_results").append(table);

            // Copy the first result to the form
            if (firstItem) {
                update_form_data(firstItem);
            }

            flash_message("Success");
        });

        ajax.fail(function (res) {
            clear_form_data();
            flash_message(res.responseJSON?.message || "Server error!");
        });
    });


    // ****************************************
    // DELETE an Inventory Item
    // ****************************************
    
    $("#delete-btn").click(function () {
    
        let item_id = $("#item_id").val();
    
        // Validation: Check that item_id exists
        if (!item_id) {
            flash_message("Error: Item ID is required for delete! Please retrieve an item first.");
            return;
        }
    
        $("#flash_message").empty();
    
        let ajax = $.ajax({
            type: "DELETE",
            url: `/inventory/${item_id}`,
            contentType: "application/json",
            data: ''
        });
    
        ajax.done(function(res){
            clear_form_data();
            flash_message("Success: Inventory item has been deleted!");
        });
    
        ajax.fail(function(res){
            flash_message(res.responseJSON?.message || "Error: Failed to delete inventory item!");
        });
    });
    

    // ****************************************
    // CLEAR THE FORM
    // ****************************************

    $("#clear-btn").click(function () {
        $("#item_id").val("");
        $("#flash_message").empty();
        clear_form_data();
        $("#search_results").empty();
    });

    // ****************************************
    // PLACEHOLDER BUTTONS (Not Implemented)
    // ****************************************

    $("#delete-btn, #restock-btn").click(function () {
        flash_message("⚠️ This function is not implemented yet.");
    });

    // ****************************************
    // AUTO LOAD LIST ON PAGE LOAD
    // ****************************************

    $("#search-btn").click();
});
