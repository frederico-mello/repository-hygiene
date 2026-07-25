# Conventional Commit Audit

## ADDED Requirements

### Requirement: Audit rule validates Conventional Commits format
The system SHALL provide an audit rule `conventional-commits` that validates all commit messages in the repository against the Conventional Commits specification. The rule SHALL be enabled by default (opt-out).

#### Scenario: Commit message follows conventional format
- **GIVEN** a repository with commit `feat(auth): add OAuth2 support`
- **WHEN** the `conventional-commits` audit rule executes
- **THEN** no findings SHALL be reported for that commit

#### Scenario: Commit message lacks conventional format
- **GIVEN** a repository with commit `added OAuth2 support`
- **WHEN** the `conventional-commits` audit rule executes
- **THEN** a finding SHALL be reported with level `warning`
- **AND** the finding SHALL include the commit hash
- **AND** the finding SHALL include a message describing the violation

### Requirement: Rule respects enabled configuration
The system SHALL respect the `enabled` and `level` configuration fields for the `conventional-commits` rule.

#### Scenario: Rule disabled in configuration
- **GIVEN** the `conventional-commits` rule is set to `enabled: false` in `auditoria.yaml`
- **WHEN** the audit executes
- **THEN** no commit validation SHALL be performed
- **AND** no findings SHALL be reported for commits

#### Scenario: Rule level configured as error
- **GIVEN** the `conventional-commits` rule is set to `level: error` in `auditoria.yaml`
- **GIVEN** a repository with a non-conventional commit
- **WHEN** the audit rule executes
- **THEN** the finding SHALL have level `error`

### Requirement: Supported commit types
The system SHALL accept the following commit types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`. Messages starting with any other type SHALL be flagged as violations.

#### Scenario: Valid commit type accepted
- **GIVEN** a repository with commit `docs: update README`
- **WHEN** the `conventional-commits` audit rule executes
- **THEN** no findings SHALL be reported for that commit

#### Scenario: Invalid commit type flagged
- **GIVEN** a repository with commit `wip: partial work`
- **WHEN** the `conventional-commits` audit rule executes
- **THEN** a finding SHALL be reported for that commit

### Requirement: Scope and breaking change syntax supported
The system SHALL accept optional scope in parentheses and breaking change indicator (`!`) in commit messages.

#### Scenario: Commit with scope
- **GIVEN** a repository with commit `feat(api): add rate limiting`
- **WHEN** the `conventional-commits` audit rule executes
- **THEN** no findings SHALL be reported for that commit

#### Scenario: Commit with breaking change indicator
- **GIVEN** a repository with commit `feat!: drop Python 3.8 support`
- **WHEN** the `conventional-commits` audit rule executes
- **THEN** no findings SHALL be reported for that commit

#### Scenario: Malformed scope syntax flagged
- **GIVEN** a repository with commit `feat(auth: add login` (unbalanced parentheses)
- **WHEN** the `conventional-commits` audit rule executes
- **THEN** a finding SHALL be reported for that commit

### Requirement: Merge commits are ignored
The system SHALL NOT validate merge commits, preventing false positives from GitHub/GitLab auto-generated merge messages.

#### Scenario: Merge commit skipped
- **GIVEN** a repository with a merge commit `Merge pull request #42 from ...`
- **WHEN** the `conventional-commits` audit rule executes
- **THEN** no findings SHALL be reported for that merge commit

### Requirement: Empty repository handled gracefully
The system SHALL return zero findings when the repository has no commits, without error.

#### Scenario: Repository with no commits
- **GIVEN** a git repository with no commits
- **WHEN** the `conventional-commits` audit rule executes
- **THEN** the rule SHALL complete successfully
- **AND** zero findings SHALL be returned

### Requirement: Missing git handled gracefully
The system SHALL report a system error when `git` is not available in the execution environment, rather than crashing.

#### Scenario: Git not installed
- **GIVEN** `git` is not in the system PATH
- **WHEN** the `conventional-commits` audit rule attempts to execute
- **THEN** the audit SHALL report a system error
- **AND** the audit SHALL NOT crash or exit abnormally

### Requirement: Hook pre-commit installed by init
The `--init` command SHALL install a `commit-msg` hook that validates the commit message format before committing. The hook SHALL block commits whose message does not conform to Conventional Commits.

#### Scenario: Hook blocks non-conventional commit
- **GIVEN** `repository-hygiene --init .` has been executed
- **AND** the user attempts `git commit -m "added something"`
- **WHEN** the `commit-msg` hook executes
- **THEN** the commit SHALL be blocked
- **AND** an error message SHALL be displayed with the expected format

#### Scenario: Hook allows conventional commit
- **GIVEN** `repository-hygiene --init .` has been executed
- **AND** the user attempts `git commit -m "feat: add something"`
- **WHEN** the `commit-msg` hook executes
- **THEN** the commit SHALL proceed without error

### Requirement: Hook respects existing hooks
The system SHALL NOT overwrite an existing `.git/hooks/commit-msg` file. The system SHALL display a warning and skip installation. The `--force` flag SHALL override this behavior and overwrite the existing hook.

#### Scenario: Existing hook preserved
- **GIVEN** `.git/hooks/commit-msg` already exists
- **WHEN** `repository-hygiene --init .` executes
- **THEN** a warning SHALL be displayed about the existing hook
- **AND** the existing hook SHALL NOT be overwritten

#### Scenario: Force overwrites existing hook
- **GIVEN** `.git/hooks/commit-msg` already exists
- **WHEN** `repository-hygiene --init . --force` executes
- **THEN** the existing hook SHALL be overwritten with the new hook

### Requirement: AGENTS.md documents Conventional Commits standard
The project's `AGENTS.md` SHALL document Conventional Commits as the required commit message format for all contributors.

#### Scenario: AGENTS.md contains commit standard
- **WHEN** a contributor reads `AGENTS.md`
- **THEN** the document SHALL specify that commits MUST follow Conventional Commits
- **AND** the document SHALL list the accepted commit types
