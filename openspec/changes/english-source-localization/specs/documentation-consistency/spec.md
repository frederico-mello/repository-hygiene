## MODIFIED Requirements

### Requirement: Documented onboarding flow

The README SHALL present `repository-hygiene --init .` (or `repository-hygiene install .` if that subcommand is canonical at release time) before running the audit as the recommended flow for a repository that is not yet configured, including a review of `auditoria.yaml` before the first audit. The README SHALL document that semantic reconciliation uses OpenSpec documents, OpenWiki documentation, and the knowledge graph when available to reduce false positives.

#### Scenario: New repository follows documented setup
- **WHEN** a user installs the package and follows the recommended flow in the README
- **THEN** they encounter installation, configuration review, and `repository-hygiene .` execution in that order

#### Scenario: User understands semantic reconciliation sources
- **WHEN** a user consults the README about how the audit classifies content
- **THEN** the README describes that OpenSpec documents, OpenWiki documentation, and the knowledge graph are used as semantic evidence when available

### Requirement: CLI documentation matches implementation

The README SHALL document only options and behaviors present in the current CLI, including the default report, explicit formats, `--output`, `--force`, `--install-hook`, and `--pre-commit` when applicable.

#### Scenario: User selects an explicit report format
- **WHEN** the user runs the CLI with `--format text`, `--format json`, or `--format sarif`
- **THEN** the README describes that the selected format is emitted on the terminal and can be saved with `--output`

### Requirement: Generated workflow handles audit failures

The workflow template SHALL preserve the audit exit code, publish the report even when the audit returns code 1 or 2, and execute issue management per the documented conditions.

#### Scenario: Audit finds errors in generated workflow
- **WHEN** the generated workflow runs an audit that returns code 1
- **THEN** the audit step records `exit_code=1`, the summary step publishes the report, and the issue step can create or update the issue outside pull requests

#### Scenario: Audit fails due to configuration or execution
- **WHEN** the generated workflow runs an audit that returns code 2
- **THEN** the report is still published and the code 2 remains available for downstream workflow conditions

### Requirement: Configuration examples match template

The `auditoria.yaml` example in the README SHALL include or explain the configuration options supported by the official template when those options change rule behavior, including artifact patterns and permitted write permissions. The example SHALL use English keys, including the canonical English key for permitted write permissions inside `insecure_workflows`.

#### Scenario: User configures workflow permission exception
- **GIVEN** the README contains a configuration example
- **WHEN** the user consults the example to permit a required write permission
- **THEN** the example uses `permitted_write_permissions` inside `insecure_workflows` (or its canonical English equivalent)
- **AND** the example explicitly references the canonical English key name

### Requirement: Documentation verification includes planning documents and knowledge graph

The auditor SHALL verify documentation consistency against OpenSpec documents in `openspec/specs/` and `openspec/changes/`, OpenWiki documentation when available, and knowledge graph nodes when a graph is present. References to files, directories, or commands described in documentation SHALL be checked against the repository structure.

#### Scenario: OpenSpec spec references a missing file
- **WHEN** an OpenSpec spec describes a file that does not exist in the repository
- **THEN** the auditor SHALL report a documentation inconsistency
- **AND** the auditor SHALL include the source document path and the expected file path

#### Scenario: OpenWiki entry is consistent with repository structure
- **WHEN** an OpenWiki entry references files and directories that exist in the repository
- **THEN** the auditor SHALL NOT report a documentation inconsistency
- **AND** the auditor SHALL confirm consistency in the audit trail

#### Scenario: Knowledge graph node references missing symbols
- **WHEN** the knowledge graph contains a node for a symbol that is not present in the current repository state
- **THEN** the auditor SHALL report stale knowledge
- **AND** the auditor SHALL recommend regenerating the knowledge graph

## ADDED Requirements

### Requirement: Documentation and config examples use English identifiers

Documentation surfaces (`README.md`, `docs/`) and config examples SHALL use English identifiers for any rule names, configuration keys, CLI flag names, or workflow step names referenced in the text. Idiomatic prose SHALL also be English.

#### Scenario: README references an English config key
- **WHEN** the user reads the README and finds an `auditoria.yaml` example or rule discussion
- **THEN** every key name, rule identifier, and CLI flag in that prose is English

#### Scenario: README mentions an English exception class name
- **WHEN** the README references an exception class from `auditoria_higiene.core`
- **THEN** the reference uses the English class name, not a translated or descriptive paraphrase

#### Scenario: README contains an English link to MIGRATION.md
- **WHEN** the README references schema migration guidance
- **THEN** the link points to `docs/MIGRATION.md`
- **AND** the link text is in English
