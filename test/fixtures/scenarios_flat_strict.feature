Scenario: Users
When the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
And I go to "Users"
Then I see the following "Users":
    | Name   | Status |
    | Ben    | Active |
    | Alice  | Active |
    | Connie | Active |

Scenario: Select user
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
And I go to "Users"
When I select user "Ben"
Then I see "1 user selected"

Scenario: Deselect user
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
And I go to "Users"
And I select user "Ben"
When I deselect user "Ben"
Then I see "0 users selected"

Scenario: Select another user
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
And I go to "Users"
And I select user "Ben"
When I select user "Alice"
Then I see "2 users selected"

Scenario: Deselect all
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
And I go to "Users"
And I select user "Ben"
And I select user "Alice"
When I click "Deselect all"
Then I see "0 users selected"

Scenario: Bulk change permissions
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
And I go to "Users"
And I select user "Ben"
And I select user "Alice"
When I select "Edit" from "Permissions"
And I click "Apply to selected"
Then I see "2 users changed"
And I see "2 users selected"

