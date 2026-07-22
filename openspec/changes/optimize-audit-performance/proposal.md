## Why

Audits can appear to hang when a repository contains generated directories or large dependency trees because artifact checking processes files one at a time. The audit should remain responsive and complete predictably on ordinary repositories, including repositories with local tooling output.

## What Changes

- Make artifact detection scale with repository size instead of spawning one Git process per file.
- Reuse repository file inventory across rules during a single audit.
- Ensure generated local tooling output, specifically `.opencode/node_modules/` and `graphify-out/`, is excluded from routine repository scans through `.gitignore`.
- Add regression coverage for large untracked trees, ignored directories, and non-Git directories.
- Preserve existing findings, severities, exit codes, and report formats.

## Capabilities

### New Capabilities

- `scalable-audit`: Audits complete predictably as repository file counts grow, without changing finding semantics.

### Modified Capabilities

- None. This change optimizes existing behavior without changing its public requirements.

## Impact

- Affected audit traversal and Git-integration logic in the core auditor.
- Affected repository ignore configuration for `.opencode/node_modules/` and `graphify-out/`.
- Affected unit and integration tests for artifact detection and audit execution time.
- No new runtime dependency, CLI flag, report schema, or external service.
