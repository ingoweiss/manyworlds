# Changelog

## [Unreleased]

### Changed

- When using the cli, the --output parameter is now optional so that one can use the cli to print the scenario hierarchy only

### Fixed

- The ScenarioForest#from_file method used to parse a scenario with excess indentation without error as long as there is a scenario at the parent level somewhere in the tree to connect to. This now raises an "InvalidFeatureFileError" (fixes #12)
- Fixed link to CHANGELOG.md in pyproject.toml (fixes #8)

## [0.1.0] - 2023-08-14

### Changed

- Change naming scheme for output scenarios: Organizational scenario names are now enclosed in angle brackets to distinguish them from regular scenarios

## [0.0.2] - 2023-08-11

### Changed

- Change naming of 'relaxed' scenarios to include the names of all scenarios in the scenario path (root to leaf scenario) that are either 'organizational' scenarios or 'validated' scenarios (scenarios for which assertions were written)

## [0.0.1] - 2023-08-08

- Initial release
