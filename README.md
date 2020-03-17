Just playing around with the idea of scenario trees.

Having been frustrated with the amount of repetition and verbosity in automated tests (especially when using Gherkin syntax) for a long time, I felt that some of this could be addressed if behavior would be described in the form of a (decision) tree of scenarios. Each scenario in the tree would have a name, a set of actions ('When ...') and a set of assertions ('Then ...') just like regular scenarios. 'Given...' steps, however, would no longer be needed since the 'Given' state would be nothing more than the cumulative effect of each scenario's chain of ancestor scenarios.

The purpose of this project is to explore this concept. Currently, it does little more than parse a file describing a hierarchy of scenarios (using indentation) and flatten it so that it can be run with currently available tools, like so:

    mw.ScenarioTree('tree.feature').flatten('flat.feature')

The above reads a file that looks like this ...

    Scenario: Users
    When I go to "Users"
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

... and writes a file that looks like this:

    Scenario: Users
    When I go to "Users"
    Then I see "Users"
    
    Scenario: Users > Select user
    Given I go to "Users"
    When I select user "Ben"
    Then I see "1 user selected"
    
    Scenario: Users > Select user > Deselect user
    Given I go to "Users"
    And I select user "Ben"
    When I deselect user "Ben"
    Then I see "0 users selected"
    
    Scenario: Users > Select user > Select another user
    Given I go to "Users"
    And I select user "Ben"
    When I select user "Alice"
    Then I see "2 users selected"
    
    Scenario: Users > Select user > Select another user > Deselect all
    Given I go to "Users"
    And I select user "Ben"
    And I select user "Alice"
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

The nested version is significantly shorter by eliminating repetition. My hope is that it is also more structured and readable. 

In order to reap the full benefits of scenario trees, however, the test runner needs to be able to walk the scenario tree which is what I would like to explore next. This could be very efficient because if a scenario fails (in an action, not an assertion) then all it's descendant scenarios can be marked as failed without running them!

Ultimately, instead of each scenario having to re-run all the actions of it's ancestor scenarios to re-create the necessary given state (which is what the generated flat scenario file does), I would like the tested application to be cloned, state and all, at each decision fork in the scenario tree (which reminds me of the 'many worlds interpretation' of quantum mechanics - hence the working title).

The library can also create a graph visualizing the scenario tree using [Mermaid](https://mermaid-js.github.io/mermaid/#/):

    mv.ScenarioTree('tree.feature').graph('tree.mermaid.txt')

 
  ![Tree graph](https://mermaid.ink/img/eyJjb2RlIjoiZ3JhcGggVERcbjAoVXNlcnMpXG4wIC0tPiAzKFNlbGVjdCB1c2VyKVxuMyAtLT4gNihEZXNlbGVjdCB1c2VyKVxuMyAtLT4gOShTZWxlY3QgYW5vdGhlciB1c2VyKVxuOSAtLT4gMTIoRGVzZWxlY3QgYWxsKVxuOSAtLT4gMTUoQnVsayBjaGFuZ2UgcGVybWlzc2lvbnMpXG5cdCIsIm1lcm1haWQiOnsidGhlbWUiOiJkZWZhdWx0In0sInVwZGF0ZUVkaXRvciI6ZmFsc2V9 "Title")
