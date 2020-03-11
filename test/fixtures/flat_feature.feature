Scenario: Users
When I go to "Users"
Then I see "Users"

Scenario: Users > Select user
When I go to "Users"
And I select user "Ben"
Then I see "1 user selected"

Scenario: Users > Select user > Deselect user
When I go to "Users"
And I select user "Ben"
And I deselect user "Ben"
Then I see "0 users selected"

Scenario: Users > Select user > Select another user
When I go to "Users"
And I select user "Ben"
And I select user "Alice"
Then I see "2 users selected"

Scenario: Users > Select user > Select another user > Deselect all
When I go to "Users"
And I select user "Ben"
And I select user "Alice"
And I click "Deselect all"
Then I see "0 users selected"

Scenario: Users > Select user > Select another user > Bulk change permissions
When I go to "Users"
And I select user "Ben"
And I select user "Alice"
And I select "Edit" from "Permissions"
And I click "Apply to selected"
Then I see "2 users changed"
And I see "2 users selected"

