Feature: User Deactivation

    As an administrator
    I want to deactivate users who leave the company
    So that only authorized users have access to the system

Scenario: View users > Deactivate user
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
When I go to "Users"
Then I see the following users:
    | Name   | Status |
    | Ben    | Active |
    | Alice  | Active |
    | Connie | Active |
When I click "Deactivate" for user "Ben"
 And I click "OK"
Then I see the following users:
    | Name   | Status |
    | Alice  | Active |
    | Connie | Active |

Scenario: [Bulk operations] Select user > Deselect user
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
When I go to "Users"
 And I select user "Ben"
Then I see "1 user selected"
When I deselect user "Ben"
Then I see "0 users selected"

Scenario: [Bulk operations] Select multiple users > Deselect all users
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
When I go to "Users"
 And I select user "Ben"
 And I select user "Alice"
Then I see "2 users selected"
When I click "Deselect all"
Then I see "0 users selected"

Scenario: [Bulk operations] Bulk deactivate users > Confirm bulk deactivation of users
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
When I go to "Users"
 And I select user "Ben"
 And I select user "Alice"
 And I click "Deactivate all"
Then I see a confirmation dialog
When I click "OK"
Then I see "0 users selected"
 And I see the following users:
    | Name   | Status |
    | Connie | Active |

Scenario: [Bulk operations] Cancel out of bulk deactivation of users
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
When I go to "Users"
 And I select user "Ben"
 And I select user "Alice"
 And I click "Deactivate all"
 And I click "Cancel"
Then I see "2 users selected"
 And I see the following users:
    | Name   | Status |
    | Ben    | Active |
    | Alice  | Active |
    | Connie | Active |

