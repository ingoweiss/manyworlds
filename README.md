# Manyworlds

Organize BDD scenarios as directed graphs for more concise and expressive feature files.

[![Build](https://github.com/ingoweiss/manyworlds/actions/workflows/build.yml/badge.svg)](https://github.com/ingoweiss/manyworlds/actions/workflows/build.yml)
![PyPI - Version](https://img.shields.io/pypi/v/manyworlds)
![PyPI - License](https://img.shields.io/pypi/l/manyworlds)
[![Downloads](https://static.pepy.tech/badge/manyworlds)](https://pepy.tech/project/manyworlds)
![Style Black](https://img.shields.io/badge/style-black-000000)


BDD feature files can be verbose and repetitive. Consider the following four scenarios, represented as a series of actions (A) resulting in an observed outcome (O):

```text
S¹  A¹ → A² → A³: O¹
S²  A¹ → A² → A³ → A⁴: O²
S³  A¹ → A² → A³ → A⁵: O³
S⁴  A¹ → A² → A³ → A⁵ → A⁶: O⁴
```
All four scenarios (S¹–S⁴) share the first three actions (A¹, A², A³). Scenarios S³ and S⁴ share one additional action (A⁵). This is very repetitive and makes it hard to understand how the scenarios are organized.

Now consider the same scenarios represented as a directed graph:

```text
S¹  A¹ → A² → A³: O¹
S²             ↳ A⁴: O²
S³             ↳ A⁵: O³
S⁴                ↳ A⁶: O⁴
```
The graph format has a few benefits:
1. Many actions are now implied by their scenario's position in the graph and no longer need to be stated which eliminates repetition and noise.
2. We can now see how scenarios relate to each other. Specifically, we can start thinking in terms of parent and child scenarios.
3. We now have what amounts to a decision tree of possible paths that a user can take through the app. This makes it easier to notice missing scenarios.

So how could we start experimenting with scenario graphs using existing tools? What if we could simply use _indentation_ in feature files? This would limit us to one type of graph (trees/forests), but maybe that would cover the vast majority of use cases? That is the idea behind Manyworlds. With Manyworlds we can:
 1. Use indentation in feature files to organize scenarios as scenario trees.
 2. Expand indented feature files into standard, flat feature files which can be run using any testing tool that understands Gherkin.

## Usage

Here is an example of an indented feature file:

```Cucumber
# indented.feature

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
                    And I see the following users:
                        | Name   | Status |
                        | Ben    | Active | # still there
                        | Alice  | Active | # still there
                        | Connie | Active |
```

Now let's use Manyworlds to flatten it:

```bash
python -m manyworlds --input indented.feature --output flat.feature
```
This will print the structure of the scenario tree(s) to the terminal …

```bash
View users
├── Deactivate user
└── Bulk operations:
    └── Select user
        ├── Deselect user
        └── Select multiple users
            ├── Deselect all users
            └── Bulk deactivate users
                ├── Confirm bulk deactivation of users
                └── Cancel out of bulk deactivation of users
```
… and write the following flat feature file:

```Cucumber
# flat.feature

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

By default, Manyworlds creates one scenario per _node_ in the scenario tree, resulting in scenarios with one set of "whens" followed by one set of "thens" which is generally considered best practice. This is the "strict" mode.

Manyworlds also supports a "relaxed" mode that creates one scenario per _leaf node_ in the scenario tree, resulting in fewer scenarios that may have multiple consecutive "when/then" pairs which is widely considered an anti-pattern. For starters, it makes it hard to name scenarios well. However, it does reduce repetition and will run faster:

```bash
python -m manyworlds --input indented.feature --output flat_relaxed.feature --mode relaxed
```

This will write the following "relaxed" flat feature file:

```Cucumber
# flat_relaxed.feature

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

### File Size

Manyworlds feature files are significantly shorter than the conventional output feature files, which is another reason I why find them easier to maintain. The exact factor is a function mostly of the depth of the scenario tree. A factor of around 3 is not uncommon.

### Organizational Scenarios

Scenarios without assertions are considered "organizational" and are used to group child scenarios only. In output feature files, organizationasl scenarios will not appear as their own scenarios, but their names are used as a "breadcrumb" in the names of their child scenarios. The "Bulk Operations" scenario in the above example is organizational.

### Comments

You can add inline comments to just about anything in Manyworlds feature files: Steps, scenarios and even data table rows! This is in contrast to the [Gherkin specification](https://cucumber.io/docs/gherkin/reference) which only allows comments on separate lines. Comments are stripped in Manyworlds output files so they validate as Gherkin.

### Using the Feature Class Directly

If you want to use Manyworlds in your code rather than using the cli, here's how to do that:

```python
import manyworlds as mw
mw.Feature.from_file('hierarchical.feature').flatten('flat.feature')
```

### Installation

```bash
pip install manyworlds
```

### What If Test Runners Could Run Scenario Trees Directly?

I believe this is where it could get really interesting. A few examples:

1. If a scenario fails in an action, the runner could mark all descendent scenarios as failing without even running them!
2. A runner could use the 'relaxed' mode under the hood to run scenarios optimized for speed, then display test results using the 'strict' mode optimized for informational clarity.
3. A runner could use network analysis tools to decide how to cleave apart the tree for optimal parallelization.

I would think that these might result in significantly faster running (and faster failing) test suites. The display of test results might also be significantly more informative compared to what we have today.
