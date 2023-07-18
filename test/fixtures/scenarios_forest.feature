Scenario: Users
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
When I go to "Users"
Then I see the following "Users":
    | Name   | Status |
    | Ben    | Active |
    | Alice  | Active |
    | Connie | Active |

    Scenario: Select user
    When I select user "Ben"
    Then I see "1 user selected"
    
        Scenario: Deselect user
        When I deselect user "Ben"
        Then I see "0 users selected"
        
        Scenario: Select another user
        When I select user "Alice"
        Then I see "2 users selected"
        
            Scenario: Deselect all
            When I click "Deselect all"
            Then I see "0 users selected"
            
            Scenario: Bulk change permissions
            When I select "Edit" from "Permissions"
            And I click "Apply to selected"
            Then I see "2 users changed"
            And I see "2 users selected"