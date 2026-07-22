## Requirements

### Requirement: Document first-use audit setup

The project documentation SHALL explain that users can run `repository-hygiene install .` to create the default `auditoria.yaml` configuration before running an audit.

#### Scenario: New user prepares repository
- **WHEN** user follows the documented first-use workflow in a repository without audit configuration
- **THEN** documentation directs user to run `repository-hygiene install .` before `repository-hygiene audit .`

### Requirement: Document report file generation

The project documentation SHALL provide commands that save text, JSON, and SARIF audit output to named files using the supported `--format` values and shell output redirection.

#### Scenario: User creates text report file
- **WHEN** user follows the text report example
- **THEN** command writes audit output to a text file

#### Scenario: User creates machine-readable report files
- **WHEN** user follows JSON or SARIF report examples
- **THEN** commands write output to files with the corresponding format and extension

### Requirement: Document audit exit codes with saved reports

The project documentation SHALL explain that generating a report file does not change audit exit codes: `0` indicates a clean audit, `1` indicates findings, and `2` indicates configuration or execution errors.

#### Scenario: Audit finds issues while report is saved
- **WHEN** audit output is redirected to a file and findings are detected
- **THEN** the report file is generated and the command exits with code `1`
