# English Source Locale

## Purpose

Enforce English as the source locale for all user-visible content, configuration identifiers, and documentation produced by the `repository-hygiene` package. Portuguese keys remain supported only as legacy input that is rejected at load time with a clear migration path to English.

## Requirements

### Requirement: Config load fails on Portuguese keys

When `repository-hygiene` loads an `auditoria.yaml` containing any top-level key whose identifier is a Portuguese word, the load SHALL fail with an error that names every offending key along with its English equivalent and points to `docs/MIGRATION.md`.

#### Scenario: Portuguese-only config rejected
- **GIVEN** an `auditoria.yaml` whose keys are Portuguese identifiers
- **WHEN** the user runs `repository-hygiene .`
- **THEN** the load raises a configuration error listing each Portuguese key with its English equivalent
- **AND** the error message references `docs/MIGRATION.md`

#### Scenario: Mixed Portuguese and English keys in same file
- **GIVEN** an `auditoria.yaml` that mixes Portuguese and English keys
- **WHEN** the user runs `repository-hygiene .`
- **THEN** the load raises a configuration error listing only the Portuguese keys
- **AND** no English key is consumed because the load fails atomically

#### Scenario: Portuguese key not in canonical mapping
- **GIVEN** an `auditoria.yaml` whose Portuguese identifier is not in the canonical Portuguese-to-English mapping
- **WHEN** the user runs `repository-hygiene .`
- **THEN** the load raises a configuration error naming the offending key
- **AND** the error directs the user to `docs/MIGRATION.md`

### Requirement: Unknown English config keys are rejected

When `auditoria.yaml` contains a key that is not in the set of valid English configuration keys, the load SHALL fail with a configuration error listing the unknown key. When the unknown key is close to a valid English key, the error SHALL suggest the closest match.

#### Scenario: Typo close to a valid English key
- **GIVEN** an `auditoria.yaml` containing `tracked_secres` (close to `tracked_secrets`)
- **WHEN** the user runs `repository-hygiene .`
- **THEN** the load raises a configuration error
- **AND** the error suggests `tracked_secrets` as the closest valid key

#### Scenario: Unknown key with no close match
- **GIVEN** an `auditoria.yaml` containing `xyzzy_foo` (no key within edit distance 2 of any valid English key)
- **WHEN** the user runs `repository-hygiene .`
- **THEN** the load raises a configuration error
- **AND** the error names `xyzzy_foo` as unknown
- **AND** the error references `docs/MIGRATION.md` for the canonical key list

### Requirement: Default config and workflow templates use English identifiers

The `auditoria.yaml` template and the workflow template bundled with `repository-hygiene install` SHALL use English keys and English job and step names.

#### Scenario: First-time install produces English config
- **GIVEN** a repository without an existing `auditoria.yaml`
- **WHEN** the user runs `repository-hygiene install .`
- **THEN** the generated `auditoria.yaml` contains English keys
- **AND** the generated `.github/workflows/repository-hygiene.yml` uses English job and step names

### Requirement: CLI help text, error messages, and text report are in English

The CLI's `argparse` help text, stderr error messages, and the text-form audit report (`--format text`) SHALL be in English. Structured output (JSON, SARIF) SHALL preserve its schema; only string values that reach the user become English.

#### Scenario: User runs `--help`
- **WHEN** the user runs `repository-hygiene --help`
- **THEN** the help text is in English

#### Scenario: User runs audit with findings in text format
- **WHEN** the audit produces findings and the user runs with `--format text`
- **THEN** the report text is in English

#### Scenario: JSON output preserves schema
- **WHEN** the user runs with `--format json`
- **THEN** the JSON document keys are unchanged from previous schema versions
- **AND** only message strings that were Portuguese become English

#### Scenario: SARIF output preserves schema
- **WHEN** the user runs with `--format sarif`
- **THEN** the SARIF document is schema-valid
- **AND** message strings that were Portuguese become English

