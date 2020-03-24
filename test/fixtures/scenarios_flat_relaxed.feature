Scenario: Users > Select user > Deselect user
When I go to "Users"
Then I see "Users"
When I select user "Ben"
Then I see "1 user selected"
When I deselect user "Ben"
Then I see "0 users selected"

Scenario: Users > Select user > Select another user > Deselect all
Given I go to "Users"
And I select user "Ben"
When I select user "Alice"
Then I see "2 users selected"
When I click "Deselect all"
Then I see "0 users selected"

Scenario: Users > Select user > Select another user > Bulk change permissions
Given I go to "Users"
And I select user "Ben"
And I select user "Alice"
When I select "Edit" from "Permissions"
And I click "Apply to selected"
Then I see "2 users changed"
And I see "2 users selected"

