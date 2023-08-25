# Manyworlds

Organize BDD scenarios as hierarchical trees for more concise and expressive feature files.

[![Pytest](https://github.com/ingoweiss/manyworlds/actions/workflows/pytest.yml/badge.svg)](https://github.com/ingoweiss/manyworlds/actions/workflows/pytest.yml)
[![Ruff](https://github.com/ingoweiss/manyworlds/actions/workflows/ruff.yml/badge.svg)](https://github.com/ingoweiss/manyworlds/actions/workflows/ruff.yml)
[![MyPy](https://github.com/ingoweiss/manyworlds/actions/workflows/mypy.yml/badge.svg)](https://github.com/ingoweiss/manyworlds/actions/workflows/mypy.yml)
[![MyPy](https://github.com/ingoweiss/manyworlds/actions/workflows/black.yml/badge.svg)](https://github.com/ingoweiss/manyworlds/actions/workflows/black.yml)

BDD scenarios tend to be verbose and repetitive. Consider the following four scenarios, represented as a series of actions (A) resulting in an observed outcome (O):

```text
A1 → A2 → A3: O1
A1 → A2 → A3 → A4: O2
A1 → A2 → A3 → A5: O3
A1 → A2 → A3 → A5 → A6: O4
```
All four scenarios share the first three actions (A1, A2, A3). Scenario 3 and 4 share one additional action (A5). This is very repetitive and makes it hard to understand how the scenarios are organized.

Now consider the same scenarios represented as a tree:

```text
A1 → A2 → A3: O1
           ↳ A4: O2
           ↳ A5: O3
              ↳ A6: O4
```
The tree structure has a few advantages:
1. Many actions are now implied by their scenario's position in the tree and no longer need to be stated which eliminates repetition and noise.
2. We can now see how scenarios relate to each other. Specifically, we can start thinking in terms of parent and child scenarios.
3. We now have what amounts to a decision tree of possible paths that a user can take through the app. This makes it easier to notice gaps in the scenarios.

 Manyworlds provides a simple way to reap the benefits of scenario trees. It enables you to:
 1. Use indentation in Gherkin feature files to organize scenarios hierarchically.
 2. Expand hierarchical feature files into standard flat feature files which can be run using any testing tool that understands Gherkin.

## Usage

Here is an example of an indented, hierarchical feature file:

```Cucumber
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
```

Now let's use Manyworlds to expand it:

```bash
python -m manyworlds --input hierarchical.feature --output flat.feature
```
This will print the structure of the scenario tree(s) to the terminal:

```text
View users
└─ Deactivate user
└─ Bulk operations
   └─ Select user
      └─ Deselect user
      └─ Select multiple users
         └─ Deselect all users
         └─ Bulk deactivate users
            └─ Confirm bulk deactivation of users
            └─ Cancel out of bulk deactivation of users
```
and write the following flat feature file:

```Cucumber
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

Scenario: [Bulk operations] Select user
Given the following users:
    | Name   | Status      |
    | Ben    | Active      |
    | Alice  | Active      |
    | Connie | Active      |
    | Dan    | Deactivated |
When I go to "Users"
 And I select user "Ben"
Then I see "1 user selected"

Scenario: [Bulk operations] Deselect user
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

Scenario: [Bulk operations] Select multiple users
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

Scenario: [Bulk operations] Deselect all users
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

Scenario: [Bulk operations] Bulk deactivate users
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

Scenario: [Bulk operations] Confirm bulk deactivation of users
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
```
### Flattening Modes

By default, Manyworlds creates one scenario per node in the scenario tree, resulting in scenarios with one set of "whens" followed by one set of "thens" which is generally considered best practice. This is the "strict" mode.

Manyworlds also supports a "relaxed" mode that creates one scenario per _leaf node_ in the scenario tree, resulting in scenarios that may have multiple consecutive "when/then" pairs which is widely considered an anti-pattern. For starters, it makes it hard to name scenarios well. However, it does reduce repetition and is therefore shorter and will run faster:

```bash
python -m manyworlds --input hierarchical.feature --output flat.feature --mode relaxed
```

This will write the following "relaxed" flat feature file:

```Cucumber
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
```
### Organizational Scenarios

Scenarios without assertions are considered "organizational" and are used to group child scenarios only. In output feature files, organizationasl scenarios will not appear as their own scenarios, but their names are used as a "breadcrumb" in the names of their child scenarios. The "Bulk operations" scenario in the above example is organizational.

### Using the ScenarioForest Class Directly

If you want to use Manyworlds in your code rather than using the cli, here's how to to do that:

```python
import manyworlds as mw
mw.ScenarioForest.from_file('hierarchical.feature').flatten('flat.feature')
```

### Installation

```bash
pip install manyworlds
```
