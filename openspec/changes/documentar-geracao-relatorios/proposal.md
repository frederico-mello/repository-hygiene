## Why

The README shows how to run an audit and choose a format, but does not explain how to create the required configuration or save the generated report to a file. Users can successfully install the package and still be unsure how to produce a reusable audit artifact.

## What Changes

- Document the initialization step that creates `auditoria.yaml` before the first audit.
- Document commands for writing text, JSON, and SARIF audit output to files.
- Clarify that audit output is emitted on standard output and can be redirected by the shell.
- Document exit codes when reports are generated, including the non-zero status for findings.

## Capabilities

### New Capabilities

- `audit-report-documentation`: Explain the complete user workflow for configuring an audit and generating report files in supported formats.

### Modified Capabilities

- None. This change updates documentation only and does not alter audit behavior.

## Impact

- README usage documentation.
- OpenSpec planning artifacts for the documentation update.
- No production code, APIs, dependencies, or runtime behavior are changed.
