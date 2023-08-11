Scenario: View users
Givven the following users: # invalid line
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