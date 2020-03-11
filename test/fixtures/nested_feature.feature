Scenario: Users
Given I go to "Users"
Then I see "Users"

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
            When I click "Apply to selected"
            Then I see "2 users changed"
            Then I see "2 users selected"