### Requirement: Exception messages visible to the user are in English

Any exception message that becomes visible through the CLI's stderr, exit text, or audit report SHALL be in English. Exceptions raised only deep inside internal helpers, where the message text is consumed only by code and never reaches a user-visible surface, MAY remain in their source locale.

#### Scenario: Config load failure surfaces English message
- **WHEN** the user runs `repository-hygiene .` against a Portuguese-keyed config
- **THEN** the exception message shown on stderr is in English

#### Scenario: Internal helper exception does not surface to users
- **WHEN** an internal helper raises an exception whose message is in Portuguese
- **AND** no user-visible surface propagates that message
- **THEN** the user-facing CLI exit does not expose Portuguese text

### Requirement: README, docs, skill, and code docstrings are in English

`README.md`, `docs/`, the `agent-hygiene-flow` skill content, and Python docstrings under `src/` SHALL be in English.

#### Scenario: User opens README
- **WHEN** the user opens `README.md` at the repository root
- **THEN** the rendered text is in English

#### Scenario: User reads skill content
- **WHEN** the user installs the `agent-hygiene-flow` skill
- **THEN** the SKILL body is in English

### Requirement: Migration guide is the canonical Portuguese-to-English key table

`docs/MIGRATION.md` SHALL list every Portuguese key in the canonical mapping in a single table. The table SHALL be the single source of truth that consumers copy from.

#### Scenario: Consumer reads MIGRATION.md after load failure
- **WHEN** a consumer reads `docs/MIGRATION.md` after triggering a load-time failure
- **THEN** they find every Portuguese key from their config listed with its English equivalent

### Requirement: Drift guards keep mapping sources consistent

A CI step SHALL assert that every Portuguese-to-English mapping value is itself a valid English configuration key. A second CI step SHALL assert that the set of Portuguese keys listed in `docs/MIGRATION.md` exactly matches the set of keys in the canonical mapping. Both assertions SHALL run on every change.

#### Scenario: New Portuguese key added without English equivalent
- **GIVEN** a contributor adds a new Portuguese identifier to the canonical mapping
- **WHEN** they fail to assign an existing-or-new English identifier in the set of valid English configuration keys
- **THEN** the CI drift guard for mapping values fails
- **AND** the change cannot merge

#### Scenario: New Portuguese key added without MIGRATION.md row
- **GIVEN** a contributor adds a new Portuguese identifier to the canonical mapping
- **WHEN** they fail to add a matching row to `docs/MIGRATION.md`
- **THEN** the CI drift guard for the migration table fails
- **AND** the change cannot merge

#### Scenario: Adding a new English-only key with no Portuguese counterpart
- **GIVEN** a contributor adds a new English-only configuration key
- **WHEN** no Portuguese counterpart exists in the canonical mapping
- **THEN** no MIGRATION.md row is required
- **AND** the CI drift guards pass

### Requirement: Default shipped config uses only valid English keys

The bundled `auditoria.yaml` template SHALL contain only keys from the set of valid English configuration keys. A CI assertion enforces this.

#### Scenario: Template uses invalid English key
- **GIVEN** a contributor adds an English key to `templates/auditoria.yaml` that is not in the set of valid English configuration keys
- **WHEN** the change is opened
- **THEN** the CI assertion fails

### Requirement: Cross-repo consumer `quiz` config stays valid

The `frederico-mello/quiz` repository's `auditoria.yaml` SHALL use the English keys accepted by this capability. A coordinated update keeps `quiz` valid before or alongside the `1.0.0` release.

#### Scenario: `quiz` migrates from Portuguese to English config
- **GIVEN** `quiz` migrates from the Portuguese-keyed config to the English-keyed config and bumps its workflow pip pin to `1.0.0`
- **WHEN** the user runs `repository-hygiene` against `quiz` at the new release
- **THEN** the load succeeds and produces no load-time configuration error
