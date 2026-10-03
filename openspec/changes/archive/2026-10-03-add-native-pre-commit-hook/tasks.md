## 1. Staged Snapshot

- [x] 1.1 Implement materialization of the Git index into an isolated temporary audit directory, preserving repository-relative paths and required Git metadata.
- [x] 1.2 Define cleanup and error handling for snapshot creation, evaluation, and removal, including exit code `2` on operational failure.
- [x] 1.3 Add tests covering clean staged content, staged errors, unstaged invalid changes, added files, modified files, and removed files.

## 2. CLI Integration

- [x] 2.1 Add the dedicated pre-commit CLI mode and route it through the existing configuration, auditor, sanitizer, reporter, and exit-code contract.
- [x] 2.2 Ensure warnings are displayed but do not block, while error findings and invalid execution block the commit.
- [x] 2.3 Add CLI tests for exit codes `0`, `1`, and `2`, including missing/invalid configuration.

## 3. Native Hook Installation

- [x] 3.1 Add an executable hook template that invokes the installed auditor in pre-commit mode and propagates its exit code.
- [x] 3.2 Extend initialization with explicit hook installation, repository validation, idempotent behavior, and force-protected replacement.
- [x] 3.3 Add tests for installation, executable permissions, existing-hook preservation, and forced replacement.

## 4. Documentation and Verification

- [x] 4.1 Document hook installation, staged-only scope, blocking behavior, warnings, operational failures, and `git commit --no-verify`.
- [x] 4.2 Document that GitHub Actions remains the independent full-repository audit.
- [x] 4.3 Run the complete test suite and validate the OpenSpec change artifacts before implementation is considered complete.
