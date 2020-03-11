Just playing around with the idea of Gherkin scenario trees.

Currently, all the code does is read a Gherkin file that describes a hierarchy of scenarios using indentation ...


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
	            And I click "Apply to selected"
	            Then I see "2 users changed"
	            And I see "2 users selected"


...and write a flat Gherkin file that can be run:

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

 The nested version eliminates repetition and therefore is a bit more compact. My hope is that is is more readable.
 
 Far down the road, I think it would be awesome to run tests by walking the scenario tree which could be very efficient. If a scenario fails (in an action, not an assertion) then you can mark all descendant scenarios as failed without running them!
