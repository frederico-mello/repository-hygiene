## ADDED Requirements

### Requirement: Provide distinct pre-commit and CI policies
The auditor MUST provide explicit `pre-commit` and `ci` execution modes with independent classification and failure policies.

#### Scenario: Pre-commit reports ambiguous findings
- **WHEN** the auditor runs in `pre-commit` mode and finds an ambiguous occurrence
- **THEN** it reports the occurrence with candidates, confidence, and reason without requiring it to fail by default

#### Scenario: CI does not fail on ambiguity
- **WHEN** the auditor runs in `ci` mode and finds an ambiguous or probable occurrence
- **THEN** the occurrence does not cause a failing exit status by default

#### Scenario: CI fails on confirmed missing reference
- **WHEN** CI mode finds a strong file reference with no valid repository resolution
- **THEN** the auditor reports it as confirmed missing and returns a failing status

### Requirement: Expose confidence and action in reports
Reports MUST expose the occurrence kind, confidence, resolution candidates, reason, and policy action when available.

#### Scenario: JSON preserves structured decision
- **WHEN** a classified occurrence is emitted as JSON
- **THEN** the output includes its classification and policy decision in addition to existing result fields
