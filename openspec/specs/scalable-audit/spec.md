# Scalable Audit

## Purpose

Ensure the auditor performs efficiently on repositories of any size by scaling artifact checking with repository size, reusing file inventories, and falling back gracefully when Git is unavailable.

## Requirements

### Requirement: Artifact checks scale with repository size

The auditor SHALL identify files that are present in the working tree, are not tracked by Git, and are not covered by Git ignore rules without performing one Git process invocation per file.

#### Scenario: Large ignored directory
- **WHEN** an audited repository contains thousands of files under an ignored directory
- **THEN** artifact checking SHALL skip those files and use at most one repository-level Git inventory query for artifact candidates, regardless of file count

#### Scenario: Large mixed tree
- **WHEN** an audited repository contains thousands of ignored files and unignored untracked files
- **THEN** artifact checking SHALL report the unignored files and use a bounded number of Git inventory queries independent of the total file count

#### Scenario: Untracked file outside ignore rules
- **WHEN** an untracked file is not covered by the repository's ignore rules
- **THEN** the audit SHALL report it as an artifact outside `.gitignore` with its configured severity

#### Scenario: Tracked file
- **WHEN** a file is tracked by Git
- **THEN** the audit SHALL not report it as an artifact outside `.gitignore`

### Requirement: Audit inventory reuse

The auditor SHALL reuse repository file inventories during one audit execution rather than repeating equivalent Git queries for each rule, and SHALL isolate cached inventories between audit executions.

#### Scenario: Multiple rules need tracked files
- **WHEN** multiple enabled rules inspect tracked repository files
- **THEN** they SHALL use a shared inventory for that audit execution and preserve their existing findings

#### Scenario: Repeated audits of one root
- **WHEN** two audits run sequentially for the same root after the working tree changes
- **THEN** the second audit SHALL observe the new working-tree state rather than reusing stale inventory from the first audit

### Requirement: Compatibility and fallback

The auditor SHALL preserve existing exit codes, severities, report formats, and findings for supported repositories, and SHALL continue auditing a directory when Git is unavailable or the directory is not a Git repository.

#### Scenario: Non-Git directory
- **WHEN** the audited directory is not a Git repository
- **THEN** the audit SHALL complete using filesystem-based fallback behavior without an unhandled Git error

#### Scenario: Git command unavailable
- **WHEN** a Git inventory command fails during an audit
- **THEN** the audit SHALL use filesystem-based fallback behavior and return a normal audit result instead of propagating a subprocess exception

#### Scenario: JSON report after optimization
- **WHEN** the audit is requested with JSON output
- **THEN** stdout SHALL contain valid JSON with the same result structure and status semantics as before

#### Scenario: SARIF report after optimization
- **WHEN** the audit is requested with SARIF output
- **THEN** stdout SHALL contain valid SARIF with the same finding levels and status properties as before

#### Scenario: Existing exit statuses
- **WHEN** an audit is clean, finds an error, or rejects invalid configuration
- **THEN** it SHALL preserve exit codes `0`, `1`, and `2` respectively
