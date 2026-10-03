## ADDED Requirements

### Requirement: Staged validation command
The CLI MUST provide a dedicated pre-commit mode that validates the content staged in Git and does not inspect unstaged modifications as commit content.

#### Scenario: Clean staged snapshot
- **WHEN** the staged snapshot satisfies all enabled error-severity rules
- **THEN** the pre-commit command exits with code `0`
- **AND** the commit is allowed to continue

#### Scenario: Unstaged error is not part of the commit
- **WHEN** a file has a clean staged version and an invalid unstaged version
- **THEN** the pre-commit command evaluates the staged version
- **AND** it does not block the commit because of the unstaged version

#### Scenario: Staged error blocks commit
- **WHEN** the staged snapshot produces at least one enabled finding with severity `error`
- **THEN** the pre-commit command exits with code `1`
- **AND** the command reports the finding

### Requirement: Operational failure blocks commit
The pre-commit command MUST exit with code `2` and block the commit when configuration is missing or invalid, the repository cannot be evaluated, or temporary snapshot creation fails.

#### Scenario: Invalid configuration
- **WHEN** the configured audit file is missing or has an unsupported version
- **THEN** the pre-commit command exits with code `2`
- **AND** it prints an actionable error to standard error

#### Scenario: Snapshot failure
- **WHEN** the staged snapshot cannot be materialized or cleaned up safely
- **THEN** the pre-commit command exits with code `2`
- **AND** it does not allow the commit to proceed silently

### Requirement: Native hook installation
The initialization flow MUST support installing an executable native `pre-commit` hook in the target repository, without overwriting an existing hook unless force is explicitly requested.

#### Scenario: Install hook in repository without hook
- **WHEN** the user requests initialization with hook installation in a Git repository without `pre-commit`
- **THEN** the flow creates an executable `.git/hooks/pre-commit`
- **AND** the hook invokes the installed auditor pre-commit mode

#### Scenario: Preserve existing hook
- **WHEN** hook installation is requested and `.git/hooks/pre-commit` already exists without force
- **THEN** the existing hook remains unchanged
- **AND** the flow reports that installation was skipped

#### Scenario: Force replacement
- **WHEN** hook installation is requested with force
- **THEN** the generated hook replaces the existing native hook
- **AND** the resulting file is executable

### Requirement: Hook output and bypass documentation
The project documentation MUST describe hook installation, exit-code behavior, staged-only scope, warnings, and the explicit `git commit --no-verify` bypass.

#### Scenario: User consults installation instructions
- **WHEN** a user reads the initialization documentation
- **THEN** the documentation includes the command to install the hook
- **AND** explains when a commit is blocked

#### Scenario: User bypasses hook explicitly
- **WHEN** a user runs `git commit --no-verify`
- **THEN** Git bypasses the local hook
- **AND** the documentation warns that CI remains the independent validation path
