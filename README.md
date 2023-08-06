[![Build Status](https://travis-ci.com/ingoweiss/manyworlds.svg?branch=master)](https://travis-ci.com/ingoweiss/manyworlds)

BDD scenarios tend to be verbose and repetitive. Consider the following abstract representation of four quite typical scenarios:

```text

G1 → W1 → W2: T1
G1 → W1 → W2 → W3: T2
G1 → W1 → W2 → W4: T3
G1 → W1 → W2 → W4 → W5: T4

```

All four scenarios share the same prerequisite or "Given" step (G1) and one action or "When" step (W1). Scenario 3 and 4 share all prerequisites (G1) and three actions (W1, W2, W4). This is very repetetive and it is hard to see how the scenarios are organized. The same scenarios can be represented much more consisely as a tree:

```text

G1 → W1 → W2: T1
           ⮑ W3: T2
           ⮑ W4: T3
              ⮑ W5: T4
```

The purpose of this project is to explore whether there is value in this concept. Currently, it does little more than parse a file describing a hierarchy of scenarios (using indentation) and flatten it so that it can be run with currently available tools, like so:

```bash

python -m manyworlds --input ./scenarios.feature --output ./scenarios_flat.feature

```

The above reads a file that looks like this ...

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

... and writes a file that looks like this:

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

```

… in additionn to printing the structure of the scenaro forest:

```bash

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

The nested version is significantly shorter by eliminating repetition. I also find it more structured and readable. 

In order to reap the full benefits of scenario trees, however, the test runner would need to be able to walk the scenario tree. Ultimately, instead of each scenario having to re-run all the actions of it's ancestor scenarios to re-create the necessary given state (which is what the generated flat scenario file does), I would like the tested application to be cloned, state and all, at each decision fork in the scenario tree (which reminds me of the 'many worlds interpretation' of quantum mechanics - hence the working title).

### Flattening Modes

By default, MW creates one scenario per node in the scenario tree, resulting in Gherkin with one set of 'When' actions followed by one set of 'Then' assertions which is generally considered best practice. This is the 'strict' mode.

MW also supports a 'relaxed' mode that creates one scenrio per _leaf node_ in the scenario tree, resulting in Gherkin that may have multipe consecutive 'When/Then' pairs in one scenario which is widely considered an anti-pattern. For once, it makes it hard to name the scenarios well. However, it does reduce repetition and is therefore shorter:

```bash

python -m manyworlds --input ./scenarios.feature --output ./scenarios_flat.feature --mode relaxed

```

This will write:

```Cucumber

Scenario: Deactivate user
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

Scenario: Bulk operations > Deselect user
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
Then I see "2 users selected"
When I click "Deselect all"
Then I see "0 users selected"

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
Then I see a confirmation dialog
When I click "OK"
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

```

### Using the ScenarioForest class directly

If you want to use manyworlds in your code rather than using the cli here's how to to do that:

```python

import manyworlds as mw
mw.ScenarioForest.from_file('tree.feature').flatten('flat.feature')

```

### Installation

```bash

pip install manyworlds

```
