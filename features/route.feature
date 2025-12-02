Feature: OpenShift Route Exposure
    As a DevOps Engineer
    I need to verify the inventory microservice route
    So that it can be accessed from outside the OpenShift cluster

    Background:
        Given the inventory microservice is deployed to OpenShift

    Scenario: Route is properly configured
        When I create a route using "oc expose service inventory"
        Then the route should be visible in "oc get routes"
        And the route should have the name "inventory"
        And the route should target service "inventory"
        And the route should target port "8080"

    Scenario: Microservice is accessible via route
        Given a route exists for the inventory service
        When I get the route URL
        Then the microservice should be accessible via the route URL
        And GET request to "{route-url}/api/inventory" returns 200 OK
        And GET request to "{route-url}/health" returns 200 OK

    Scenario: API documentation is accessible
        Given a route exists for the inventory service
        When I get the route URL
        Then the Swagger docs are accessible at "{route-url}/apidocs"
        And GET request to "{route-url}/apidocs" returns 200 OK

    Scenario: Route handles API operations correctly
        Given a route exists for the inventory service
        And I have the route URL
        When I POST a new inventory item via the route
        Then I should receive a 201 Created response
        And the Location header should contain the route URL
        When I GET the created item via the route
        Then I should receive a 200 OK response
        And the response should contain the correct item data