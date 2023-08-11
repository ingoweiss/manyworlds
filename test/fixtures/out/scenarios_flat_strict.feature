Scenario: View users
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

Scenario: Deactivate user
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
When I go to "Users"
 And I click "Deactivate" for user "Ben"
 And I click "OK"
Then I see the following users:
    | Name   | Status |
    | Alice  | Active |
    | Connie | Active |

Scenario: Bulk operations > Select user
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
When I go to "Users"
 And I select user "Ben"
Then I see "1 user selected"

Scenario: Bulk operations > Deselect user
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
When I go to "Users"
 And I select user "Ben"
 And I deselect user "Ben"
Then I see "0 users selected"

Scenario: Bulk operations > Select multiple users
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

Scenario: Bulk operations > Deselect all users
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
When I go to "Users"
 And I select user "Ben"
 And I select user "Alice"
 And I click "Deselect all"
Then I see "0 users selected"

Scenario: Bulk operations > Bulk deactivate users
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

Scenario: Bulk operations > Confirm bulk deactivation of users
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
 And I click "OK"
Then I see "0 users selected"
 And I see the following users:
    | Name   | Status |
    | Connie | Active |

Scenario: Bulk operations > Cancel out of bulk deactivation of users
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

