# Markdown Audit Report

## Purpose

Formato determinístico de relatório de auditoria em Markdown, para leitura humana e por agentes: título, status, contagens de erro/aviso, achados agrupados por severidade e detalhes acionáveis por achado. Capabilidade movida do workspace stray (criada em 2026-07-22).

## Requirements

### Requirement: Markdown audit reports

The system SHALL support a deterministic Markdown audit report format containing a title, audit status, error and warning counts, findings grouped by severity, disabled rules when present, and actionable details for each finding.

#### Scenario: Render a failed audit as Markdown

- **WHEN** the audit has at least one error and the user selects the Markdown format
- **THEN** the output contains a Markdown heading identifying the audit report
- **AND** the output contains the failed status and error and warning counts
- **AND** the output contains separate severity sections in a stable order
- **AND** each finding contains its rule, path, message, evidence, and recommendation when available

#### Scenario: Render a clean audit as Markdown

- **WHEN** the audit has no errors or warnings and the user selects the Markdown format
- **THEN** the output contains the successful status
- **AND** the output contains zero error and warning counts
- **AND** the output does not invent findings

#### Scenario: Render warnings without errors as Markdown

- **WHEN** the audit has warnings but no errors and the user selects the Markdown format
- **THEN** the output contains the successful status
- **AND** the output contains the warning count and warning findings
- **AND** the output contains zero errors

#### Scenario: Render disabled rules as Markdown

- **WHEN** one or more audit rules are disabled
- **THEN** the Markdown output identifies the disabled rules separately from findings

### Requirement: Optional report file output

The system SHALL accept an output path and write the selected sanitized report to that path using UTF-8 encoding, overwriting an existing regular file.

#### Scenario: Save a Markdown report

- **WHEN** the user selects Markdown and provides a writable output path
- **THEN** the system writes the Markdown report to that path
- **AND** the command writes the file as UTF-8
- **AND** stdout contains a confirmation naming the output path

#### Scenario: Save an existing report format

- **WHEN** the user selects text, JSON, or SARIF and provides a writable output path
- **THEN** the system writes the corresponding existing format to that path
- **AND** the format content remains compatible with output produced without a file path

#### Scenario: Overwrite an existing report file

- **WHEN** the requested output path identifies an existing regular file
- **THEN** the system replaces its contents with the new report

#### Scenario: Do not create missing parent directories

- **WHEN** the requested output path has a parent directory that does not exist
- **THEN** the command reports the write failure on stderr
- **AND** the command returns exit code `2`

#### Scenario: Preserve terminal output by default

- **WHEN** the user does not provide an output path
- **THEN** the selected report is printed to the terminal as before

#### Scenario: Report an audit failure separately from an output failure

- **WHEN** the audit finds errors and the report is successfully generated
- **THEN** the command returns exit code `1`
- **BUT** an output-path failure returns exit code `2` regardless of audit findings

#### Scenario: Reject an unwritable output path

- **WHEN** the requested output path cannot be opened or written
- **THEN** the command reports the failure on stderr
- **AND** the command returns exit code `2`
- **AND** the command does not claim that the report was successfully saved

### Requirement: Sensitive data protection in saved reports

The system SHALL apply the same result sanitization to reports saved in files as to reports printed to the terminal.

#### Scenario: Mask a detected secret in a saved report

- **WHEN** an audit finding contains a detected secret and the user saves the report
- **THEN** the saved report contains the sanitized finding
- **AND** the original secret value is absent from the saved report
