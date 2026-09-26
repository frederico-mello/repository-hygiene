## ADDED Requirements

### Requirement: Support optional user-selected LLM triage
The auditor MUST allow users to configure an LLM provider for ambiguous pre-commit occurrences and MUST operate without an LLM.

#### Scenario: Local LLM classifies ambiguity
- **WHEN** pre-commit mode has an enabled local provider and an ambiguous occurrence
- **THEN** the auditor sends minimized context for classification and records the provider-assisted result

#### Scenario: LLM is disabled in CI
- **WHEN** CI mode is configured with LLM disabled
- **THEN** no LLM request is made and classification remains deterministic

#### Scenario: LLM failure does not create a false failure
- **WHEN** the configured LLM is unavailable or returns an invalid classification
- **THEN** the occurrence remains ambiguous and is handled by the active policy

### Requirement: Minimize and disclose LLM data
The auditor MUST redact recognized secrets, limit context sent to the provider, and disclose the configured provider when LLM triage is active.

#### Scenario: Secret is redacted before request
- **WHEN** the context contains a recognized credential pattern
- **THEN** the provider request contains a redacted value

#### Scenario: User can opt out
- **WHEN** the user disables LLM triage
- **THEN** the auditor performs no provider request and runs deterministically
