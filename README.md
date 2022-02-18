[![Build Status](https://travis-ci.com/ingoweiss/manyworlds.svg?branch=master)](https://travis-ci.com/ingoweiss/manyworlds)

Just playing around with the idea of scenario trees.

Having been frustrated with the amount of repetition and verbosity in automated tests (especially when using Gherkin syntax) for a long time, I felt that some of this could be addressed if behavior could be described as a tree of scenarios.

Just like regular scenarios, each scenario in the tree would have a name, a set of actions ('When ...') and a set of assertions ('Then ...').

*'Given...' steps, however, would no longer be needed since any scenario's 'Given' state would simply be the cumulative effect of running its chain of ancestor scenarios*.

The purpose of this project is to explore whether there is value in this concept. Currently, it does little more than parse a file describing a hierarchy of scenarios (using indentation) and flatten it so that it can be run with currently available tools, like so:

```python

import manyworlds as mw
mw.ScenarioForest.from_file('tree.feature').flatten('flat.feature')

```

The above reads a file that looks like this ...

```Cucumber

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
```

... and writes a file that looks like this:

```Cucumber

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
    
```

The nested version is significantly shorter by eliminating repetition. My hope is that it is also more structured and readable. 

In order to reap the full benefits of scenario trees, however, the test runner needs to be able to walk the scenario tree which is what I would like to explore next. This could be very efficient because if a scenario fails (in an action, not an assertion) then all its descendant scenarios can be marked as failed without running them!

Ultimately, instead of each scenario having to re-run all the actions of it's ancestor scenarios to re-create the necessary given state (which is what the generated flat scenario file does), I would like the tested application to be cloned, state and all, at each decision fork in the scenario tree (which reminds me of the 'many worlds interpretation' of quantum mechanics - hence the working title).

### Visualization

MW can also create a graph visualizing the scenario tree using [Mermaid](https://mermaid-js.github.io/mermaid/#/):

```python

mv.ScenarioForest.from_file('tree.feature').graph('tree.mermaid.txt')

```
 
  ![Tree graph](https://mermaid.ink/img/eyJjb2RlIjoiZ3JhcGggVERcbjAoVXNlcnMpXG4wIC0tPiAzKFNlbGVjdCB1c2VyKVxuMyAtLT4gNihEZXNlbGVjdCB1c2VyKVxuMyAtLT4gOShTZWxlY3QgYW5vdGhlciB1c2VyKVxuOSAtLT4gMTIoRGVzZWxlY3QgYWxsKVxuOSAtLT4gMTUoQnVsayBjaGFuZ2UgcGVybWlzc2lvbnMpXG5cdCIsIm1lcm1haWQiOnsidGhlbWUiOiJkZWZhdWx0In0sInVwZGF0ZUVkaXRvciI6ZmFsc2V9 "Title")

### Flattening Modes

By default, MW creates one scenario per node in the scenario tree, resulting in Gherkin with one set of 'When' actions followed by one set of 'Then' assertions which is generally considered best practice. This is the 'strict' mode.

MW also supports a 'relaxed' mode that creates one scenrio per _leaf node_ in the scenario tree, resulting in Gherkin that may have multipe consecutive 'When/Then' pairs in one scenario which is widely considered an anti-pattern. However, it does reduce repetition and is therefore shorter:

```python

mw.ScenarioForest.from_file('tree.feature').flatten('flat.feature', mode='relaxed')

```

This will write:

```Cucumber

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

```

### CLI

MW can be used from the command line like so:

```bash

python manyworlds_cli.py flatten --mode relaxed --input test/fixtures/scenarios_forest.feature --output test/out/scenarios_flat_relaxed.feature
python manyworlds_cli.py graph --input test/fixtures/scenarios_forest.feature --output test/out/scenarios.mermaid.txt
python manyworlds_cli.py --help

```

