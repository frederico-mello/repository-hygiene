## ADDED Requirements

### Requirement: Detect OpenSpec before applying OpenSpec semantics
The auditor MUST apply OpenSpec-specific classification only when recognizable OpenSpec metadata or directory structure is present.

#### Scenario: OpenSpec repository is detected
- **WHEN** the repository contains OpenSpec structure or metadata
- **THEN** known OpenSpec properties, templates, and artifact paths use OpenSpec semantics

#### Scenario: Non-OpenSpec repository remains generic
- **WHEN** the repository does not contain OpenSpec markers
- **THEN** the auditor does not assume OpenSpec-specific path semantics

### Requirement: Treat archived OpenSpec content as historical
The auditor MUST treat OpenSpec archive content as historical by default and MUST NOT fail CI solely because an archived reference does not resolve in the current filesystem.

#### Scenario: Archived abbreviated path is historical
- **WHEN** archived content references `routes.py` while the current repository contains `app/routes.py`
- **THEN** the auditor records historical context or ignores the occurrence according to policy without a CI failure

#### Scenario: Current OpenSpec artifact remains auditable
- **WHEN** a non-archived OpenSpec artifact contains a confirmed missing current file reference
- **THEN** the active mode policy evaluates and reports it normally
