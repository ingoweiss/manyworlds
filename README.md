Just playing around with the idea of scenario trees.

Currently, the code does little more than parse a file describing a hierarchy of scenarios (using indentation) and flatten it so that it can be run with currently available tools, like so:

    mw.ScenarioTree('tree.feature').flatten('flat.feature')

The above reads the file 'tree.feature' ...

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

... and writes the file 'flat.feature':

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

The nested version eliminates repetition and therefore is a bit more compact. My hope is that is is more structured and readable. Both could already provide some benefits.

In order to reap the real benefits of scenario trees, however, the code needs to be able to run tests by walking the scenario tree which is what I would like to explore next. This could be very efficient because if a scenario fails (in an action, not an assertion) then all it's descendant scenarios can be marked as failed without running them!

Ultimately, instead of each scenario having to run all the actions of it's ancestor scenarios to re-create the necessary given state (which is what the generated flat scenario file does), I would like the tested application to be cloned, state and all, at each decision fork in the scenario tree (which reminds me of the 'many worlds interpretation' of quantum mechanics - hence the working title).

The code can also create a graph visualizing the scenario tree using Mermaid:

    mv.ScenarioTree('tree.feature').graph('tree.mermaid.txt')

 
 The above writes the file 'tree.mermaid.txt' describing the scenario tree in the Mermaid syntax which can be used to create this graph:
 
 ![Tree graph](https://mermaid.ink/img/eyJjb2RlIjoiZ3JhcGggVERcbjAoVXNlcnMpXG4wIC0tPiAzKFNlbGVjdCB1c2VyKVxuMyAtLT4gNihEZXNlbGVjdCB1c2VyKVxuMyAtLT4gOShTZWxlY3QgYW5vdGhlciB1c2VyKVxuOSAtLT4gMTIoRGVzZWxlY3QgYWxsKVxuOSAtLT4gMTUoQnVsayBjaGFuZ2UgcGVybWlzc2lvbnMpXG5cdCIsIm1lcm1haWQiOnsidGhlbWUiOiJkZWZhdWx0In0sInVwZGF0ZUVkaXRvciI6ZmFsc2V9 "Title")
