# Agent-Friendly Audit Report

## Purpose

Define the behavior of the auditor's default output mode, explicit format selection, JSON report persistence, and agent integration guidance. The auditor SHALL produce concise terminal summaries by default, write sanitized JSON reports to a well-known path, support explicit formats (text, JSON, SARIF), and document how agents should consume the report.

## Requirements

### Requirement: Default audit produces agent report and human summary

The auditor SHALL, when run without an explicit report format in normal audit mode, display a concise terminal summary and write a sanitized JSON report to `.repository-hygiene/auditoria.json` relative to the audited directory.

#### Scenario: Clean default audit
- **GIVEN** an auditable directory has no findings with severity `error`
- **WHEN** the user runs the audit without `--format`
- **THEN** the terminal SHALL display audit status, error count, warning count, and report path
- **AND** `.repository-hygiene/auditoria.json` SHALL contain the current audit result

#### Scenario: Default audit with errors
- **GIVEN** an auditable directory has one or more findings with severity `error`
- **WHEN** the user runs the audit without `--format`
- **THEN** the terminal SHALL display a failed status and the counts of errors and warnings
- **AND** the JSON report SHALL contain the findings from that execution

#### Scenario: Previous report is replaced
- **GIVEN** `.repository-hygiene/auditoria.json` contains a result from an earlier audit
- **WHEN** the user runs a new default audit
- **THEN** the report SHALL represent only the new execution
- **AND** findings from the earlier execution SHALL not remain in the report

### Requirement: Explicit formats remain available

The auditor SHALL preserve complete terminal reports for explicit `--format text`, `--format json`, and `--format sarif` requests, and SHALL write the selected format when `--output` is supplied with an explicit format.

#### Scenario: Explicit text format
- **WHEN** the user runs the audit with `--format text`
- **THEN** stdout SHALL contain the complete text report rather than only the concise summary

#### Scenario: Explicit JSON format
- **WHEN** the user runs the audit with `--format json`
- **THEN** stdout SHALL contain valid JSON with the audit result structure and status semantics

#### Scenario: Explicit SARIF format
- **WHEN** the user runs the audit with `--format sarif`
- **THEN** stdout SHALL contain valid SARIF with the audit findings and status properties

#### Scenario: Explicit format written to custom path
- **GIVEN** the parent directory of the requested output path exists
- **WHEN** the user runs the audit with an explicit format and `--output <path>`
- **THEN** stdout SHALL contain the complete selected report
- **AND** `<path>` SHALL contain the same selected format
- **AND** it SHALL return exit code `0` for a clean audit or `1` when the audit has error findings

#### Scenario: Explicit format cannot be written
- **WHEN** the user runs the audit with an explicit format and an unusable `--output <path>`
- **THEN** the command SHALL report a persistence error on stderr
- **AND** it SHALL return exit code `2`

### Requirement: Custom output path supports agent JSON

The auditor SHALL accept `--output <path>` without `--format`, write JSON to the requested path, and continue displaying the concise summary in normal audit mode.

#### Scenario: Custom JSON output
- **GIVEN** the parent directory of the requested output path exists
- **WHEN** the user runs the audit with `--output report.json`
- **THEN** `report.json` SHALL contain valid sanitized JSON for the current audit
- **AND** the terminal SHALL display the concise summary

#### Scenario: Missing custom output parent
- **GIVEN** the parent directory of a custom output path does not exist
- **WHEN** the user runs the audit with `--output <path>`
- **THEN** the command SHALL report a persistence error on stderr
- **AND** it SHALL return exit code `2`

#### Scenario: Invalid or unwritable custom output
- **WHEN** the requested custom output path cannot be validated or written
- **THEN** the command SHALL report a persistence error on stderr
- **AND** it SHALL return exit code `2`

### Requirement: JSON report is versioned and sanitized

The persisted JSON report SHALL include a numeric `schema_version`, auditor version, UTC execution timestamp, normalized audited directory, and the sanitized current audit result. It SHALL not persist the raw audit result.

#### Scenario: Stable report metadata
- **WHEN** a JSON report is generated
- **THEN** it SHALL include `schema_version`, auditor version, UTC timestamp, audited directory, status, findings, and disabled rules
- **AND** the schema version SHALL be numeric

#### Scenario: Sensitive finding content
- **GIVEN** an audit finding contains a value recognized as sensitive content
- **WHEN** a JSON report is generated
- **THEN** the sensitive value SHALL be masked according to the auditor sanitization policy
- **AND** the raw audit result SHALL not be written to disk

### Requirement: Report persistence does not corrupt results or exit semantics

The auditor SHALL persist reports without leaving a truncated output file and SHALL preserve audit exit semantics when persistence succeeds. Missing output parents, invalid output paths, and write failures SHALL all use exit code `2` as execution errors.

#### Scenario: Successful persistence after clean audit
- **WHEN** a clean audit writes its report successfully
- **THEN** the command SHALL return exit code `0`

#### Scenario: Successful persistence after findings
- **GIVEN** an audit has findings with severity `error`
- **WHEN** its report writes successfully
- **THEN** the command SHALL return exit code `1`

#### Scenario: Interrupted or failed write
- **WHEN** report persistence fails before a complete report is available
- **THEN** the command SHALL return exit code `2`
- **AND** it SHALL not present the report as successfully generated

### Requirement: Pre-commit mode does not create an implicit report

The auditor SHALL not create `.repository-hygiene/auditoria.json` implicitly during `--pre-commit`, and SHALL preserve existing hook output behavior unless explicit output options are supplied.

#### Scenario: Default pre-commit audit
- **WHEN** the user runs the auditor with `--pre-commit` and no output option
- **THEN** the command SHALL not write the default JSON report into the temporary snapshot or audited repository
- **AND** the hook SHALL preserve its existing audit decision and exit semantics

#### Scenario: Explicit pre-commit output
- **GIVEN** the parent directory of the requested output path exists
- **WHEN** the user runs `--pre-commit --output <path>`
- **THEN** the command SHALL write a JSON report unless an explicit format is selected
- **AND** persistence errors SHALL return exit code `2`

### Requirement: Agent integration guidance is documented and optional

The project documentation SHALL provide an optional `AGENTS.md` instruction that tells agents to read the JSON report, prioritize `error` findings, avoid exposing sensitive values, and rerun the audit after corrections. The auditor SHALL not create or modify `AGENTS.md` automatically.

#### Scenario: Documentation provides agent guidance
- **WHEN** a user reads the report integration documentation
- **THEN** the documentation SHALL include a reusable `AGENTS.md` instruction block
- **AND** the block SHALL identify `.repository-hygiene/auditoria.json` as the complete audit source

#### Scenario: Existing agent instructions remain untouched
- **GIVEN** a project already has an `AGENTS.md` file
- **WHEN** the auditor runs or is initialized
- **THEN** the auditor SHALL not overwrite or modify that file

### Requirement: Default report directory is not reported as an unexpected artifact

The auditor SHALL treat its default `.repository-hygiene/` directory as generated local output for artifact detection, while leaving custom output paths subject to the audited repository's normal ignore rules.

#### Scenario: Default report on later audit
- **GIVEN** a previous audit generated `.repository-hygiene/auditoria.json`
- **WHEN** a later audit checks for artifacts outside ignore rules
- **THEN** the default report directory SHALL not be reported as an unexpected artifact

#### Scenario: Custom report remains consumer-controlled
- **GIVEN** a user writes a report to a custom path outside the default directory
- **WHEN** artifact detection evaluates that path
- **THEN** the path SHALL follow the repository's normal ignore rules
