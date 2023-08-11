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
    When I click "Deactivate" for user "Ben"
    And I click "OK"
    Then I see the following users: # I no longer see Ben
        | Name   | Status |
        | Alice  | Active |
        | Connie | Active |

    Scenario: Bulk operations

        Scenario: Select user
        When I select user "Ben"
        Then I see "1 user selected"
        
            Scenario: Deselect user
            When I deselect user "Ben"
            Then I see "0 users selected"
            
            Scenario: Select multiple users
            When I select user "Alice"
            Then I see "2 users selected"
            
                Scenario: Deselect all users
                When I click "Deselect all"
                Then I see "0 users selected"
                
                Scenario: Bulk deactivate users
                When I click "Deactivate all"
                Then I see a confirmation dialog

                    Scenario: Confirm bulk deactivation of users
                    When I click "OK"
                    Then I see "0 users selected"
                    And I see the following users: # I no longer see Ben or Alice
                        | Name   | Status |
                        | Connie | Active |

                    Scenario: Cancel out of bulk deactivation of users
                    When I click "Cancel"
                    Then I see "2 users selected"
                    And I see the following users: # same as before
                        | Name   | Status |
                        | Ben    | Active |
                        | Alice  | Active |
                        | Connie | Active |
