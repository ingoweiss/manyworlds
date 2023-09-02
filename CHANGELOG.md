# Changelog

## [Unreleased]

### Changed

- Improved terminal output of scenario hierarchy (better branch lines)

## [0.3.0] - 2023-08-25

### Added

- Add support for data table row comments

## [0.2.0] - 2023-08-18

### Changed

- When using the cli, the --output parameter is now optional so that the cli can be used to print the scenario hierarchy to the terminal only
- Change naming scheme for output scenarios: It is now the same for strict and relaxed scenarios, and organizational scenario names are enclosed in angle brackets to distinguish them from regular scenarios

### Fixed

- The ScenarioForest#from_file method used to parse a scenario with excess indentation without error as long as there is a scenario at the parent level somewhere in the tree to connect to. This now raises an "InvalidFeatureFileError" (fixes #12)
- Fixed link to CHANGELOG.md in pyproject.toml (fixes #8)

## [0.1.0] - 2023-08-14

### Changed

- Change naming scheme for 'relaxed' output scenarios: All path scenario names are now joined using ' > ' rather than using ' > ' for organizational scenarios and ' / ' for validated scenarios

## [0.0.2] - 2023-08-11

### Changed

- Change naming of 'relaxed' scenarios to include the names of all scenarios in the scenario path (root to leaf scenario) that are either 'organizational' scenarios or 'validated' scenarios (scenarios for which assertions were written)

## [0.0.1] - 2023-08-08

- Initial release
